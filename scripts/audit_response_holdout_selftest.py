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


def test_runner_question_index_hash() -> None:
  manifest = {"protocolVersion": "holdout-v1", "selectionSeed": 1, "selectionConfig": {}, "documents": [
    {"documentId": "d1", "canonicalPath": "G:/nope.pdf", "contentFingerprint": "fp", "family": "CMF",
     "year": 2010, "sourceType": "text_native",
     "selectedQuestions": [{"questionId": "d1:q1", "questionNumber": 1, "pageStart": 1, "pageEnd": 1}]}]}
  ground_truth = {"protocolVersion": "holdout-v1", "manifestSha256": schema.sha256_json(manifest),
                  "documentFingerprints": {"d1": "fp"},
                  "questions": [gt_question(doc="d1", qid="d1:q1")]}
  index = {"protocolVersion": "holdout-v1", "documents": [
    {"documentId": "d1", "contentFingerprint": "fp",
     "questions": [{"questionId": "d1:q1", "questionNumber": 1, "pageStart": 1, "pageEnd": 1}]}]}
  report = runner.evaluate_manifest(manifest, ground_truth, {"protocolVersion": "holdout-v1"},
                                    fingerprint_fn=lambda path: "fp", question_index=index)
  check("runner.index_hash_nonnull", report["hashes"].get("questionIndexSha256") is not None, report["hashes"])
  check("runner.index_hash_matches", report["hashes"].get("questionIndexSha256") == schema.sha256_json(index), report["hashes"])
  without = runner.evaluate_manifest(manifest, ground_truth, {"protocolVersion": "holdout-v1"},
                                     fingerprint_fn=lambda path: "fp")
  check("runner.index_hash_absent", without["hashes"].get("questionIndexSha256") is None, without["hashes"])


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
  for response_mode in ("numeric", "numeric_response"):
    valid_gt = {"protocolVersion": "holdout-v4", "questions": [gt_question(response_mode=response_mode, count=None)]}
    schema.validate_ground_truth(valid_gt)
    check(f"validators.gt_{response_mode}_accept", valid_gt["questions"][0]["responseMode"] == response_mode)
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


def test_metadata_eligibility() -> None:
  cases = [
    ({"relativePath": "CMF/6o Ano/GABARITO/foo.pdf"}, False, "answer_key_directory"),
    ({"relativePath": "CMF/6o Ano/GABARITOS/foo.pdf"}, False, "answer_key_directory"),
    ({"relativePath": "CMF/6o Ano/gab_prova.pdf"}, False, "answer_key_filename"),
    ({"relativePath": "CMF/6o Ano/VEST UnB 2010 GABARITO.pdf"}, False, "answer_key_filename"),
    ({"relativePath": "CMF/6o Ano/Gabriel.pdf"}, True, None),
    ({"relativePath": "CMF/6o Ano/prova_respostas_comentadas.pdf"}, True, None),
    ({"relativePath": "CMF/6o Ano/cartao_geometria.pdf"}, True, None),
    ({"relativePath": "CMF/6o Ano/CMF - 6ANO - 2012_2013 (mat).pdf"}, True, None),
    ({"relativePath": "CMF/6o Ano/GABARITO.pdf"}, False, "answer_key_filename"),
    ({"relativePath": "CMF/6o Ano/Subpasta/GABARITOS/2022-2023 CMRJ.pdf"}, False, "answer_key_directory"),
  ]
  for metadata, expected_eligible, expected_reason in cases:
    eligible, reason = schema.is_eligible_question_document(metadata)
    check(f"meta.{metadata['relativePath']}", eligible == expected_eligible and reason == expected_reason, (eligible, reason))


def test_v1_fingerprint_exclusion() -> None:
  proto = protocol()
  mapping = content_map()
  victim_path = "cmf/b - 6ano - 2008 (mat).pdf"
  victim_fp = mapping[victim_path]
  pool = selector.build_candidate_pool(inventory(), proto, content_hashes=mapping, v1_fingerprints={victim_fp})["pool"]
  check("v1excl.not_in_pool", all(document["contentFingerprint"] != victim_fp for document in pool), pool)
  built = selector.build_candidate_pool(inventory(), proto, content_hashes=mapping, v1_fingerprints={victim_fp})
  check("v1excl.reason", built["stats"]["excludedByReason"].get("v1_revealed_fingerprint") == 1, built["stats"])


def test_answer_key_role_exclusion() -> None:
  proto = protocol()
  inv = {"pdfs": [
    entry("CMF/GABARITO/foo.pdf", "CMF", 2010, "text_native"),
    entry("gab_prova.pdf", "CMF", 2011, "raster"),
    entry("normal.pdf", "CMF", 2012, "text_native"),
  ]}
  mapping = {s: schema.sha256_text("c:" + s) for s in ["cmf/cmf/gabarito/foo.pdf", "cmf/gab_prova.pdf", "cmf/normal.pdf"]}
  built = selector.build_candidate_pool(inv, proto, content_hashes=mapping)
  check("role.pool", built["stats"]["poolSize"] == 1, built["stats"])
  check("role.dir", built["stats"]["excludedByReason"].get("answer_key_directory") == 1, built["stats"])
  check("role.file", built["stats"]["excludedByReason"].get("answer_key_filename") == 1, built["stats"])


def test_v2_quota_abort_low() -> None:
  proto = protocol(target=8)
  proto["randomHoldout"]["sourceQuota"] = {"text_native": 3, "text_low_quality": 2}
  inv = {"pdfs": [entry(f"{c} - 6ANO - 2010.pdf", f"CM{c}", 2010, "text_native") for c in "ABCD"] + [entry("LOW - 6ANO - 2011.pdf", "CMZ", 2011, "text_low_quality")]}
  mapping = {s["relativePath"].lower(): schema.sha256_text("c:" + s["relativePath"]) for s in inv["pdfs"]}
  pool = selector.build_candidate_pool(inv, proto, content_hashes=mapping)["pool"]
  result = selector.select_documents(pool, proto["randomHoldout"], 1234)
  check("quota.low_abort", result["status"] == "selection_constraints_unsatisfied" and any(u["constraint"] == "sourceQuota" and u["sourceType"] == "text_low_quality" for u in result["unsatisfied"]), result["unsatisfied"])


def test_v2_quota_abort_hybrid() -> None:
  proto = protocol(target=8)
  proto["randomHoldout"]["sourceQuota"] = {"text_native": 3, "hybrid": 4}
  inv = {"pdfs": [entry(f"{c} - 6ANO - 2010.pdf", f"CM{c}", 2010, "text_native") for c in "ABCD"] + [entry(f"H{i} - 6ANO - 201{i}.pdf", f"HY{i}", 2015 + i, "hybrid") for i in range(3)]}
  mapping = {s["relativePath"].lower(): schema.sha256_text("c:" + s["relativePath"]) for s in inv["pdfs"]}
  pool = selector.build_candidate_pool(inv, proto, content_hashes=mapping)["pool"]
  result = selector.select_documents(pool, proto["randomHoldout"], 1234)
  check("quota.hybrid_abort", result["status"] == "selection_constraints_unsatisfied" and any(u["constraint"] == "sourceQuota" and u["sourceType"] == "hybrid" for u in result["unsatisfied"]), result["unsatisfied"])


