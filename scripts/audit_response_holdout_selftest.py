from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_holdout_schema as schema  # noqa: E402
import audit_response_holdout as runner  # noqa: E402
import audit_response_holdout_select as selector  # noqa: E402

FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
  if condition:
    print(f"PASS {name}")
  else:
    print(f"FAIL {name} {detail}")
    FAILURES.append(name)


def entry(name: str, institution: str, year: int, source: str, pages: int = 12, series: str = "6o Ano") -> dict:
  relative = f"{institution}/{name}"
  return {"path": f"G:/fake/{relative}", "relativePath": relative, "institution": institution,
          "year": year, "series": series, "pageCount": pages, "classification": source}


def protocol(target: int = 8, questions: int = 3) -> dict:
  return {
    "protocolVersion": "holdout-v1",
    "selectionSeed": 1234,
    "randomHoldout": {
      "targetDocuments": target, "questionsPerDocument": questions, "maxDocumentsPerFamily": 2,
      "minFamilies": 3, "minDistinctYears": 3, "eras": ["2004-2009", "2010-2014", "2015-2019", "2020-2025"],
      "sourceQuota": {"text_native": 3, "raster": 2, "text_low_quality": 2, "hybrid": 1},
    },
    "challengeSet": {"targetDocuments": 16},
    "developmentDocuments": ["DEV - 6ANO - 2020.pdf"],
  }


def inventory() -> dict:
  pdfs = [
    entry("A - 6ANO - 2006 (mat).pdf", "CMF", 2006, "text_native"),
    entry("B - 6ANO - 2008 (mat).pdf", "CMF", 2008, "raster"),
    entry("C - 6ANO - 2011 (mat).pdf", "CMJF", 2011, "text_native"),
    entry("D - 6ANO - 2013 (mat).pdf", "CMJF", 2013, "text_low_quality"),
    entry("E - 6ANO - 2016 (mat).pdf", "CMM", 2016, "text_native"),
    entry("F - 6ANO - 2017 (mat).pdf", "CMM", 2017, "hybrid"),
    entry("G - 6ANO - 2019 (mat).pdf", "CMPA", 2019, "raster"),
    entry("H - 6ANO - 2021 (mat).pdf", "CMPA", 2021, "text_low_quality"),
    entry("I - 6ANO - 2023 (mat).pdf", "CMR", 2023, "text_native"),
    entry("J - 6ANO - 2024 (mat).pdf", "CMR", 2024, "text_native"),
    entry("K - 6ANO - 2012 (mat).pdf", "CMS", 2012, "text_native"),
    entry("L - 6ANO - 2015 (mat).pdf", "CMS", 2015, "raster"),
    entry("M - 6ANO - 2018 (mat).pdf", "CMT", 2018, "text_low_quality"),
    entry("N - 6ANO - 2022 (mat).pdf", "CMT", 2022, "hybrid"),
    entry("DUP-A - 6ANO - 2020 (mat).pdf", "CMSM", 2020, "text_native"),
    entry("Z/DUP-A - 6ANO - 2020 (mat).pdf", "CMSM", 2020, "text_native"),
    entry("DEV - 6ANO - 2020.pdf", "CMVM", 2020, "text_native"),
  ]
  return {"pdfs": pdfs}


def content_map() -> dict:
  # Each path -> content fingerprint. The two DUP entries share content.
  dup = schema.sha256_text("content:duplicate")
  mapping = {"cmf/a - 6ano - 2006 (mat).pdf": schema.sha256_text("content:A")}
  for relative in [
    "CMF/A - 6ANO - 2006 (mat).pdf", "CMF/B - 6ANO - 2008 (mat).pdf", "CMJF/C - 6ANO - 2011 (mat).pdf",
    "CMJF/D - 6ANO - 2013 (mat).pdf", "CMM/E - 6ANO - 2016 (mat).pdf", "CMM/F - 6ANO - 2017 (mat).pdf",
    "CMPA/G - 6ANO - 2019 (mat).pdf", "CMPA/H - 6ANO - 2021 (mat).pdf", "CMR/I - 6ANO - 2023 (mat).pdf",
    "CMR/J - 6ANO - 2024 (mat).pdf", "CMS/K - 6ANO - 2012 (mat).pdf", "CMS/L - 6ANO - 2015 (mat).pdf",
    "CMT/M - 6ANO - 2018 (mat).pdf", "CMT/N - 6ANO - 2022 (mat).pdf",
    "CMSM/DUP-A - 6ANO - 2020 (mat).pdf", "CMSM/Z/DUP-A - 6ANO - 2020 (mat).pdf",
    "CMVM/DEV - 6ANO - 2020.pdf",
  ]:
    mapping[relative.lower()] = schema.sha256_text("content:" + relative)
  mapping["cmsm/dup-a - 6ano - 2020 (mat).pdf"] = dup
  mapping["cmsm/z/dup-a - 6ano - 2020 (mat).pdf"] = dup
  mapping["cmvm/dev - 6ano - 2020.pdf"] = schema.sha256_text("content:development")
  return mapping


