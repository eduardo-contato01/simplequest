from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Any


PROTOCOL_VERSION = "holdout-v1"
SUPPORTED_PROTOCOL_VERSIONS = ("holdout-v1", "holdout-v2")
SELECTOR_VERSION = "holdout-v1"
SELECTOR_VERSION_BY_PROTOCOL = {"holdout-v1": "holdout-v1", "holdout-v2": "holdout-v2"}
FINGERPRINT_CACHE_VERSION = 1

ANSWER_KEY_DIRECTORY_SEGMENTS = ("gabarito", "gabaritos")
ANSWER_KEY_FILENAME_TOKENS = ("gabarito", "gabaritos")
ANSWER_KEY_FILENAME_PREFIX = "gab_"

SOURCE_CLASSES = ("text_native", "raster", "text_low_quality", "hybrid")
SPLITS = ("random", "challenge", "reserved")

RESPONSE_MODES = ("single_choice", "true_false", "numeric", "discursive", "other", "unknown")
LAYOUTS = ("vertical", "two_column", "grid", "parent_child", "internal_enumeration", "mixed", "none", "unknown")
MARKER_STYLES = ("textual", "parenthesized", "circled_outline", "circled_filled", "symbolic_control", "none", "mixed", "unknown")
CONTENT_KINDS = ("text", "math", "media", "mixed", "none", "unknown")

QUESTION_CLASSES = ("correct", "partial", "safe_abstention", "unsafe_error", "not_applicable", "not_executable")


class HoldoutValidationError(ValueError):
  pass


def sha256_bytes(data: bytes) -> str:
  return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
  return sha256_bytes(text.encode("utf-8"))


def sha256_file(path: str | Path) -> str:
  return sha256_bytes(Path(path).read_bytes())


def sha256_json(obj: Any) -> str:
  return sha256_text(json.dumps(obj, ensure_ascii=False, sort_keys=True))


def content_fingerprint_file(path: str | Path) -> str:
  return sha256_bytes(Path(path).read_bytes())


def content_fingerprint_bytes(data: bytes) -> str:
  return sha256_bytes(data)


def load_fingerprint_cache(path: str | Path) -> dict[str, Any]:
  target = Path(path)
  if not target.exists():
    return {"cacheVersion": FINGERPRINT_CACHE_VERSION, "entries": {}}
  data = json.loads(target.read_text(encoding="utf-8"))
  if data.get("cacheVersion") != FINGERPRINT_CACHE_VERSION:
    return {"cacheVersion": FINGERPRINT_CACHE_VERSION, "entries": {}}
  return data