def test_invalid_metadata_null_year() -> None:
  proto = protocol()
  base = entry("VALID - 6ANO - 2010.pdf", "CMF", 2010, "text_native")
  null_year = dict(entry("NULLYEAR - 6ANO - 2010.pdf", "CMF", 2010, "raster"))
  null_year["year"] = None
  missing = dict(entry("MISSING - 6ANO - 2010.pdf", "CMF", 2010, "raster"))
  del missing["year"]
  empty = dict(entry("EMPTY - 6ANO - 2010.pdf", "CMF", 2010, "raster"))
  empty["year"] = ""
  nonnumeric = dict(entry("NONNUM - 6ANO - 2010.pdf", "CMF", 2010, "raster"))
  nonnumeric["year"] = "abc"
  inv = {"pdfs": [base, null_year, missing, empty, nonnumeric]}
  mapping = {"cmf/valid - 6ano - 2010.pdf": schema.sha256_text("c:valid")}
  try:
    built = selector.build_candidate_pool(inv, proto, content_hashes=mapping)
    check("invalidyear.no_crash", True)
    check("invalidyear.pool", built["stats"]["poolSize"] == 1, built["stats"])
    check("invalidyear.count", built["stats"]["excludedByReason"].get("invalid_metadata") == 4, built["stats"])
  except Exception as exc:
    check("invalidyear.no_crash", False, str(exc))
    check("invalidyear.pool", False, "exception")
    check("invalidyear.count", False, "exception")


def test_provenance_not_recomputed() -> None:
  proto = protocol()
  prov = provenance()
  prov["selectionCodeState"] = "clean"
  pool = selector.build_candidate_pool(inventory(), proto, content_hashes=content_map())["pool"]
  selection = selector.select_documents(pool, proto["randomHoldout"], 1234)
  manifest = selector.build_manifest(proto, prov, selection, None, 1234)
  check("prov.clean_preserved", manifest["selectionCodeState"] == "clean", manifest["selectionCodeState"])
  check("prov.selector_v2", schema.selector_version_for(proto["protocolVersion"]) == "holdout-v1")


def test_selector_version_v2() -> None:
  check("selector.v2", schema.selector_version_for("holdout-v2") == "holdout-v2")
  check("selector.v1", schema.selector_version_for("holdout-v1") == "holdout-v1")


def test_deterministic_v2() -> None:
  proto = protocol()
  proto["protocolVersion"] = "holdout-v2"
  pool = selector.build_candidate_pool(inventory(), proto, content_hashes=content_map())["pool"]
  first = selector.select_documents(pool, proto["randomHoldout"], 20260918)
  second = selector.select_documents(pool, proto["randomHoldout"], 20260918)
  check("v2.deterministic", [d["documentId"] for d in first["documents"]] == [d["documentId"] for d in second["documents"]])


def test_recovered_geometry_marker_adapter() -> None:
  lines = [
    {
      "text": "A) um",
      "page": 1,
      "x0": 50.0,
      "top": 100.0,
      "x1": 150.0,
      "bottom": 112.0,
      "lineIndex": 0,
    },
    {
      "text": "B) dois",
      "page": 1,
      "x0": 50.0,
      "top": 130.0,
      "x1": 150.0,
      "bottom": 142.0,
      "lineIndex": 1,
    },
    {
      "text": "(Cc) tres",
      "page": 1,
      "x0": 50.0,
      "top": 160.0,
      "x1": 150.0,
      "bottom": 172.0,
      "lineIndex": 2,
    },
    {
      "text": "D) quatro",
      "page": 1,
      "x0": 50.0,
      "top": 190.0,
      "x1": 150.0,
      "bottom": 202.0,
      "lineIndex": 3,
    },
    {
      "text": "E) cinco",
      "page": 1,
      "x0": 50.0,
      "top": 220.0,
      "x1": 150.0,
      "bottom": 232.0,
      "lineIndex": 4,
    },
  ]

  structure = {
    "recoveredAlternativeMarkerCandidates": [{
      "expectedLabel": "C",
      "label": None,
      "labelSource": "recovered_geometry",
      "page": 1,
      "bbox": [50.0, 160.0, 150.0, 172.0],
      "lineIndex": 2,
      "text": "(Cc) tres",
      "evidence": [
        "sequence_gap",
        "alignment",
        "spatial_cluster",
      ],
    }],
  }

  markers = runner._markers_with_recovered_geometry(
    lines,
    structure,
  )

  recovered = [
    marker
    for marker in markers
    if marker.get("source") == "recovered_geometry"
  ]

  labels = {
    marker.get("label")
    for marker in markers
    if marker.get("markerKind") == "answer_marker"
  }

  check(
    "adapter.recovered_one",
    len(recovered) == 1,
    recovered,
  )

  check(
    "adapter.recovered_label",
    recovered
    and recovered[0]["label"] == "C",
    recovered,
  )

  check(
    "adapter.complete_labels",
    labels == set("ABCDE"),
    labels,
  )

  invalid_structure = {
    "recoveredAlternativeMarkerCandidates": [{
      "expectedLabel": "C",
      "labelSource": "recovered_geometry",
      "page": 1,
      "bbox": [50.0, 160.0, 150.0, 172.0],
      "lineIndex": 2,
      "text": "(Cc) tres",
      "evidence": [
        "sequence_gap",
        "alignment",
      ],
    }],
  }

  invalid_markers = runner._markers_with_recovered_geometry(
    lines,
    invalid_structure,
  )

  check(
    "adapter.requires_full_evidence",
    not any(
      marker.get("source") == "recovered_geometry"
      for marker in invalid_markers
    ),
    invalid_markers,
  )


def selected_set_lines(texts: list[tuple[str, float]]) -> list[dict]:
  return [{"text": text, "page": 1, "x0": 50.0, "x1": 250.0,
           "top": top, "bottom": top + 12.0, "lineIndex": i, "role": "stem"}
          for i, (text, top) in enumerate(texts)]


def selected_set_pipeline(lines: list[dict], structure=None):
  structure = structure or runner.response_structure.discover_response_structure(runner._observed_lines(lines))
  markers = runner._markers_with_recovered_geometry(lines, structure)
  boundary = {"reliable": True, "pages": [1]}
  kwargs = {}
  # The new contract must be supported by the consumer, but RED remains runnable.
  import inspect
  if "selected_response_set" in inspect.signature(runner.regions.discover_response_regions).parameters:
    kwargs["selected_response_set"] = structure.get("selectedResponseSet")
  regions = runner.regions.discover_response_regions(boundary=boundary, lines=lines, words=None,
                                                    strong_markers=markers, **kwargs)
  fusion = runner.fusion.fuse_response_evidence(boundary, structure, {}, regions)
  return structure, markers, regions, fusion