def gt_question(response_mode="single_choice", count=5, labels=None, layout="vertical",
                marker="parenthesized", content="text", doc="doc-1", qid="q1") -> dict:
  return {"documentId": doc, "questionId": qid, "pages": [1], "responseMode": response_mode,
          "optionCount": count, "optionLabels": labels, "subitems": None, "responseControls": None,
          "layout": layout, "markerStyle": marker, "contentKind": content, "notes": None}


def fusion_result(count=None, labels=None, agreement="partial", interpretation="medium") -> dict:
  return {"agreement": agreement, "sources": ["visual"], "slots": [], "optionCountHypothesis": count,
          "optionLabelsHypothesis": labels, "observationConfidence": "high", "interpretationConfidence": interpretation,
          "blockers": [], "hardBlockers": [], "softBlockers": []}


def provenance() -> dict:
  return {"protocolSha256": "p", "inventorySha256": "i", "candidatePoolHash": "c",
          "candidatePoolPathHash": "cp", "gitCommit": "abc", "selectionCodeState": "clean", "selectorSha256": None}


def test_deterministic_and_quotas() -> None:
  proto = protocol()
  pool = selector.build_candidate_pool(inventory(), proto, content_hashes=content_map())["pool"]
  first = selector.select_documents(pool, proto["randomHoldout"], 1234)
  second = selector.select_documents(pool, proto["randomHoldout"], 1234)
  check("select.deterministic", [d["documentId"] for d in first["documents"]] == [d["documentId"] for d in second["documents"]])
  check("select.status", first["status"] == "ok", first["unsatisfied"])
  check("select.quota", first["stats"]["bySource"].get("text_native") == 3 and first["stats"]["bySource"].get("raster") == 2, first["stats"])
  check("select.family_cap", all(count <= 2 for count in first["stats"]["families"].values()), first["stats"]["families"])
  check("select.eras", len(first["stats"]["coveredEras"]) >= 3, first["stats"])
  check("select.reserved", first["reservedCount"] > 0, first)


def test_pool_filters() -> None:
  proto = protocol()
  built = selector.build_candidate_pool(inventory(), proto, content_hashes=content_map())
  check("pool.dev_excluded", built["stats"]["excludedDevelopment"] == 1, built["stats"])
  check("pool.duplicate_excluded", built["stats"]["excludedDuplicateFingerprint"] == 1, built["stats"])
  check("pool.size", built["stats"]["poolSize"] == 15, built["stats"])


def test_same_content_dedup_and_canonical() -> None:
  proto = protocol()
  pool = selector.build_candidate_pool(inventory(), proto, content_hashes=content_map())["pool"]
  duplicates = [document for document in pool if document["duplicateCount"] > 0]
  check("dedup.one_entry", len(duplicates) == 1, duplicates)
  check("dedup.canonical_min", duplicates[0]["normalizedRelativePath"] == "cmsm/dup-a - 6ano - 2020 (mat).pdf", duplicates)


def test_same_filename_different_content() -> None:
  proto = protocol()
  inv = {"pdfs": [
    entry("P - 6ANO - 2010 (mat).pdf", "CMF", 2010, "text_native"),
    entry("X/P - 6ANO - 2010 (mat).pdf", "CMZ", 2010, "text_native"),
  ]}
  hashes = {
    "cmf/p - 6ano - 2010 (mat).pdf": schema.sha256_text("content:one"),
    "cmz/x/p - 6ano - 2010 (mat).pdf": schema.sha256_text("content:two"),
  }
  built = selector.build_candidate_pool(inv, proto, content_hashes=hashes)
  check("samefile.two", built["stats"]["poolSize"] == 2, built["stats"])


def test_development_excluded_by_content() -> None:
  proto = protocol()
  dev_fp = schema.sha256_text("content:development")
  inv = {"pdfs": [entry("COPY - 6ANO - 2020.pdf", "CMX", 2020, "text_native")]}
  hashes = {"cmx/copy - 6ano - 2020.pdf": dev_fp}
  built = selector.build_candidate_pool(inv, proto, content_hashes=hashes, dev_fingerprints={dev_fp})
  check("devcontent.excluded", built["stats"]["poolSize"] == 0 and built["stats"]["excludedDevelopment"] == 1, built["stats"])


