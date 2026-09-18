from __future__ import annotations

import argparse
import json
import random
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

import audit_holdout_schema as schema


def era_of(year: int) -> str:
  if year <= 2009:
    return "2004-2009"
  if year <= 2014:
    return "2010-2014"
  if year <= 2019:
    return "2015-2019"
  return "2020-2025"


def normalize_relative(entry: dict[str, Any]) -> str:
  return str(entry.get("relativePath") or entry.get("path") or "").replace("\\", "/").lower()


def document_id_for_content(content_fingerprint: str) -> str:
  return "doc-" + content_fingerprint[:12]


def _rand_key(seed: int, value: str) -> str:
  return schema.sha256_text(f"{seed}|{value}")


def _is_development_path(entry: dict[str, Any], development: list[str]) -> bool:
  name = Path(str(entry.get("relativePath") or entry.get("path") or "")).name.lower()
  return any(dev.lower() in name for dev in development)


def _resolve_content_fingerprint(entry: dict[str, Any], content_hashes: dict[str, str] | None,
                                 fingerprint_cache: dict[str, Any] | None) -> str | None:
  if content_hashes is not None:
    return content_hashes.get(normalize_relative(entry)) or content_hashes.get(str(entry.get("relativePath") or ""))
  path = entry.get("path") or entry.get("relativePath")
  if not path:
    return None
  if fingerprint_cache is not None:
    return schema.fingerprint_with_cache(path, fingerprint_cache)
  try:
    return schema.content_fingerprint_file(path)
  except OSError:
    return None


def build_candidate_pool(inventory: dict[str, Any], protocol: dict[str, Any],
                         content_hashes: dict[str, str] | None = None,
                         dev_fingerprints: set[str] | None = None,
                         fingerprint_cache: dict[str, Any] | None = None) -> dict[str, Any]:
  pdfs = inventory.get("pdfs")
  if not isinstance(pdfs, list):
    raise schema.HoldoutValidationError("inventory: pdfs missing")
  development = protocol.get("developmentDocuments") or []
  by_content: dict[str, dict[str, Any]] = {}
  excluded_development = 0
  excluded_invalid = 0
  excluded_inaccessible = 0
  duplicates = 0
  for index, entry in enumerate(pdfs):
    try:
      schema.validate_candidate_entry(entry, index)
    except schema.HoldoutValidationError:
      excluded_invalid += 1
      continue
    if _is_development_path(entry, development):
      excluded_development += 1
      continue
    content_fingerprint = _resolve_content_fingerprint(entry, content_hashes, fingerprint_cache)
    if not content_fingerprint:
      excluded_inaccessible += 1
      continue
    if dev_fingerprints and content_fingerprint in dev_fingerprints:
      excluded_development += 1
      continue
    relative = str(entry.get("relativePath") or "")
    canonical_path = str(entry.get("path") or relative)
    year = int(entry["year"])
    candidate = {
      "documentId": document_id_for_content(content_fingerprint),
      "canonicalPath": canonical_path,
      "relativePath": relative,
      "normalizedRelativePath": normalize_relative(entry),
      "contentFingerprint": content_fingerprint,
      "duplicatePaths": [],
      "duplicateCount": 0,
      "family": str(entry["institution"]),
      "year": year,
      "era": era_of(year),
      "series": entry.get("series"),
      "sourceType": str(entry["classification"]),
      "pageCount": int(entry["pageCount"]),
    }
    existing = by_content.get(content_fingerprint)
    if existing is None:
      by_content[content_fingerprint] = candidate
      continue
    # same content: keep the lexicographically smallest normalizedRelativePath as canonical
    duplicates += 1
    existing["duplicatePaths"].append(relative)
    existing["duplicateCount"] = existing.get("duplicateCount", 0) + 1
    if candidate["normalizedRelativePath"] < existing["normalizedRelativePath"]:
      candidate["duplicatePaths"] = existing["duplicatePaths"] + [existing["relativePath"]]
      candidate["duplicateCount"] = existing["duplicateCount"]
      by_content[content_fingerprint] = candidate
  pool = list(by_content.values())
  return {
    "pool": pool,
    "stats": {
      "totalPdfs": len(pdfs),
      "poolSize": len(pool),
      "excludedDevelopment": excluded_development,
      "excludedDuplicateFingerprint": duplicates,
      "excludedInvalid": excluded_invalid,
      "excludedInaccessible": excluded_inaccessible,
      "bySource": dict(Counter(document["sourceType"] for document in pool)),
      "byFamily": dict(Counter(document["family"] for document in pool)),
    },
  }