def test_selected_response_set_contract() -> None:
  options = [(f"({label}) alternativa com conteudo", 300.0 + i * 24) for i, label in enumerate("ABCDE")]
  for name, texts, count, labels in [
    ("before", [("(A) falso marcador no enunciado", 40.0)] + options, 5, "A-E"),
    ("after", options[:4] + [("(E) rodape independente", 800.0)], 4, "A-D"),
    ("inline", options[:3] + [("(D) conteudo com (A) referencia interna", 372.0)], 4, "A-D"),
    ("real_ad", options[:4], 4, "A-D"),
    ("real_ae", options, 5, "A-E"),
    ("real_ac_no_clamp", options[:3], 3, "A-C"),
  ]:
    structure, markers, regions, fusion = selected_set_pipeline(selected_set_lines(texts))
    answers = [s for s in regions["responseSlotHypotheses"] if s["role"] == "answer_option"]
    contract = structure.get("selectedResponseSet") or {}
    check(f"selected.{name}.contract", contract.get("clusterId") is not None and not contract.get("ambiguous", True))
    check(f"selected.{name}.slots", len(answers) == count, len(answers))
    check(f"selected.{name}.count_labels", fusion["optionCountHypothesis"] == count and fusion["optionLabelsHypothesis"] == labels, fusion)
    check(f"selected.{name}.no_conflict", not {"count_conflict", "label_conflict"} & set(fusion["blockers"]))
    check(f"selected.{name}.provenance", all(o.get("selectedResponseSetMember") is True
          for s in answers for o in s["markerObservations"] if o["source"] in {"strong", "recovered_geometry"}))
    check(f"selected.{name}.refs", all("text" not in ref and "spanWithinLine" in ref
          for ref in contract.get("candidateRefs", [])) and bool(contract.get("candidateRefs")))

  competing = options + [(f"({label}) outro conjunto legitimo", 650.0 + i * 24) for i, label in enumerate("ABCDE")]
  structure, markers, regions, fusion = selected_set_pipeline(selected_set_lines(competing))
  check("selected.ambiguous.structure", structure["ambiguous"] is True)
  check("selected.ambiguous.not_hidden", len([m for m in markers if m["markerKind"] == "answer_marker"]) == 10)
  check("selected.ambiguous.blocked", fusion["optionCountHypothesis"] is None and "competing_response_sets" in fusion["hardBlockers"])

  # Internal enumeration keeps its role instead of becoming an extra answer.
  texts = [("I) primeiro item interno", 40.0), ("II) segundo item interno", 64.0)] + options
  _, _, regions, fusion = selected_set_pipeline(selected_set_lines(texts))
  check("selected.internal.not_option", len([s for s in regions["responseSlotHypotheses"] if s["role"] == "answer_option"]) == 5)
  check("selected.internal.subitems", any(s["role"] == "subitem" for s in regions["responseSlotHypotheses"]))

  # Existing conservative internal-gap recovery, not a new observation capability.
  gap = options.copy()
  gap[2] = ("corrompido mas alinhado com as alternativas", 348.0)
  lines = selected_set_lines(gap)
  structure, markers, regions, fusion = selected_set_pipeline(lines)
  check("selected.recovered.valid", any(m.get("source") == "recovered_geometry" and m.get("selectedResponseSetMember") for m in markers))
  check("selected.recovered.count", fusion["optionCountHypothesis"] == 5, fusion)
  check("selected.recovered.labels", structure["selectedResponseSet"]["labels"] == list("ABCDE")
        and fusion["optionLabelsHypothesis"] == "A-E")
  import copy
  foreign = copy.deepcopy(structure)
  foreign["recoveredAlternativeMarkerCandidates"][0]["page"] = 2
  _, markers, _, _ = selected_set_pipeline(lines, foreign)
  check("selected.recovered.membership_required", not any(m.get("source") == "recovered_geometry" for m in markers))
  invalid = copy.deepcopy(structure)
  for key in ("recoveredAlternativeMarkerCandidates",):
    for candidate in invalid[key]:
      candidate["evidence"] = ["sequence_gap", "alignment"]
  for candidate in (invalid.get("selectedResponseSet") or {}).get("candidates", []):
    if candidate.get("labelSource") == "recovered_geometry":
      candidate["evidence"] = ["sequence_gap", "alignment"]
  _, markers, _, fusion = selected_set_pipeline(lines, invalid)
  check("selected.recovered.invalid", not any(m.get("source") == "recovered_geometry" for m in markers))

  # Filtering must retain non-answer roles even alongside an authoritative set.
  structure = runner.response_structure.discover_response_structure(runner._observed_lines(selected_set_lines(options)))
  non_answers = selected_set_lines([( "12-A afirmacao com controle", 100.0), ("12-B segunda afirmacao", 124.0)])
  raw = runner.observations.extract_text_markers(non_answers)
  kept = runner._markers_with_recovered_geometry(non_answers, structure)
  check("selected.parent_control.preserved", bool(raw) and [m for m in kept if m["markerKind"] != "answer_marker"] == raw)
  ce = selected_set_lines([( "Julgue os itens como certo ou errado", 40.0),
                           ("12-A primeira afirmacao", 100.0), ("12-B segunda afirmacao", 124.0)])
  structure, _, _, fusion = selected_set_pipeline(ce)
  check("selected.parent_child.not_single", structure["inferredResponseStructure"]["mode"] != "single_choice" and fusion["optionCountHypothesis"] is None)
  structure, _, _, fusion = selected_set_pipeline(selected_set_lines([
    ("(C) afirmacao verdadeira", 300.0), ("(E) afirmacao falsa", 324.0)]))
  check("selected.ce.not_single", structure["inferredResponseStructure"]["mode"] != "single_choice"
        and fusion["optionCountHypothesis"] is None and fusion["optionLabelsHypothesis"] == "CE")
  # C/E controls and parent-child slots survive an authoritative answer filter.
  texts = [("Julgue as afirmacoes e assinale C ou E", 40.0)]
  for i, label in enumerate("ABC"):
    texts.append((f"12-{label} afirmacao com \ue000 \ue001 controles", 100.0 + i * 40))
  texts += options
  structure, _, regions, _ = selected_set_pipeline(selected_set_lines(texts))
  roles = [slot["role"] for slot in regions["responseSlotHypotheses"]]
  check("selected.ce.controls_retained", roles.count("response_control") == 6 and roles.count("subitem") == 3, roles)
  non_answer_roles = [{"markerKind": kind} for kind in ("parent_child", "subitem", "response_control")]
  check("selected.non_answer_roles.unfiltered", runner.response_structure.selected_response_markers(
        non_answer_roles, structure.get("selectedResponseSet")) == non_answer_roles)
  # A leading observation cannot claim membership of a rejected inline ordinal.
  lines = selected_set_lines(options[:3] + [("(D) conteudo com (A) referencia interna", 372.0)])
  structure, markers, regions, fusion = selected_set_pipeline(lines)
  rejected = next(c for c in structure["alternativeMarkerCandidates"] if c["ordinalWithinLine"] == 1)
  forged = {**markers[-1], "label": rejected["label"], "candidateRef": runner.response_structure.response_candidate_ref(rejected)}
  check("selected.identity.inline_rejected", runner.response_structure.selected_response_markers([forged], structure["selectedResponseSet"]) == [])
  # Regions and Fusion independently enforce the contract on stale raw inputs.
  raw_regions = runner.regions.discover_response_regions(boundary={"reliable": True, "pages": [1]},
    lines=lines, words=None, strong_markers=runner.observations.extract_text_markers(lines),
    selected_response_set=structure["selectedResponseSet"])
  check("selected.regions.direct_contract", all(o.get("selectedResponseSetMember") for s in raw_regions["responseSlotHypotheses"]
    if s["role"] == "answer_option" for o in s["markerObservations"]))
  stale = copy.deepcopy(regions)
  stale_slot = copy.deepcopy(stale["responseSlotHypotheses"][-1])
  stale_slot["slotId"] = 99
  stale_slot["label"] = rejected["label"]
  stale_slot["markerObservations"] = [{"source": "strong", "label": rejected["label"],
    "candidateRef": runner.response_structure.response_candidate_ref(rejected)}]
  stale["responseSlotHypotheses"].insert(0, stale_slot)
  fused = runner.fusion.fuse_response_evidence({"reliable": True}, structure, {}, stale)
  check("selected.fusion.direct_contract", fused["optionCountHypothesis"] == 4 and fused["optionLabelsHypothesis"] == "A-D"
        and len(fused["excludedAnswerSlotCandidateRefs"]) == 1, fused)
  merged = copy.deepcopy(regions)
  merged["responseSlotHypotheses"][-1]["markerObservations"] += stale_slot["markerObservations"]
  fused = runner.fusion.fuse_response_evidence({"reliable": True}, structure, {}, merged)
  check("selected.fusion.rejected_merge_excluded", fused["optionCountHypothesis"] == 4
        and "label_conflict" not in fused["blockers"] and len(fused["excludedAnswerSlotCandidateRefs"]) == 1)
  # Missing internal label without a recovery observation is not invented.
  _, markers, _, _ = selected_set_pipeline(selected_set_lines(options[:2] + options[3:]))
  check("selected.missing_label.not_invented", not any(m["label"] == "C" for m in markers))
  check("selected.no_new_recovery_policy", all(m.get("source") != "recovered_geometry" or
        set(m.get("recoveredEvidence", [])) >= {"sequence_gap", "alignment", "spatial_cluster"} for m in markers))