def save_fingerprint_cache(path: str | Path, cache: dict[str, Any]) -> None:
  target = Path(path)
  target.parent.mkdir(parents=True, exist_ok=True)
  target.write_text(json.dumps(cache, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def fingerprint_with_cache(path: str | Path, cache: dict[str, Any]) -> str | None:
  file_path = Path(path)
  if not file_path.exists():
    return None
  stat = file_path.stat()
  key = str(file_path)
  entry = (cache.setdefault("entries", {})).get(key)
  if entry and entry.get("sizeBytes") == stat.st_size and entry.get("mtimeNs") == stat.st_mtime_ns:
    return entry.get("contentFingerprint")
  fingerprint = content_fingerprint_file(file_path)
  cache["entries"][key] = {
    "sizeBytes": stat.st_size,
    "mtimeNs": stat.st_mtime_ns,
    "contentFingerprint": fingerprint,
  }
  return fingerprint


def canonical_content_pool_hash(candidates: list[dict[str, Any]]) -> str:
  canonical = sorted(
    [
      {
        "contentFingerprint": candidate["contentFingerprint"],
        "family": candidate["family"],
        "year": candidate["year"],
        "series": candidate.get("series"),
        "sourceType": candidate["sourceType"],
      }
      for candidate in candidates
    ],
    key=lambda item: (item["contentFingerprint"], item["family"], item["year"], item["sourceType"]),
  )
  return sha256_json(canonical)


def reserved_pool_hash(content_fingerprints: list[str]) -> str:
  return sha256_json(sorted(set(content_fingerprints)))


def validate_no_content_overlap(sets: dict[str, list[str]]) -> None:
  owners: dict[str, str] = {}
  for set_name, fingerprints in sets.items():
    for fingerprint in fingerprints:
      owner = owners.get(fingerprint)
      if owner is not None and owner != set_name:
        raise HoldoutValidationError(f"contentFingerprint {fingerprint} present in both {owner} and {set_name}")
      owners[fingerprint] = set_name


def validate_bindings(manifest: dict[str, Any], question_index: dict[str, Any] | None = None,
                      ground_truth: dict[str, Any] | None = None) -> None:
  manifest_by_id = {document["documentId"]: document for document in manifest.get("documents", [])}
  if question_index is not None:
    for document in question_index.get("documents", []):
      reference = manifest_by_id.get(document["documentId"])
      if reference is None:
        raise HoldoutValidationError(f"questionIndex: unknown documentId {document['documentId']}")
      if document.get("contentFingerprint") != reference.get("contentFingerprint"):
        raise HoldoutValidationError(
          f"questionIndex: contentFingerprint mismatch for {document['documentId']}"
        )
  if ground_truth is not None:
    if ground_truth.get("manifestSha256") is not None and ground_truth["manifestSha256"] != sha256_json(manifest):
      raise HoldoutValidationError("groundTruth: manifestSha256 does not match manifest")
    for document_id, fingerprint in (ground_truth.get("documentFingerprints") or {}).items():
      reference = manifest_by_id.get(document_id)
      if reference is None or reference.get("contentFingerprint") != fingerprint:
        raise HoldoutValidationError(f"groundTruth: contentFingerprint mismatch for {document_id}")


def _require(condition: bool, message: str) -> None:
  if not condition:
    raise HoldoutValidationError(message)


def selector_version_for(protocol_version: str) -> str:
  return SELECTOR_VERSION_BY_PROTOCOL.get(protocol_version, SELECTOR_VERSION)


def normalize_metadata_text(value: str) -> str:
  import unicodedata
  text = unicodedata.normalize("NFKD", str(value or ""))
  text = "".join(char for char in text if not unicodedata.combining(char))
  text = text.casefold()
  text = re.sub(r"[_\-\.\\/]+", " ", text)
  text = re.sub(r"\s+", " ", text).strip()
  return text


def normalize_metadata_path(value: str) -> str:
  import unicodedata
  text = unicodedata.normalize("NFKD", str(value or "").replace("\\", "/"))
  text = "".join(char for char in text if not unicodedata.combining(char))
  text = text.casefold()
  return text


def is_eligible_question_document(metadata: dict[str, Any]) -> tuple[bool, str | None]:
  # Metadata-only sampling-frame filter. Only clearly non-question document
  # roles (answer keys) are excluded; ambiguous names remain eligible.
  relative = str(metadata.get("relativePath") or metadata.get("path") or "")
  normalized_path = normalize_metadata_path(relative)
  segments = [normalize_metadata_text(segment) for segment in normalized_path.split("/") if segment]
  for segment in segments:
    if segment in ANSWER_KEY_DIRECTORY_SEGMENTS:
      return False, "answer_key_directory"
  import os
  basename = os.path.basename(normalized_path)
  stem = basename.rsplit(".", 1)[0] if "." in basename else basename
  stem_tokens = stem.split()
  if stem.startswith(ANSWER_KEY_FILENAME_PREFIX):
    return False, "answer_key_filename"
  if stem_tokens and stem_tokens[0] == "gab" and len(stem_tokens) > 1:
    return False, "answer_key_filename"
  if any(token in ANSWER_KEY_FILENAME_TOKENS for token in stem_tokens):
    return False, "answer_key_filename"
  return True, None


def validate_protocol(protocol: dict[str, Any]) -> None:
  _require(protocol.get("protocolVersion") in SUPPORTED_PROTOCOL_VERSIONS, "protocol: protocolVersion must be holdout-v1")
  random_cfg = protocol.get("randomHoldout")
  _require(isinstance(random_cfg, dict), "protocol: randomHoldout missing")
  _require(int(random_cfg.get("targetDocuments", 0)) > 0, "protocol: targetDocuments must be > 0")
  _require(int(random_cfg.get("questionsPerDocument", 0)) > 0, "protocol: questionsPerDocument must be > 0")
  quota = random_cfg.get("sourceQuota")
  _require(isinstance(quota, dict) and quota, "protocol: sourceQuota missing")
  for source, count in quota.items():
    _require(source in SOURCE_CLASSES, f"protocol: unknown sourceClass in quota: {source}")
    _require(int(count) >= 0, f"protocol: quota must be >= 0 for {source}")
  dev = protocol.get("developmentDocuments")
  _require(isinstance(dev, list) and dev, "protocol: developmentDocuments missing")
  _require(isinstance(protocol.get("challengeSet"), dict), "protocol: challengeSet missing")


def candidate_metadata_reason(entry: dict[str, Any]) -> str | None:
  # Returns None when the entry has usable metadata for sampling-frame
  # eligibility, or a machine-readable reason when it must be excluded as
  # invalid_metadata (checked before any downstream conversion/constraint).
  for field in ("path", "relativePath", "institution", "year", "pageCount", "classification"):
    if field not in entry:
      return f"missing_field:{field}"
  if entry.get("classification") not in SOURCE_CLASSES:
    return "bad_classification"
  year = entry.get("year")
  if year is None:
    return "invalid_year"
  if isinstance(year, bool):
    return "invalid_year"
  if isinstance(year, str):
    if not year.strip():
      return "invalid_year"
    try:
      int(year)
    except ValueError:
      return "invalid_year"
  elif not isinstance(year, (int, float)):
    return "invalid_year"
  try:
    if int(entry.get("pageCount")) < 0:
      return "bad_pageCount"
  except (TypeError, ValueError):
    return "bad_pageCount"
  return None


def validate_candidate_entry(entry: dict[str, Any], index: int) -> None:
  for field in ("path", "relativePath", "institution", "year", "pageCount", "classification"):
    _require(field in entry, f"candidate[{index}]: missing {field}")
  _require(entry["classification"] in SOURCE_CLASSES, f"candidate[{index}]: bad classification {entry['classification']}")
  _require(int(entry["pageCount"]) >= 0, f"candidate[{index}]: bad pageCount")


def validate_manifest(manifest: dict[str, Any]) -> None:
  _require(manifest.get("protocolVersion") in SUPPORTED_PROTOCOL_VERSIONS, "manifest: bad protocolVersion")
  _require(isinstance(manifest.get("selectionSeed"), int), "manifest: selectionSeed missing/not int")
  _require(isinstance(manifest.get("selectionConfig"), dict), "manifest: selectionConfig missing")
  _require(isinstance(manifest.get("documents"), list) and manifest["documents"], "manifest: documents missing")
  seen = set()
  for index, document in enumerate(manifest["documents"]):
    for field in ("documentId", "canonicalPath", "contentFingerprint", "family", "year", "sourceType"):
      _require(field in document, f"manifest.documents[{index}]: missing {field}")
    _require(document["sourceType"] in SOURCE_CLASSES, f"manifest.documents[{index}]: bad sourceType")
    _require(document["documentId"] not in seen, f"manifest.documents[{index}]: duplicate documentId {document['documentId']}")
    seen.add(document["documentId"])
    questions = document.get("selectedQuestions", [])
    _require(isinstance(questions, list), f"manifest.documents[{index}]: selectedQuestions must be a list")
    for qindex, question in enumerate(questions):
      for field in ("questionId", "questionNumber", "pageStart", "pageEnd"):
        _require(field in question, f"manifest.documents[{index}].selectedQuestions[{qindex}]: missing {field}")


def validate_question_index(index: dict[str, Any]) -> None:
  _require(index.get("protocolVersion") in SUPPORTED_PROTOCOL_VERSIONS, "questionIndex: bad protocolVersion")
  _require(isinstance(index.get("documents"), list), "questionIndex: documents missing")
  for dindex, document in enumerate(index["documents"]):
    for field in ("documentId", "contentFingerprint", "questions"):
      _require(field in document, f"questionIndex.documents[{dindex}]: missing {field}")
    _require(isinstance(document["questions"], list) and document["questions"], f"questionIndex.documents[{dindex}]: empty questions")
    for qindex, question in enumerate(document["questions"]):
      for field in ("questionId", "questionNumber", "pageStart", "pageEnd"):
        _require(field in question, f"questionIndex.documents[{dindex}].questions[{qindex}]: missing {field}")


def validate_ground_truth(gt: dict[str, Any]) -> None:
  _require(gt.get("protocolVersion") in SUPPORTED_PROTOCOL_VERSIONS, "groundTruth: bad protocolVersion")
  _require(isinstance(gt.get("questions"), list) and gt["questions"], "groundTruth: questions missing")
  for index, item in enumerate(gt["questions"]):
    for field in ("documentId", "questionId", "responseMode", "layout", "markerStyle", "contentKind"):
      _require(field in item, f"groundTruth.questions[{index}]: missing {field}")
    _require(item["responseMode"] in RESPONSE_MODES, f"groundTruth.questions[{index}]: bad responseMode {item['responseMode']}")
    _require(item["layout"] in LAYOUTS, f"groundTruth.questions[{index}]: bad layout {item['layout']}")
    _require(item["markerStyle"] in MARKER_STYLES, f"groundTruth.questions[{index}]: bad markerStyle {item['markerStyle']}")
    _require(item["contentKind"] in CONTENT_KINDS, f"groundTruth.questions[{index}]: bad contentKind {item['contentKind']}")
    count = item.get("optionCount")
    _require(count is None or (isinstance(count, int) and count >= 0), f"groundTruth.questions[{index}]: bad optionCount")
    labels = item.get("optionLabels")
    _require(labels is None or (isinstance(labels, list) and all(isinstance(label, str) for label in labels)),
             f"groundTruth.questions[{index}]: bad optionLabels")


def validate_challenge(challenge: dict[str, Any]) -> None:
  _require(challenge.get("protocolVersion") in SUPPORTED_PROTOCOL_VERSIONS, "challenge: bad protocolVersion")
  _require(isinstance(challenge.get("documents"), list), "challenge: documents missing")
  for index, document in enumerate(challenge["documents"]):
    for field in ("documentId", "family", "year", "sourceType", "pathologies"):
      _require(field in document, f"challenge.documents[{index}]: missing {field}")


def manifest_hashes(manifest: dict[str, Any], question_index: dict[str, Any] | None, ground_truth: dict[str, Any] | None) -> dict[str, Any]:
  return {
    "manifestSha256": sha256_json(manifest),
    "questionIndexSha256": sha256_json(question_index) if question_index is not None else None,
    "groundTruthSha256": sha256_json(ground_truth) if ground_truth is not None else None,
  }


def load_json(path: str | Path) -> Any:
  return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path: str | Path, obj: Any) -> None:
  target = Path(path)
  target.parent.mkdir(parents=True, exist_ok=True)
  target.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")