def test_overlap_guard() -> None:
  try:
    schema.validate_no_content_overlap({"random": ["x"], "challenge": ["x"]})
    check("overlap.reject", False, "should have raised")
  except schema.HoldoutValidationError:
    check("overlap.reject", True)


def test_reserved_unique_and_order_independent() -> None:
  check("reserved.order", schema.reserved_pool_hash(["b", "a", "b"]) == schema.reserved_pool_hash(["a", "b"]))
  proto = protocol()
  pool = selector.build_candidate_pool(inventory(), proto, content_hashes=content_map())["pool"]
  selection = selector.select_documents(pool, proto["randomHoldout"], 1234)
  check("reserved.unique", selection["reservedCount"] == len({d["contentFingerprint"] for d in pool}) - len(selection["documents"]), selection["stats"])


def test_candidate_pool_hash_order_independent() -> None:
  proto = protocol()
  pool = selector.build_candidate_pool(inventory(), proto, content_hashes=content_map())["pool"]
  shuffled = list(reversed(pool))
  check("poolhash.order", schema.canonical_content_pool_hash(pool) == schema.canonical_content_pool_hash(shuffled))


def test_bindings_index_and_gt() -> None:
  proto = protocol()
  pool = selector.build_candidate_pool(inventory(), proto, content_hashes=content_map())["pool"]
  selection = selector.select_documents(pool, proto["randomHoldout"], 1234)
  manifest = selector.build_manifest(proto, provenance(), selection, None, 1234)
  document = manifest["documents"][0]
  good_index = {"protocolVersion": "holdout-v1", "documents": [
    {"documentId": document["documentId"], "contentFingerprint": document["contentFingerprint"],
     "questions": [{"questionId": "q1", "questionNumber": 1, "pageStart": 1, "pageEnd": 1}]}]}
  schema.validate_bindings(manifest, question_index=good_index)
  bad_index = {"protocolVersion": "holdout-v1", "documents": [
    {"documentId": document["documentId"], "contentFingerprint": "wrong",
     "questions": [{"questionId": "q1", "questionNumber": 1, "pageStart": 1, "pageEnd": 1}]}]}
  try:
    schema.validate_bindings(manifest, question_index=bad_index)
    check("bind.index_reject", False, "should have raised")
  except schema.HoldoutValidationError:
    check("bind.index_reject", True)
  bad_gt = {"protocolVersion": "holdout-v1", "manifestSha256": "wrong", "documentFingerprints": {}}
  try:
    schema.validate_bindings(manifest, ground_truth=bad_gt)
    check("bind.gt_reject", False, "should have raised")
  except schema.HoldoutValidationError:
    check("bind.gt_reject", True)
  good_gt = {"protocolVersion": "holdout-v1", "manifestSha256": schema.sha256_json(manifest),
             "documentFingerprints": {document["documentId"]: document["contentFingerprint"]}}
  schema.validate_bindings(manifest, ground_truth=good_gt)


def test_fingerprint_mismatch_runner() -> None:
  document = {"documentId": "d", "canonicalPath": "G:/x.pdf", "contentFingerprint": "expected"}
  check("mismatch.detect", runner.verify_document_fingerprint(document, fingerprint_fn=lambda path: "other") == "source_fingerprint_mismatch")
  check("mismatch.ok", runner.verify_document_fingerprint(document, fingerprint_fn=lambda path: "expected") is None)


def test_fingerprint_cache_invalidation() -> None:
  with tempfile.TemporaryDirectory() as tmp:
    file_path = Path(tmp) / "a.pdf"
    cache: dict = {"cacheVersion": schema.FINGERPRINT_CACHE_VERSION, "entries": {}}
    file_path.write_bytes(b"one")
    first = schema.fingerprint_with_cache(file_path, cache)
    second = schema.fingerprint_with_cache(file_path, cache)
    check("cache.hit", first == second and first == schema.sha256_bytes(b"one"))
    file_path.write_bytes(b"two-longer")
    os.utime(file_path, (1, 1))
    third = schema.fingerprint_with_cache(file_path, cache)
    check("cache.invalidate", third == schema.sha256_bytes(b"two-longer") and third != first)


def test_protocol_hash_stable() -> None:
  proto = protocol()
  check("protocolhash.stable", schema.sha256_json(proto) == schema.sha256_json(proto))