def test_response_set_completeness() -> None:
  def options(labels):
    return [(f"({label}) alternativa observada", 300.0 + i * 24) for i, label in enumerate(labels)]

  cases = [
    ("real_ad", options("ABCD"), "complete", 4, "A-D"),
    ("real_ae", options("ABCDE"), "complete", 5, "A-E"),
    ("real_ac", options("ABC"), "complete", 3, "A-C"),
    ("suffix_cde", options("CDE"), "incomplete", None, "unknown"),
    ("suffix_bcde", options("BCDE"), "incomplete", None, "unknown"),
    ("gap_acde", options("ACDE"), "incomplete", None, "unknown"),
    ("gap_abde", options("ABDE"), "incomplete", None, "unknown"),
    ("terminal_residual", options("ABCD") + [("?? fragmento residual curto", 396.0)], "ambiguous", None, "unknown"),
    ("distant_footer", options("ABCD") + [("rodape distante", 800.0)], "complete", 4, "A-D"),
  ]
  for name, texts, status, count, labels in cases:
    structure, markers, _, fusion = selected_set_pipeline(selected_set_lines(texts))
    completeness = structure.get("responseSetCompleteness") or {}
    check(f"completeness.{name}.status", completeness.get("status") == status, completeness)
    check(f"completeness.{name}.emission", fusion["optionCountHypothesis"] == count and fusion["optionLabelsHypothesis"] == labels, fusion)
    check(f"completeness.{name}.no_invention", all(m.get("source") != "recovered_geometry" for m in markers))
    if status != "complete":
      check(f"completeness.{name}.hard_gate", bool(set(completeness.get("blockers", [])) & set(fusion["hardBlockers"])))
      check(f"completeness.{name}.confidence", fusion["interpretationConfidence"] != "high")

  lines = selected_set_lines(options("ABCD") + [("continuacao textual curta", 396.0)])
  lines[-1]["x0"] = 100.0
  s, _, _, f = selected_set_pipeline(lines)
  check("completeness.unaligned_continuation", (s.get("responseSetCompleteness") or {}).get("status") == "complete"
        and f["optionCountHypothesis"] == 4 and f["optionLabelsHypothesis"] == "A-D")
  for name, mutate in [("other_page", lambda x: x.update(page=2)),
                       ("long_text", lambda x: x.update(text="palavra " * 12))]:
    lines = selected_set_lines(options("ABCD") + [("residual curto", 396.0)])
    mutate(lines[-1])
    s, _, _, f = selected_set_pipeline(lines)
    check(f"completeness.{name}.negative", (s.get("responseSetCompleteness") or {}).get("status") == "complete" and f["optionCountHypothesis"] == 4)

  # Adjacency must work in pixel-scaled observations, not only PDF-size units.
  scaled = selected_set_lines(options("ABCD") + [("residual curto alinhado", 396.0)])
  for line in scaled:
    for key in ("x0", "x1", "top", "bottom"):
      line[key] *= 2.0
  s, _, _, f = selected_set_pipeline(scaled)
  check("completeness.scaled_cadence.ambiguous", (s.get("responseSetCompleteness") or {}).get("status") == "ambiguous"
        and f["optionCountHypothesis"] is None)
  scaled[-1]["top"] = 1100.0
  scaled[-1]["bottom"] = 1124.0
  s, _, _, f = selected_set_pipeline(scaled)
  check("completeness.scaled_cadence.distant_negative", (s.get("responseSetCompleteness") or {}).get("status") == "complete" and f["optionCountHypothesis"] == 4)

  # Operator spacing is not additional prose; use a general residual-size guard.
  s, markers, _, f = selected_set_pipeline(selected_set_lines(options("ABCD") + [
    ("?? x < 1 + y > 2 = z", 396.0)]))
  check("completeness.operator_spacing.residual", (s.get("responseSetCompleteness") or {}).get("status") == "ambiguous"
        and f["optionCountHypothesis"] is None and not any(m["label"] == "E" for m in markers))

  gap = selected_set_lines(options("ABCDE"))
  gap[1]["text"] = "conteudo alinhado sem marcador legivel"
  s, markers, _, f = selected_set_pipeline(gap)
  check("completeness.recovered_gap.complete", (s.get("responseSetCompleteness") or {}).get("status") == "complete"
        and f["optionCountHypothesis"] == 5 and f["optionLabelsHypothesis"] == "A-E")
  check("completeness.recovered_gap.old_evidence", any(m.get("source") == "recovered_geometry" and
        set(m.get("recoveredEvidence", [])) >= {"sequence_gap", "alignment", "spatial_cluster"} for m in markers))

  # Rejected A may diagnose fragmentation, never supply a response slot/label.
  s, markers, _, f = selected_set_pipeline(selected_set_lines(
    [("(A) candidato isolado", 40.0)] + options("CDE")))
  check("completeness.rejected_prefix.not_reintroduced", not any(m["label"] == "A" for m in markers)
        and f["optionCountHypothesis"] is None and f["optionLabelsHypothesis"] == "unknown")

  for name, texts in [
    ("ce", [("julgue os itens como certo ou errado", 40.0)] + options("CE")),
    ("parent_child", [("julgue os itens como certo ou errado", 40.0), ("12-A afirmacao", 100.0), ("12-B afirmacao", 124.0)]),
    ("numeric", [("Resposta: valor solicitado", 100.0)]),
    ("discursive", [("Justifique sua resposta", 100.0)]),
    ("internal", [("I) primeiro item", 100.0), ("II) segundo item", 124.0)]),
    ("unknown", [("texto sem estrutura de resposta", 100.0)]),
  ]:
    s, _, _, f = selected_set_pipeline(selected_set_lines(texts))
    c = s.get("responseSetCompleteness") or {}
    check(f"completeness.{name}.exempt", c.get("requiredForOptionEmission") is False and c.get("status") != "incomplete"
          and not {"response_set_incomplete", "response_set_completeness_uncertain"} & set(f["hardBlockers"]))

  # No cross-page stitching: a selected A-B fragment remains non-emitting.
  lines = selected_set_lines(options("AB") + [(f"({label}) continuacao", 60.0 + i * 24) for i, label in enumerate("CDE")])
  for line in lines[2:]:
    line["page"] = 2
  s, markers, _, f = selected_set_pipeline(lines)
  c = s.get("responseSetCompleteness") or {}
  check("completeness.multipage.conservative", c.get("status") in {"incomplete", "ambiguous", "unknown"}
        and bool(c) and f["optionCountHypothesis"] is None)
  check("completeness.multipage.no_stitching", len({m["page"] for m in markers}) == 1)

  # A high-confidence independent observation cannot override a closure gate.
  import copy
  s, _, r, _ = selected_set_pipeline(selected_set_lines(options("ABCDE")))
  for slot in r["responseSlotHypotheses"]:
    slot["confidence"] = "high"
    slot["markerObservations"].append({"source": "visual", "visualIndex": slot["slotId"]})
  visual = {"visualAlternativeEvidence": [{"confidence": "high"}] * 5}
  for status in ("incomplete", "ambiguous", "unknown"):
    blocked = copy.deepcopy(s)
    blocked["responseSetCompleteness"] = {"status": status, "requiredForOptionEmission": True,
                                         "selectedLabels": list("ABCDE"), "evidence": [], "blockers": []}
    f = runner.fusion.fuse_response_evidence({"reliable": True}, blocked, visual, r)
    check(f"completeness.fusion.{status}.status_not_confidence", f["optionCountHypothesis"] is None
          and f["optionLabelsHypothesis"] == "unknown" and f["interpretationConfidence"] != "high")
  del s["responseSetCompleteness"]
  f = runner.fusion.fuse_response_evidence({"reliable": True}, s, visual, r)
  check("completeness.fusion.missing_contract.fail_closed", f["optionCountHypothesis"] is None
        and f["responseSetCompleteness"]["status"] == "unknown")