def _improve_era_coverage(selected: list[dict[str, Any]], pool: list[dict[str, Any]], config: dict[str, Any], seed: int) -> None:
  eras = list(config.get("eras") or [])
  family_cap = int(config.get("maxDocumentsPerFamily", 4))
  selected_fingerprints = {document["contentFingerprint"] for document in selected}
  for missing in eras:
    era_counts = Counter(document["era"] for document in selected)
    if era_counts.get(missing, 0) > 0:
      continue
    candidates = [document for document in pool if document["era"] == missing and document["contentFingerprint"] not in selected_fingerprints]
    candidates.sort(key=lambda document: _rand_key(seed, "era|" + document["documentId"]))
    swapped = False
    for candidate in candidates:
      victims = [document for document in selected if document["sourceType"] == candidate["sourceType"]]
      victims.sort(key=lambda document: (-era_counts.get(document["era"], 0), _rand_key(seed, "victim|" + document["documentId"])))
      for victim in victims:
        families = Counter(document["family"] for document in selected if document is not victim)
        families[candidate["family"]] = families.get(candidate["family"], 0) + 1
        if max(families.values(), default=0) > family_cap:
          continue
        selected.remove(victim)
        selected.append(candidate)
        selected_fingerprints.discard(victim["contentFingerprint"])
        selected_fingerprints.add(candidate["contentFingerprint"])
        swapped = True
        break
      if swapped:
        break


def select_documents(pool: list[dict[str, Any]], config: dict[str, Any], seed: int) -> dict[str, Any]:
  quotas = {key: int(value) for key, value in (config.get("sourceQuota") or {}).items()}
  family_cap = int(config.get("maxDocumentsPerFamily", 4))
  target = int(config.get("targetDocuments", 48))
  min_families = int(config.get("minFamilies", 10))
  min_years = int(config.get("minDistinctYears", 10))
  eras = list(config.get("eras") or [])

  selected: list[dict[str, Any]] = []
  selected_fp: set[str] = set()
  family_counts: Counter[str] = Counter()
  unsatisfied: list[dict[str, Any]] = []

  for source, quota in quotas.items():
    candidates = [document for document in pool if document["sourceType"] == source]
    candidates.sort(key=lambda document: _rand_key(seed, document["documentId"]))
    picked = 0
    for document in candidates:
      if picked >= quota:
        break
      if family_counts[document["family"]] >= family_cap:
        continue
      if document["contentFingerprint"] in selected_fp:
        continue
      selected.append(document)
      selected_fp.add(document["contentFingerprint"])
      family_counts[document["family"]] += 1
      picked += 1
    if picked < quota:
      unsatisfied.append({
        "constraint": "sourceQuota",
        "sourceType": source,
        "quota": quota,
        "selected": picked,
        "available": len(candidates),
        "reason": "availability_or_family_cap",
      })

  _improve_era_coverage(selected, pool, config, seed)
  family_counts = Counter(document["family"] for document in selected)

  if len(selected) < target:
    unsatisfied.append({"constraint": "targetDocuments", "target": target, "selected": len(selected)})
  if len(family_counts) < min_families:
    unsatisfied.append({"constraint": "minFamilies", "min": min_families, "actual": len(family_counts)})
  distinct_years = sorted({document["year"] for document in selected})
  if len(distinct_years) < min_years:
    unsatisfied.append({"constraint": "minDistinctYears", "min": min_years, "actual": len(distinct_years)})
  covered_eras = sorted({document["era"] for document in selected})
  missing_eras = [era for era in eras if era not in covered_eras]
  if missing_eras:
    unsatisfied.append({"constraint": "eraCoverage", "missing": missing_eras})

  reserved = [document for document in pool if document["contentFingerprint"] not in selected_fp]
  reserved_fingerprints = sorted(document["contentFingerprint"] for document in reserved)
  return {
    "status": "selection_constraints_unsatisfied" if unsatisfied else "ok",
    "selectionSeed": seed,
    "documents": sorted(selected, key=lambda document: document["documentId"]),
    "unsatisfied": unsatisfied,
    "reservedPoolHash": schema.reserved_pool_hash(reserved_fingerprints),
    "reservedCount": len(reserved),
    "stats": {
      "selectedCount": len(selected),
      "families": dict(family_counts),
      "distinctYears": distinct_years,
      "coveredEras": covered_eras,
      "bySource": dict(Counter(document["sourceType"] for document in selected)),
    },
  }


def select_questions(questions: list[dict[str, Any]], seed: int, document_id_value: str, count: int = 3) -> list[dict[str, Any]]:
  if not questions:
    return []
  if len(questions) <= count:
    return list(questions)
  size = len(questions)
  boundaries = [0, size // 3, (2 * size) // 3, size]
  picked: list[dict[str, Any]] = []
  for tertile in range(3):
    window = questions[boundaries[tertile]:boundaries[tertile + 1]]
    if not window:
      continue
    rng = random.Random(int(schema.sha256_text(f"{seed}|{document_id_value}|{tertile}")[:12], 16))
    picked.append(window[rng.randrange(len(window))])
  return picked[:count]


def code_identity() -> dict[str, Any]:
  try:
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=10).stdout.strip() or None
    status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, timeout=10).stdout.strip()
    return {"gitCommit": commit, "selectionCodeState": "dirty" if status else "clean"}
  except Exception:
    return {"gitCommit": None, "selectionCodeState": "unknown"}