def test_selector_identity_registered() -> None:
  proto = protocol()
  pool = selector.build_candidate_pool(inventory(), proto, content_hashes=content_map())["pool"]
  selection = selector.select_documents(pool, proto["randomHoldout"], 1234)
  manifest = selector.build_manifest(proto, provenance(), selection, None, 1234)
  check("identity.selectorVersion", manifest.get("selectorVersion") == schema.SELECTOR_VERSION, manifest.get("selectorVersion"))
  check("identity.git", "gitCommit" in manifest and "selectionCodeState" in manifest, manifest)


def test_constraint_failure() -> None:
  proto = protocol(target=8)
  small = {"pdfs": [entry("X - 6ANO - 2010.pdf", "CMF", 2010, "text_native")]}
  hashes = {"cmf/x - 6ano - 2010.pdf": schema.sha256_text("content:x")}
  pool = selector.build_candidate_pool(small, proto, content_hashes=hashes)["pool"]
  result = selector.select_documents(pool, proto["randomHoldout"], 1234)
  check("constraint.failure", result["status"] == "selection_constraints_unsatisfied", result)
  check("constraint.reason", any(item["constraint"] == "sourceQuota" for item in result["unsatisfied"]), result["unsatisfied"])


def test_question_tertiles() -> None:
  questions = [{"questionId": f"q{i}", "questionNumber": i, "pageStart": i, "pageEnd": i} for i in range(1, 13)]
  picked = selector.select_questions(questions, 1234, "doc-1", 3)
  check("tertile.count", len(picked) == 3, picked)
  numbers = [q["questionNumber"] for q in picked]
  check("tertile.spread", numbers[0] <= 4 and 5 <= numbers[1] <= 8 and numbers[2] >= 9, numbers)


def test_question_few() -> None:
  one = [{"questionId": "q1", "questionNumber": 1, "pageStart": 1, "pageEnd": 1}]
  two = one + [{"questionId": "q2", "questionNumber": 2, "pageStart": 2, "pageEnd": 2}]
  check("few.one", len(selector.select_questions(one, 1234, "d", 3)) == 1)
  check("few.two", len(selector.select_questions(two, 1234, "d", 3)) == 2)
  check("few.empty", selector.select_questions([], 1234, "d", 3) == [])


def test_hashes_stable() -> None:
  proto = protocol()
  pool = selector.build_candidate_pool(inventory(), proto, content_hashes=content_map())["pool"]
  selection = selector.select_documents(pool, proto["randomHoldout"], 1234)
  manifest = selector.build_manifest(proto, provenance(), selection, None, 1234)
  check("hash.manifest_stable", schema.sha256_json(manifest) == schema.sha256_json(manifest))
  gt = {"protocolVersion": "holdout-v1", "questions": [gt_question()]}
  check("hash.gt_stable", schema.sha256_json(gt) == schema.sha256_json(gt))
  schema.validate_manifest(manifest)


def test_classification() -> None:
  check("cls.numeric_not_applicable", runner.classify_question(gt_question(response_mode="numeric", count=None, labels=None, layout="none", marker="none", content="math"), fusion_result(count=None, labels=None))["classification"] == "not_applicable")
  check("cls.option_abstention", runner.classify_question(gt_question(count=5, labels=None), fusion_result(count=None, labels=None))["classification"] == "safe_abstention")
  under = runner.classify_question(gt_question(count=5, labels=None), fusion_result(count=4, labels=None))
  check("cls.undercount", under["classification"] == "unsafe_error" and under["countErrorDirection"] == "under", under)
  over = runner.classify_question(gt_question(count=4, labels=None), fusion_result(count=5, labels=None))
  check("cls.overcount", over["classification"] == "unsafe_error" and over["countErrorDirection"] == "over", over)
  partial = runner.classify_question(gt_question(count=5, labels=["A", "B", "C", "D", "E"]), fusion_result(count=5, labels="unknown"))
  check("cls.labels_unknown_partial", partial["classification"] == "partial" and partial["labelsCorrect"] is False, partial)
  correct = runner.classify_question(gt_question(count=4, labels=["A", "B", "C", "D"]), fusion_result(count=4, labels="A-D"))
  check("cls.labels_correct", correct["classification"] == "correct", correct)
  check("cls.not_executable", runner.classify_question(gt_question(count=5, labels=None), {}, executable=False)["classification"] == "not_executable")