def test_marker_role_and_spacing() -> None:
  structure_api = runner.response_structure
  # A-G: grammar and exact offsets/body, without fuzzy parsing.
  for name, prefix, label, case in [
    ("compact_upper", "(A)", "A", "upper"), ("spaced_upper", "( A )", "A", "upper"),
    ("spaced_lower", "( a )", "A", "lower"), ("many_spaces", "(  b  )", "B", "lower"),
    ("tab", "(\tc\t)", "C", "lower"), ("nbsp", "(\u00a0D\u00a0)", "D", "upper"),
  ]:
    raw = "  " + prefix + "  corpo  com   espacos"
    parsed = structure_api.parse_marker(raw) or {}
    check(f"spacing.parse.{name}.descriptor", parsed.get("label") == label
          and parsed.get("labelCase") == case and parsed.get("markerShape") == "parentheses"
          and parsed.get("markerKind") == "answer_marker", parsed)
    check(f"spacing.parse.{name}.offset_body", parsed.get("spanStart") == 2
          and parsed.get("spanEnd") == 2 + len(prefix) + 2
          and parsed.get("textStart") == 2 + len(prefix) + 2
          and parsed.get("text") == "corpo  com   espacos", parsed)
  for raw in ("( palavra )", "(12)", "( 12 )", "(AB)", "( AB )", "(x)", "( x )", "A"):
    check(f"spacing.reject.{raw}", structure_api.parse_marker(raw) is None)
  prefixes = [f"({left}{label}{right})" for label in "ABCDEabcde"
              for left, right in (("", ""), (" ", " "), ("  ", "\t"))]
  check("spacing.strong_parser_consistent", all(structure_api.STRONG_MARKER_RE.fullmatch(prefix)
        and structure_api.parse_marker(prefix + " corpo") for prefix in prefixes))

  def options(labels="abcde", spaced=True, top=300):
    return [(f"( {label} ) alternativa com conteudo" if spaced else f"({label}) alternativa com conteudo",
             top + i * 24.0) for i, label in enumerate(labels)]

  # H-K, T/U: all-lower is a style, not a role; instruction may follow options.
  for name, labels, spaced in [("upper", "ABCDE", True), ("lower", "abcde", True),
                               ("lower_compact", "abcde", False), ("real_ad", "ABCD", False),
                               ("real_ae", "ABCDE", False)]:
    lines = selected_set_lines(options(labels, spaced) + [("Assinale a opcao correta", 450.0)])
    s, _, r, f = selected_set_pipeline(lines)
    selected = s.get("selectedResponseSet") or {}
    slots = r["responseSlotHypotheses"]
    members = [slot for slot in slots if any(o.get("selectedResponseSetMember") is True
               for o in slot["markerObservations"])]
    check(f"spacing.set.{name}.authoritative", structure_api.response_set_authoritative(selected)
          and selected.get("labels") == list(labels.upper()))
    check(f"spacing.set.{name}.single_choice", s["inferredResponseStructure"]["mode"] == "single_choice")
    check(f"spacing.set.{name}.member_roles", len(members) == len(labels)
          and all(slot["role"] == "answer_option" for slot in members), slots)
    check(f"spacing.set.{name}.role_evidence", bool(members) and all(
          "selected_response_set_member" in slot["evidence"] for slot in members))
    check(f"spacing.set.{name}.count", f["optionCountHypothesis"] == len(labels)
          and f["optionLabelsHypothesis"] == "A-" + labels[-1].upper(), f)

  # L-N: non-selected lowercase and Roman runs remain internal, without case-only selection.
  for name, internal in [
    ("lower_upper", [(f"{label}) afirmacao interna", 40.0 + i * 24) for i, label in enumerate("abc")]),
    ("lower_lower", [(f"{label}) afirmacao interna", 40.0 + i * 24) for i, label in enumerate("abc")]),
    ("roman", [(f"{label}. condicao interna", 40.0 + i * 24) for i, label in enumerate(["I", "II", "III"])]),
  ]:
    labels = "ABCDE" if name == "lower_upper" else "abcde"
    s, _, r, f = selected_set_pipeline(selected_set_lines(internal + [("Escolha a opcao correta", 150.0)]
                                                       + options(labels)))
    slots = r["responseSlotHypotheses"]
    check(f"spacing.internal.{name}.roles", sum(slot["role"] == "subitem" for slot in slots) == 3
          and sum(slot["role"] == "answer_option" for slot in slots) == 5, slots)
    check(f"spacing.internal.{name}.pattern", r["questionResponsePattern"]["pattern"] == "internal_enumeration_then_options")
    check(f"spacing.internal.{name}.count", f["optionCountHypothesis"] == 5)
    if name != "roman":
      check(f"spacing.internal.{name}.structure", len(s["internalEnumerationCandidates"]) == 1)

  # O-Q: incompatible roles and CE must not become single-choice members.
  controls = [("Julgue as afirmacoes e assinale C ou E", 20.0)]
  controls += [(f"15-{label} afirmacao com \ue000 \ue001 controles", 60.0 + i * 40) for i, label in enumerate("ABC")]
  _, _, r, _ = selected_set_pipeline(selected_set_lines(controls + options()))
  roles = [slot["role"] for slot in r["responseSlotHypotheses"]]
  check("spacing.parent_child_controls", roles.count("subitem") == 3 and roles.count("response_control") == 6)
  s, _, _, f = selected_set_pipeline(selected_set_lines([("( C ) certo", 300.0), ("( E ) errado", 324.0)]))
  check("spacing.ce_preserved", s["inferredResponseStructure"]["mode"] != "single_choice"
        and f["optionCountHypothesis"] is None and f["optionLabelsHypothesis"] == "CE")
  s, _, r, _ = selected_set_pipeline(selected_set_lines([(f"{label}( )", 300.0 + i * 24) for i, label in enumerate("ABCDE")]))
  check("spacing.response_fields_preserved", all(slot["role"] == "response_field" for slot in r["responseSlotHypotheses"])
        and len(r["responseSlotHypotheses"]) == 5)

  # R: parentheses do not remove a genuine competitor; original safety selection.
  s, markers, _, f = selected_set_pipeline(selected_set_lines(options(top=100) + options(top=650)))
  check("spacing.competing.ambiguous", s["ambiguous"] is True
        and not structure_api.response_set_authoritative(s.get("selectedResponseSet")))
  check("spacing.competing.retained", len(markers) == 10)
  check("spacing.competing.blocked", f["optionCountHypothesis"] is None
        and "competing_response_sets" in f["hardBlockers"])

  # S: short weak geometry may remain diagnostic, never expands a selected set.
  weak_lines = [("12", 40.0), ("17", 64.0), ("21", 88.0)]
  s, _, r, f = selected_set_pipeline(selected_set_lines(weak_lines + options()))
  check("spacing.weak.no_extra_slots", len(r["responseSlotHypotheses"]) == 5
        and f["optionCountHypothesis"] == 5 and "weak_anchor_only" not in f["blockers"])

  # V: spacing/role precedence cannot bypass the Patch02 closure gate.
  s, _, _, f = selected_set_pipeline(selected_set_lines(options("acde") ))
  check("spacing.completeness.gap", s["responseSetCompleteness"]["status"] == "incomplete"
        and f["optionCountHypothesis"] is None and "response_set_incomplete" in f["hardBlockers"])

  # W: same-line scanning materializes every detected strong spaced prefix.
  raw = "( a ) um  texto ( B ) dois (  c  ) tres (d) quatro ( e ) cinco"
  candidates = structure_api.extract_candidates(runner._observed_lines(selected_set_lines([(raw, 300.0)])))
  check("spacing.same_line.labels", [c.label for c in candidates] == list("ABCDE"))
  check("spacing.same_line.ordinal_body", [c.ordinal_within_line for c in candidates] == list(range(5))
        and [c.text for c in candidates] == ["um  texto", "dois", "tres", "quatro", "cinco"])
  check("spacing.same_line.spans", all(c.span[1] - c.span[0] >= len(c.text) for c in candidates)
        and len(candidates) == 5)