def build_manifest(protocol: dict[str, Any], provenance: dict[str, Any], selection: dict[str, Any],
                   question_index: dict[str, Any] | None = None, seed: int | None = None) -> dict[str, Any]:
  documents = []
  index_by_document = {}
  if question_index:
    index_by_document = {document["documentId"]: document for document in question_index.get("documents", [])}
  effective_seed = seed if seed is not None else int(selection["selectionSeed"])
  for document in selection["documents"]:
    entry = {
      "documentId": document["documentId"],
      "canonicalPath": document["canonicalPath"],
      "contentFingerprint": document["contentFingerprint"],
      "duplicatePaths": document.get("duplicatePaths") or [],
      "family": document["family"],
      "year": document["year"],
      "series": document["series"],
      "sourceType": document["sourceType"],
      "selectedQuestions": [],
    }
    index_document = index_by_document.get(document["documentId"])
    if index_document:
      entry["selectedQuestions"] = select_questions(
        index_document["questions"], effective_seed, document["documentId"],
        int(protocol["randomHoldout"]["questionsPerDocument"]),
      )
    documents.append(entry)
  return {
    "protocolVersion": protocol["protocolVersion"],
    "selectorVersion": schema.SELECTOR_VERSION,
    "selectionSeed": effective_seed,
    "protocolSha256": provenance.get("protocolSha256"),
    "inventorySha256": provenance.get("inventorySha256"),
    "candidatePoolHash": provenance.get("candidatePoolHash"),
    "candidatePoolPathHash": provenance.get("candidatePoolPathHash"),
    "gitCommit": provenance.get("gitCommit"),
    "selectionCodeState": provenance.get("selectionCodeState"),
    "selectorSha256": provenance.get("selectorSha256"),
    "selectionConfig": protocol["randomHoldout"],
    "reservedPoolHash": selection.get("reservedPoolHash"),
    "reservedCount": selection.get("reservedCount"),
    "documents": documents,
  }


def _load(path: str | Path) -> Any:
  return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> None:
  parser = argparse.ArgumentParser(description="Holdout selection (deterministic, offline).")
  parser.add_argument("--inventory", required=True)
  parser.add_argument("--protocol", required=True)
  parser.add_argument("--seed", type=int, default=None)
  parser.add_argument("--phase", choices=["A", "B"], default="A")
  parser.add_argument("--question-index", default=None)
  parser.add_argument("--content-fingerprints", default=None,
                      help="JSON mapping normalizedRelativePath -> contentFingerprint (tests/preflight).")
  parser.add_argument("--fingerprint-cache", default=None,
                      help="JSON cache path; computes SHA-256 of candidate PDFs when no mapping is given.")
  parser.add_argument("--out", required=True)
  args = parser.parse_args()

  protocol = _load(args.protocol)
  schema.validate_protocol(protocol)
  inventory = _load(args.inventory)
  seed = args.seed if args.seed is not None else int(protocol["selectionSeed"])

  content_hashes = _load(args.content_fingerprints) if args.content_fingerprints else None
  fingerprint_cache = schema.load_fingerprint_cache(args.fingerprint_cache) if args.fingerprint_cache else None
  candidate = build_candidate_pool(inventory, protocol, content_hashes=content_hashes, fingerprint_cache=fingerprint_cache)
  selection = select_documents(candidate["pool"], protocol["randomHoldout"], seed)

  if selection["status"] != "ok":
    print(json.dumps({"status": selection["status"], "unsatisfied": selection["unsatisfied"], "stats": selection["stats"]}, ensure_ascii=False, indent=2))
    raise SystemExit(2)

  provenance = {
    "protocolSha256": schema.sha256_file(args.protocol),
    "inventorySha256": schema.sha256_file(args.inventory),
    "candidatePoolHash": schema.canonical_content_pool_hash(candidate["pool"]),
    "candidatePoolPathHash": schema.sha256_json(sorted(document["normalizedRelativePath"] for document in candidate["pool"])),
    **code_identity(),
  }
  question_index = _load(args.question_index) if args.question_index else None
  if question_index:
    schema.validate_question_index(question_index)
  manifest = build_manifest(protocol, provenance, selection, question_index, seed)
  schema.validate_manifest(manifest)
  if question_index:
    schema.validate_bindings(manifest, question_index=question_index)
  if fingerprint_cache is not None and args.fingerprint_cache:
    schema.save_fingerprint_cache(args.fingerprint_cache, fingerprint_cache)
  schema.write_json(args.out, manifest)
  print(json.dumps({
    "status": "ok",
    "out": args.out,
    "documents": len(manifest["documents"]),
    "reservedCount": manifest["reservedCount"],
    "selectionCodeState": manifest["selectionCodeState"],
    "candidatePoolStats": candidate["stats"],
  }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
  main()