def test_false_conflict_and_document_summary() -> None:
  record = {"classification": "partial", "countApplicable": True, "countEmitted": False, "countCorrect": None,
            "labelsApplicable": False, "labelsEmitted": False, "labelsCorrect": None, "unsafeCertainty": False,
            "countErrorDirection": None, "hasUsable": True, "conflict": True, "unambiguousGroundTruth": True}
  metrics = runner.compute_metrics([record])
  check("metrics.false_conflict", metrics["falseConflictRate"] == 1.0, metrics)
  records = [
    {"documentId": "doc-1", "questionId": "q1", "classification": "correct", "countApplicable": True, "countEmitted": True, "countCorrect": True, "labelsApplicable": False, "labelsEmitted": False, "labelsCorrect": None, "unsafeCertainty": False, "countErrorDirection": None, "hasUsable": True, "conflict": False},
    {"documentId": "doc-1", "questionId": "q2", "classification": "unsafe_error", "countApplicable": True, "countEmitted": True, "countCorrect": False, "labelsApplicable": False, "labelsEmitted": False, "labelsCorrect": None, "unsafeCertainty": True, "countErrorDirection": "over", "hasUsable": True, "conflict": False},
  ]
  summary = runner.document_summary(records)
  check("docsummary.unsafe", summary["documents"]["doc-1"]["documentHasUnsafeError"] is True, summary)
  check("docsummary.ratio", summary["documentsWithoutUnsafeErrorRatio"] == 0.0, summary)


def test_slice_and_labels() -> None:
  records = [{"classification": "correct", "sourceType": "text_native", "family": "CMF", "era": "2010-2014",
              "responseMode": "single_choice", "layout": "vertical", "markerStyle": "textual", "contentKind": "text",
              "origins": ["visual_marker"]}]
  slices = runner.compute_slices(records)
  check("slice.descriptive_only", slices["sourceType"]["text_native"]["descriptiveOnly"] is True, slices["sourceType"])
  check("labels.A-E", runner.labels_to_set("A-E") == {"A", "B", "C", "D", "E"})
  check("labels.CE", runner.labels_to_set("CE") == {"C", "E"})
  check("labels.unknown", runner.labels_to_set("unknown") is None)


def test_validators() -> None:
  invalid_manifest = {"protocolVersion": "holdout-v1", "selectionSeed": 1, "selectionConfig": {}, "documents": [
    {"documentId": "d1", "canonicalPath": "x", "contentFingerprint": "f", "family": "CMF", "year": 2010, "sourceType": "bogus"}]}
  try:
    schema.validate_manifest(invalid_manifest)
    check("validators.manifest_reject", False, "should have raised")
  except schema.HoldoutValidationError:
    check("validators.manifest_reject", True)
  invalid_gt = {"protocolVersion": "holdout-v1", "questions": [gt_question(response_mode="invalid")]}
  try:
    schema.validate_ground_truth(invalid_gt)
    check("validators.gt_reject", False, "should have raised")
  except schema.HoldoutValidationError as exc:
    check("validators.gt_reject", "responseMode" in str(exc), str(exc))
  schema.validate_challenge({"protocolVersion": "holdout-v1", "documents": [
    {"documentId": "c1", "family": "CMF", "year": 2010, "sourceType": "raster", "pathologies": ["grid"]}]})


def test_development_config_coherence() -> None:
  import glob
  import json as _json
  protocol_path = ROOT / "audit" / "holdout" / "protocol-v1.json"
  data = _json.loads(protocol_path.read_text(encoding="utf-8"))
  cases = data.get("developmentCases") or []
  documents = data.get("developmentDocuments") or []
  check("devconfig.cases", len(cases) == 12, cases)
  check("devconfig.documents", len(documents) == 6, documents)
  prefixes = {str(case).split("-")[0] for case in cases}
  check("devconfig.families", prefixes == {"CMBH17", "CMC11", "CMBH18", "CMBel17", "CMT22", "PAS19"}, prefixes)


def main() -> None:
  test_deterministic_and_quotas()
  test_pool_filters()
  test_same_content_dedup_and_canonical()
  test_same_filename_different_content()
  test_development_excluded_by_content()
  test_overlap_guard()
  test_reserved_unique_and_order_independent()
  test_candidate_pool_hash_order_independent()
  test_bindings_index_and_gt()
  test_fingerprint_mismatch_runner()
  test_fingerprint_cache_invalidation()
  test_protocol_hash_stable()
  test_selector_identity_registered()
  test_constraint_failure()
  test_question_tertiles()
  test_question_few()
  test_hashes_stable()
  test_classification()
  test_false_conflict_and_document_summary()
  test_slice_and_labels()
  test_validators()
  test_development_config_coherence()
  if FAILURES:
    print(f"\n{len(FAILURES)} checks falharam: {FAILURES}")
    raise SystemExit(1)
  print("\nTodos os checks de endurecimento do holdout passaram.")


if __name__ == "__main__":
  main()