def test_visual_response_set_fallback() -> None:
  from unittest.mock import patch
  from PIL import Image, ImageDraw
  import audit_visual_marker_evidence_selftest as fixtures

  def image_at(points):
    image = Image.new('L', (500, 500), 255)
    draw = ImageDraw.Draw(image)
    for x, y in points:
      fixtures.draw_ring(draw, x, y, 30)
    return image

  five = [(45, 120 + i * 55) for i in range(5)]
  contents = [('Some substantial content for this response', 108 + i * 55, 70) for i in range(5)]

  def run(points=five, texts=contents, limits=None, native=False, reliable=True, failure=False, raw_only=False,
          line_right=340, missing=False):
    with tempfile.TemporaryDirectory() as temporary:
      directory = Path(temporary)
      image = image_at(points)
      if raw_only:
        ImageDraw.Draw(image).rectangle((75, 108, 300, 125), fill=0)
      image.save(directory / 'page-01.png')
      scale = 160 / 72 if native else 1
      lines = [runner.observations.ObservedLine(1, text, (x / scale, y / scale, line_right / scale, (y + 20) / scale),
                line_index=i, source='native_pdf' if native else 'ocr_cache') for i, (text, y, x) in enumerate(texts)]
      bundle = runner.observations.ObservationBundle([], lines, [], {}, 'native_pdf' if native else 'ocr_cache')
      boundary = dict(reliable=reliable, pages=[1], pageLimits={1: limits or dict(top=0, bottom=500 / scale)})
      bundle = runner.question_boundary.filter_bundle(bundle, boundary)
      captured = {}
      original = runner.fusion.fuse_response_evidence
      def fuse(b, s, v, r):
        captured.update(visual=v, regions=r, structure=s)
        return original(b, s, v, r)
      render = dict(path=str(directory / ('missing.png' if missing else 'page-01.png')), scale=scale)
      with patch.object(runner.fusion, 'fuse_response_evidence', side_effect=fuse), patch.object(
          runner.observations, 'render_pdf_page', side_effect=OSError('unavailable') if failure else None,
          return_value=render) as render_mock:
        try:
          kwargs = dict(native_pdf=directory / 'canonical.pdf', native_render_cache=directory) if native else {}
          result = runner._run_from_bundle(bundle, boundary, None if native else directory, [1], **kwargs)
        except TypeError as error:
          check('visual.native.contract', False, str(error))
          return {}, {}, {}, render_mock.call_count
      return result, captured.get('visual', {}), captured.get('regions', {}), render_mock.call_count

  f, v, r, _ = run()
  hypotheses = v.get('visualResponseSetHypotheses', [])
  check('visual.A.unique_support', len(hypotheses) == 1 and hypotheses[0]['support'] == 5)
  check('visual.A.adjacent_content', bool(hypotheses) and hypotheses[0]['adjacentContentEvidence'] == 1)
  check('visual.B.count_regions', f.get('optionCountHypothesis') == 5 and all(
        s['contentRegionId'] is not None for s in r.get('responseSlotHypotheses', [])))
  check('visual.C.no_labels_by_order', f.get('optionLabelsHypothesis') == 'unknown'
        and all(s['label'] is None for s in f.get('slots', [])))
  check('visual.U.propagated', 'visualResponseSetHypotheses' in v and 'visualResponseSetAmbiguous' in v)
  check('visual.provenance.raster', v.get('visualObservationSource') == 'raster_cache')
  for name, points in [('D.one', five[:1]), ('E.two', five[:2]),
                       ('I.scatter', [(40 + i * 65, 120 + i * 55) for i in range(5)])]:
    f, v, r, _ = run(points)
    check('visual.' + name + '.no_hypothesis', v.get('visualResponseSetHypotheses') == [])
    check('visual.' + name + '.no_active', v.get('activeVisualMarkerIndexes') == [])
    check('visual.' + name + '.no_count', f.get('optionCountHypothesis') is None)
  f, v, r, _ = run(five + [(180, y) for _, y in five])
  check('visual.F.ambiguous', v.get('visualResponseSetAmbiguous') is True)
  check('visual.F.no_active', v.get('activeVisualMarkerIndexes') == [])
  check('visual.V.existing_gate', f.get('optionCountHypothesis') is None and 'competing_response_sets' in f.get('blockers', []))
  check('visual.F.no_answer_slots', not any(s['role'] == 'answer_option' for s in r.get('responseSlotHypotheses', [])))
  # Isolated candidate precedes the selected set: refs must retain raw indexes.
  f, v, r, _ = run([(350, 45)] + five)
  check('visual.G.raw_retained', len(v.get('visualAlternativeEvidence', [])) == 6)
  check('visual.G.selected_only', len(r.get('responseSlotHypotheses', [])) == 5 and f.get('optionCountHypothesis') == 5)
  check('visual.G.raw_index_refs', [s['visualEvidenceRefs'] for s in f.get('slots', [])] == [[i] for i in range(1, 6)])
  f, v, r, _ = run(texts=[])
  check('visual.H.missing_region_gate', f.get('optionCountHypothesis') is None
        and 'visual_only_content_region_missing' in f.get('blockers', []))
  for labels, name in [('ABCD', 'J'), ('ABCDE', 'K')]:
    text = [(f'({label}) substantial content for response', 108 + i * 55, 30) for i, label in enumerate(labels)]
    f, v, r, _ = run(five + [(180, y) for _, y in five] + [(350, 45)], texts=text)
    check('visual.' + name + '.text_authority', f.get('optionCountHypothesis') == len(labels)
          and f.get('optionLabelsHypothesis') == 'A-' + labels[-1])
  ce_text = [('Assinale C ou E para cada item', 10, 20)] + [
    (f'12 - {letter} substantial statement', 108 + i * 55, 10) for i, letter in enumerate('ABC')]
  f, v, r, _ = run([(x, 120 + i * 55) for i in range(3) for x in [250, 310]], texts=ce_text)
  check('visual.L.controls_not_options', f.get('optionCountHypothesis') is None
        and not any(s['role'] == 'answer_option' for s in f.get('slots', [])))
  f, v, r, _ = run(texts=[('I. first internal statement', 10, 20), ('II. second internal statement', 40, 20)] + contents)
  check('visual.M.internal_preserved', sum(s['role'] == 'subitem' for s in f.get('slots', [])) == 2)
  check('visual.M.visual_set', f.get('optionCountHypothesis') == 5)
  f, v, r, _ = run(five + [(45, 430)], limits=dict(top=100, bottom=370))
  check('visual.N.vertical_crop', len(v.get('visualAlternativeEvidence', [])) == 5)
  check('visual.N.selected_count', f.get('optionCountHypothesis') == 5)
  check('visual.N.actual_crop', (v.get('visualPageGeometry') or [{}])[0].get('cropPixels') == [0, 100, 500, 370])
  f, v, r, _ = run(five + [(300, y) for _, y in five], limits=dict(top=100, bottom=370, x0=0, x1=200), line_right=190)
  check('visual.O.column_crop', len(v.get('visualAlternativeEvidence', [])) == 5 and f.get('optionCountHypothesis') == 5)
  check('visual.O.actual_crop', (v.get('visualPageGeometry') or [{}])[0].get('cropPixels') == [0, 100, 200, 370])
  f, v, r, calls = run(native=True)
  check('visual.S.native_fallback', calls == 1 and v.get('nativeVisualFallbackTriggered') is True)
  check('visual.P.native_count', f.get('optionCountHypothesis') == 5)
  evidence = v.get('visualAlternativeEvidence', [])
  check('visual.P.roundtrip', len(evidence) == 5 and all(abs(a - b) <= 0.01
        for a, b in zip(evidence[0]['bbox'], [30 / (160 / 72), 105 / (160 / 72), 61 / (160 / 72), 136 / (160 / 72)])))
  check('visual.P.native_source', v.get('visualObservationSource') == 'native_render')
  f, v, r, _ = run(five + [(81, y) for _, y in five], native=True)
  check('visual.P.scale_cluster_separation', len(v.get('visualResponseSetHypotheses', [])) == 2
        and v.get('activeVisualMarkerIndexes') == [] and f.get('optionCountHypothesis') is None)
  f, v, r, calls = run(native=True, reliable=False)
  check('visual.Q.unreliable_no_render', calls == 0 and f.get('optionCountHypothesis') is None)
  check('visual.Q.not_triggered', v.get('nativeVisualFallbackTriggered') is False)
  f, v, r, calls = run(native=True, texts=[(f'({label}) substantial response content', 108 + i * 55, 30) for i, label in enumerate('ABCDE')])
  check('visual.R.text_first_no_render', calls == 0 and f.get('optionCountHypothesis') == 5)
  check('visual.R.not_triggered', v.get('nativeVisualFallbackTriggered') is False)
  f, v, r, calls = run(native=True, failure=True)
  check('visual.T.failure_safe', calls == 1 and f.get('optionCountHypothesis') is None)
  f, v, r, calls = run(native=True, missing=True)
  check('visual.T.missing_safe', calls == 1 and f.get('optionCountHypothesis') is None
        and not v.get('activeVisualMarkerIndexes'))
  f, v, r, _ = run(points=[], texts=[], raw_only=True)
  check('visual.W.raw_not_marker', not f.get('slots') and f.get('optionCountHypothesis') is None)


def test_reconstructed_terminal_closure() -> None:
  import copy

  def options(labels, rebuilt=()):
    lines = selected_set_lines([(f"({label}) resposta observada", 300.0 + i * 24)
                                for i, label in enumerate(labels)])
    for line, label in zip(lines, labels):
      line["source"] = "reconstructed_from_words" if label in rebuilt else "native_pdf"
    return lines

  for labels in ("ABC", "ABCD", "ABCDE"):
    for rebuilt in (False, True):
      name = f"closure.{'rebuilt' if rebuilt else 'original'}.{labels}"
      lines = options(labels, labels if rebuilt else ())
      observed = runner._observed_lines(lines)
      s, _, _, f = selected_set_pipeline(lines)
      complete = not rebuilt or labels == "ABCDE"
      c = s["responseSetCompleteness"]
      check(name + ".adapter", all(l.is_reconstructed == rebuilt for l in observed))
      check(name + ".candidates", all(("reconstructed_from_words" in m["evidence"]) == rebuilt
            for m in s["alternativeMarkerCandidates"]))
      check(name + ".clusters", all(("reconstructed_from_words" in m["evidence"]) == rebuilt
            for cluster in s["responseSetCandidates"] for m in cluster["candidates"]))
      check(name + ".selected", all(("reconstructed_from_words" in m["evidence"]) == rebuilt
            for m in s["selectedResponseSet"]["candidates"]))
      check(name + ".completeness", c["status"] == "complete" if complete else c["status"] in {"unknown", "ambiguous"}, c)
      check(name + ".count_labels", f["optionCountHypothesis"] == (len(labels) if complete else None)
            and f["optionLabelsHypothesis"] == ("A-" + labels[-1] if complete else "unknown"))
      check(name + ".provenance_evidence", ("reconstructed_from_words" in c["evidence"]) == rebuilt)
      check(name + ".stable_identity", all("text" not in ref for ref in s["selectedResponseSet"]["candidateRefs"]))
  for rebuilt in ("C", "A"):
    s, _, _, f = selected_set_pipeline(options("ABC", rebuilt))
    check("closure.mixed." + rebuilt, s["responseSetCompleteness"]["status"] in {"unknown", "ambiguous"}
          and f["optionCountHypothesis"] is None and f["optionLabelsHypothesis"] == "unknown")
  lines = options("ABC", "ABC") + selected_set_lines([("?? fragmento residual", 372.0)])
  lines[-1]["lineIndex"] = 3
  s, _, _, f = selected_set_pipeline(lines)
  check("closure.residual", s["responseSetCompleteness"]["status"] == "ambiguous" and f["optionCountHypothesis"] is None)
  lines = options("ABCDE", "ABCDE")
  lines[1]["text"] = "conteudo alinhado sem marcador legivel"
  s, markers, _, f = selected_set_pipeline(lines)
  check("closure.internal_gap", s["responseSetCompleteness"]["status"] == "complete" and f["optionCountHypothesis"] == 5
        and any(m.get("source") == "recovered_geometry" for m in markers))
  recovered = next(m for m in s["selectedResponseSet"]["candidates"] if m.get("labelSource") == "recovered_geometry")
  check("closure.internal_gap.provenance", "reconstructed_from_words" in recovered["evidence"])
  for name, texts in [
    ("ce", [("julgue os itens como certo ou errado", 260.0), ("(C) verdadeiro", 300.0), ("(E) falso", 324.0)]),
    ("parent_child", [("julgue os itens como certo ou errado", 260.0), ("12-A afirmacao", 300.0), ("12-B afirmacao", 324.0)])]:
    lines = selected_set_lines(texts)
    for line in lines: line["source"] = "reconstructed_from_words"
    s, _, _, f = selected_set_pipeline(lines)
    check("closure." + name, s["responseSetCompleteness"]["requiredForOptionEmission"] is False and f["optionCountHypothesis"] is None)
  lines = selected_set_lines([("(A) rejeitado no enunciado", 40.0)]) + options("ABCDE", "ABCDE")
  for i, line in enumerate(lines): line["lineIndex"] = i
  s, markers, r, f = selected_set_pipeline(lines)
  check("closure.selected_rejected", len(markers) == 5 and f["optionCountHypothesis"] == 5
        and not any(o["lineIndex"] == 0 for slot in r["responseSlotHypotheses"] if slot["role"] == "answer_option" for o in slot["markerObservations"]))
  # Visual-only count has no textual selected set and no textual closure gate.
  _, _, r, _ = selected_set_pipeline(options("ABCDE"))
  r = copy.deepcopy(r)
  for slot in r["responseSlotHypotheses"]:
    slot["label"] = None
    slot["markerObservations"] = [{"source": "visual", "visualIndex": slot["slotId"]}]
  f = runner.fusion.fuse_response_evidence({"reliable": True}, {},
      {"visualAlternativeEvidence": [{"confidence": "high"}] * 5}, r)
  check("closure.visual_only", f["optionCountHypothesis"] == 5 and f["optionLabelsHypothesis"] == "unknown")


def main() -> None:
  test_reconstructed_terminal_closure()
  test_visual_response_set_fallback()
  test_marker_role_and_spacing()
  test_response_set_completeness()
  test_selected_response_set_contract()
  test_recovered_geometry_marker_adapter()
  test_deterministic_and_quotas()
  test_pool_filters()
  test_same_content_dedup_and_canonical()
  test_same_filename_different_content()
  test_development_excluded_by_content()
  test_overlap_guard()
  test_reserved_unique_and_order_independent()
  test_candidate_pool_hash_order_independent()
  test_bindings_index_and_gt()
  test_runner_question_index_hash()
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
  test_metadata_eligibility()
  test_v1_fingerprint_exclusion()
  test_answer_key_role_exclusion()
  test_v2_quota_abort_low()
  test_v2_quota_abort_hybrid()
  test_invalid_metadata_null_year()
  test_provenance_not_recomputed()
  test_selector_version_v2()
  test_deterministic_v2()
  if FAILURES:
    print(f"\n{len(FAILURES)} checks falharam: {FAILURES}")
    raise SystemExit(1)
  print("\nTodos os checks de endurecimento do holdout passaram.")


if __name__ == "__main__":
  main()
