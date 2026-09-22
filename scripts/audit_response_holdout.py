from __future__ import annotations

import argparse
import datetime as _dt
import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

import audit_holdout_schema as schema
import audit_observations as observations
import audit_question_boundary as question_boundary
import audit_response_fusion as fusion
import audit_response_regions as regions
import audit_response_structure as response_structure
import audit_visual_marker_evidence as visual_evidence

ROOT = Path(__file__).resolve().parents[1]
OCR_DIR = ROOT / "outputs" / "audit" / "ocr"
REPORT_DIR = ROOT / "outputs" / "audit" / "holdout"
MIN_SLICE_N = 20


def labels_to_set(value: Any) -> set[str] | None:
  if not value or value == "unknown":
    return None
  letters: set[str] = set()
  text = str(value).upper()
  if "-" in text and text[0] == "A" and len(text) >= 3:
    start = ord("A")
    end = ord(text[-1])
    letters = {chr(code) for code in range(start, end + 1)}
    return letters
  for char in text:
    if char in "ABCDE":
      letters.add(char)
  return letters or None


def classify_question(gt: dict[str, Any], fusion_result: dict[str, Any], executable: bool = True) -> dict[str, Any]:
  count = gt.get("optionCount")
  gt_labels = {str(label).upper() for label in (gt.get("optionLabels") or [])}
  count_applicable = count is not None
  labels_applicable = bool(gt_labels)
  hyp_count = fusion_result.get("optionCountHypothesis")
  hyp_labels = labels_to_set(fusion_result.get("optionLabelsHypothesis"))
  count_emitted = hyp_count is not None
  labels_emitted = hyp_labels is not None
  interpretation = str(fusion_result.get("interpretationConfidence") or "low")

  if not executable:
    return {"classification": "not_executable", "countErrorDirection": None, "unsafeCertainty": False,
            "countApplicable": count_applicable, "countEmitted": count_emitted, "countCorrect": None,
            "labelsApplicable": labels_applicable, "labelsEmitted": labels_emitted, "labelsCorrect": None,
            "hasUsable": False, "conflict": fusion_result.get("agreement") == "conflict"}

  unsafe = False
  direction: str | None = None
  if count_applicable:
    if count_emitted and hyp_count != count:
      unsafe = True
      direction = "under" if hyp_count < count else "over"
  elif count_emitted:
    unsafe = True
    direction = "over"
  if labels_applicable:
    if labels_emitted and hyp_labels != gt_labels:
      unsafe = True
  elif labels_emitted:
    unsafe = True

  count_ok = (not count_applicable) or (count_emitted and hyp_count == count)
  count_cov = (not count_applicable) or count_emitted
  labels_ok = (not labels_applicable) or (labels_emitted and hyp_labels == gt_labels)
  labels_cov = (not labels_applicable) or labels_emitted

  if unsafe:
    classification = "unsafe_error"
  elif not count_applicable and not labels_applicable:
    classification = "not_applicable"
  elif count_ok and count_cov and labels_ok and labels_cov:
    classification = "correct"
  elif (count_applicable and count_ok and count_cov) or (labels_applicable and labels_ok and labels_cov):
    classification = "partial"
  else:
    classification = "safe_abstention"

  has_usable = bool(
    fusion_result.get("optionCountHypothesis") is not None
    or hyp_labels is not None
    or (fusion_result.get("agreement") in {"strong", "partial"})
    or (fusion_result.get("slots") and any(slot.get("role") in {"answer_option", "subitem", "response_control"} for slot in fusion_result["slots"]))
  )
  return {
    "classification": classification,
    "countErrorDirection": direction,
    "unsafeCertainty": bool(unsafe and interpretation in {"medium", "high"}),
    "unsafeConfidence": interpretation if unsafe else None,
    "countApplicable": count_applicable,
    "countEmitted": count_emitted,
    "countCorrect": (count_emitted and hyp_count == count) if count_applicable else None,
    "labelsApplicable": labels_applicable,
    "labelsEmitted": labels_emitted,
    "labelsCorrect": (labels_emitted and hyp_labels == gt_labels) if labels_applicable else None,
    "hasUsable": has_usable,
    "conflict": fusion_result.get("agreement") == "conflict",
  }


def compute_metrics(records: list[dict[str, Any]]) -> dict[str, Any]:
  total = len(records)
  classes = Counter(record["classification"] for record in records)
  count_applicable = [record for record in records if record["countApplicable"] and record["classification"] != "not_executable"]
  count_emitted = [record for record in count_applicable if record["countEmitted"]]
  count_correct = [record for record in count_emitted if record["countCorrect"]]
  labels_applicable = [record for record in records if record["labelsApplicable"] and record["classification"] != "not_executable"]
  labels_emitted = [record for record in labels_applicable if record["labelsEmitted"]]
  labels_correct = [record for record in labels_emitted if record["labelsCorrect"]]
  emitted_questions = [
    record for record in records
    if ((record["countApplicable"] and record["countEmitted"]) or (record["labelsApplicable"] and record["labelsEmitted"]))
    and record["classification"] != "not_executable"
  ]
  emitted_without_unsafe = [record for record in emitted_questions if record["classification"] != "unsafe_error"]
  conflicts = [record for record in records if record["conflict"]]
  fake_conflicts = [record for record in conflicts if record.get("unambiguousGroundTruth")]
  unsafe = [record for record in records if record["classification"] == "unsafe_error"]
  executable = [record for record in records if record["classification"] != "not_executable"]

  def rate(numerator: int, denominator: int) -> float | None:
    return round(numerator / denominator, 4) if denominator else None

  return {
    "questions": total,
    "executable": len(executable),
    "classes": {name: classes.get(name, 0) for name in schema.QUESTION_CLASSES},
    "coverage": rate(len([r for r in executable if r["hasUsable"]]), len(executable)),
    "abstention": rate(classes.get("safe_abstention", 0), len(executable)),
    "questionLevelEmittedPrecision": rate(len(emitted_without_unsafe), len(emitted_questions)),
    "optionCount": {
      "applicable": len(count_applicable),
      "emitted": len(count_emitted),
      "correct": len(count_correct),
      "precision": rate(len(count_correct), len(count_emitted)),
      "coverage": rate(len(count_emitted), len(count_applicable)),
      "abstention": rate(len(count_applicable) - len(count_emitted), len(count_applicable)),
      "undercount": len([r for r in unsafe if r.get("countErrorDirection") == "under"]),
      "overcount": len([r for r in unsafe if r.get("countErrorDirection") == "over"]),
    },
    "optionLabels": {
      "applicable": len(labels_applicable),
      "emitted": len(labels_emitted),
      "correct": len(labels_correct),
      "precision": rate(len(labels_correct), len(labels_emitted)),
      "coverage": rate(len(labels_emitted), len(labels_applicable)),
    },
    "unsafeError": len(unsafe),
    "unsafeErrorLowConfidence": len([r for r in unsafe if not r["unsafeCertainty"]]),
    "unsafeErrorMediumHighConfidence": len([r for r in unsafe if r["unsafeCertainty"]]),
    "falseConflictRate": rate(len(fake_conflicts), len(conflicts)),
    "conflicts": len(conflicts),
  }


def document_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
  by_document: dict[str, list[dict[str, Any]]] = {}
  for record in records:
    by_document.setdefault(record["documentId"], []).append(record)
  summary: dict[str, Any] = {}
  documents_without_unsafe = 0
  for document_id, items in sorted(by_document.items()):
    classes = Counter(item["classification"] for item in items)
    has_unsafe = classes.get("unsafe_error", 0) > 0
    if not has_unsafe:
      documents_without_unsafe += 1
    summary[document_id] = {
      "questionsEvaluated": len(items),
      "correct": classes.get("correct", 0),
      "partial": classes.get("partial", 0),
      "safeAbstention": classes.get("safe_abstention", 0),
      "unsafeError": classes.get("unsafe_error", 0),
      "notExecutable": classes.get("not_executable", 0),
      "documentHasUnsafeError": has_unsafe,
    }
  return {
    "documents": summary,
    "documentsWithoutUnsafeErrorRatio": round(documents_without_unsafe / len(by_document), 4) if by_document else None,
  }


def compute_slices(records: list[dict[str, Any]]) -> dict[str, Any]:
  axes = ("sourceType", "family", "era", "responseMode", "layout", "markerStyle", "contentKind", "origins")
  slices: dict[str, Any] = {}
  for axis in axes:
    buckets: dict[str, list[dict[str, Any]]] = {}
    for record in records:
      value = record.get(axis)
      if isinstance(value, list):
        value = "+".join(value) if value else "none"
      buckets.setdefault(str(value), []).append(record)
    slices[axis] = {
      key: {
        "n": len(items),
        "descriptiveOnly": len(items) < MIN_SLICE_N,
        "unsafeError": len([i for i in items if i["classification"] == "unsafe_error"]),
        "correct": len([i for i in items if i["classification"] == "correct"]),
        "safeAbstention": len([i for i in items if i["classification"] == "safe_abstention"]),
      }
      for key, items in sorted(buckets.items())
    }
  return slices


def _commit() -> str | None:
  try:
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT), capture_output=True, text=True, timeout=10)
    return result.stdout.strip() or None
  except Exception:
    return None


def verify_document_fingerprint(document: dict[str, Any], fingerprint_fn: Any = None) -> str | None:
  expected = document.get("contentFingerprint")
  if not expected:
    return "missing_manifest_fingerprint"
  path = document.get("canonicalPath")
  try:
    actual = fingerprint_fn(path) if fingerprint_fn else schema.content_fingerprint_file(path)
  except OSError:
    return "source_unreadable"
  if actual != expected:
    return "source_fingerprint_mismatch"
  return None


def _not_executable_classification() -> dict[str, Any]:
  return {"classification": "not_executable", "countApplicable": False, "countEmitted": False, "countCorrect": None,
          "labelsApplicable": False, "labelsEmitted": False, "labelsCorrect": None, "hasUsable": False,
          "conflict": False, "countErrorDirection": None, "unsafeCertainty": False}


def evaluate_manifest(manifest: dict[str, Any], ground_truth: dict[str, Any], protocol: dict[str, Any],
                      base_dir: str | Path | None = None, fingerprint_fn: Any = None,
                      question_index: dict[str, Any] | None = None) -> dict[str, Any]:
  base = Path(base_dir) if base_dir else ROOT
  index_by_document = question_boundary.index_document_by_id(question_index)
  gt_by_key = {(item["documentId"], item["questionId"]): item for item in ground_truth["questions"]}
  records: list[dict[str, Any]] = []
  for document in manifest["documents"]:
    document_error = verify_document_fingerprint(document, fingerprint_fn)
    index_document = index_by_document.get(document["documentId"])
    for question in document.get("selectedQuestions", []):
      key = (document["documentId"], question["questionId"])
      gt = gt_by_key.get(key)
      if document_error is not None:
        records.append(_record(document, question, gt or {"documentId": document["documentId"], "questionId": question["questionId"]},
                               fusion_result={}, classification=_not_executable_classification(),
                               gt_meta=gt or {}, executable=False, observation_error=document_error))
        continue
      if gt is None:
        records.append(_record(document, question, gt={"documentId": document["documentId"], "questionId": question["questionId"]},
                               fusion_result={}, classification=_not_executable_classification(),
                               gt_meta={}, executable=False, observation_error="missing_ground_truth"))
        continue
      try:
        fusion_result = _run_question(document, question, gt, protocol, base, index_document)
        executable = fusion_result is not None
        observation_error = None if executable else "observation_unavailable"
      except Exception:
        fusion_result = None
        executable = False
        observation_error = "observer_error"
      classification = classify_question(gt, fusion_result or {}, executable)
      records.append(_record(document, question, gt, fusion_result or {}, classification, gt, executable, observation_error))
  metrics = compute_metrics(records)
  documents = document_summary(records)
  slices = compute_slices(records)
  hashes = schema.manifest_hashes(manifest, question_index, ground_truth)
  report = {
    "protocolVersion": protocol["protocolVersion"],
    "generatedAt": _dt.datetime.now(_dt.timezone.utc).isoformat(),
    "commit": _commit(),
    "hashes": hashes,
    "metrics": metrics,
    "documents": documents,
    "slices": slices,
    "records": records,
    "promotionReadiness": {
      "note": "diagnostic only; no automatic boolean and no hardcoded threshold",
      "unsafeErrorMediumHighConfidence": metrics["unsafeErrorMediumHighConfidence"],
      "overcount": metrics["optionCount"]["overcount"],
      "documentsWithoutUnsafeErrorRatio": documents["documentsWithoutUnsafeErrorRatio"],
      "optionCountPrecision": metrics["optionCount"]["precision"],
      "optionLabelsPrecision": metrics["optionLabels"]["precision"],
    },
  }
  return report


def _record(document: dict[str, Any], question: dict[str, Any], gt: dict[str, Any], fusion_result: dict[str, Any],
            classification: dict[str, Any], gt_meta: dict[str, Any], executable: bool,
            observation_error: str | None = None) -> dict[str, Any]:
  origins = sorted({origin for slot in (fusion_result.get("slots") or []) for origin in slot.get("origins", [])})
  return {
    "documentId": document["documentId"],
    "questionId": question["questionId"],
    "contentFingerprint": document.get("contentFingerprint"),
    "observationError": observation_error,
    "sourceType": document["sourceType"],
    "family": document["family"],
    "era": era_of(document["year"]),
    "responseMode": gt_meta.get("responseMode", "unknown"),
    "layout": gt_meta.get("layout", "unknown"),
    "markerStyle": gt_meta.get("markerStyle", "unknown"),
    "contentKind": gt_meta.get("contentKind", "unknown"),
    "origins": origins,
    "executable": executable,
    "fusion": {key: fusion_result.get(key) for key in ("agreement", "sources", "optionCountHypothesis", "optionLabelsHypothesis",
                                                        "observationConfidence", "interpretationConfidence", "blockers")},
    "unambiguousGroundTruth": gt_meta.get("responseMode") in {"single_choice", "true_false"} or gt_meta.get("layout") in {"parent_child", "internal_enumeration"},
    **classification,
  }


def resolve_index_entries(index_document: dict[str, Any] | None, question_id: str) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
  questions = question_boundary.index_questions(index_document)
  current = question_boundary.find_question(questions, question_id)
  if current is None:
    return None, None
  return current, question_boundary.next_question_in_order(questions, question_id)


def _run_question(document: dict[str, Any], question: dict[str, Any], gt: dict[str, Any], protocol: dict[str, Any],
                  base: Path, index_document: dict[str, Any] | None = None) -> dict[str, Any] | None:
  index_current, index_next = resolve_index_entries(index_document, question["questionId"])
  # The frozen question index is authoritative for document order and pages.
  # Ground-truth pages are only a fallback when the index entry is unavailable.
  if index_current is not None:
    pages = question_boundary.expected_pages(index_current)
  else:
    pages = gt.get("pages") or list(range(int(question["pageStart"]), int(question["pageEnd"]) + 1))
  source = document["sourceType"]
  canonical = document["canonicalPath"]
  if source == "text_native" or (canonical and Path(canonical).exists() and source != "raster"):
    bundle = observations.from_native_pdf(canonical, pages)
    if bundle.words:
      return _run_with_boundary(bundle, question, index_current, index_next, pages, None)
  return _run_ocr(document, question, index_current, index_next, pages, base)


def _run_ocr(document: dict[str, Any], question: dict[str, Any], index_current: dict[str, Any] | None,
             index_next: dict[str, Any] | None, pages: list[int], base: Path) -> dict[str, Any] | None:
  payload_path = base / "outputs" / "audit" / "ocr" / document["documentId"] / "tesseract" / "ocr.json"
  if not payload_path.exists():
    return None
  payload = json.loads(payload_path.read_text(encoding="utf-8"))
  bundle = observations.from_ocr_payload(payload, pages)
  if not bundle.lines:
    return None
  return _run_with_boundary(bundle, question, index_current, index_next, pages, payload_path.parent / "rendered")


def _run_with_boundary(bundle: observations.ObservationBundle, question: dict[str, Any],
                       index_current: dict[str, Any] | None, index_next: dict[str, Any] | None,
                       pages: list[int], rendered_dir: Path | None) -> dict[str, Any]:
  effective = index_current or question
  boundary = question_boundary.compute_question_boundary(bundle, effective, index_next, pages)
  if index_current is None:
    # Without a frozen index entry the question order is unknown; be conservative.
    boundary = {**boundary, "reliable": False, "reason": "question_not_in_index"}
  filtered = question_boundary.filter_bundle(bundle, boundary)
  return _run_from_bundle(filtered, boundary, rendered_dir, pages)


def _run_from_bundle(bundle: observations.ObservationBundle, boundary: dict[str, Any], rendered_dir: Path | None,
                     pages: list[int]) -> dict[str, Any]:
  lines = bundle.lines_as_region_input()
  words = bundle.words_as_region_input()
  markers = observations.extract_text_markers(lines)
  raster = bundle.visual_as_region_input()
  visual_markers: list[dict[str, Any]] = []
  for page in pages:
    image_path = None
    if rendered_dir is not None:
      candidate = rendered_dir / f"page-{page:02d}.png"
      image_path = str(candidate) if candidate.exists() else None
    if image_path:
      from PIL import Image
      with Image.open(image_path) as image:
        page_result = visual_evidence.analyze_image(image, 160.0, page)
      visual_markers.extend(page_result["evidence"])
      raster.extend(page_result["rawComponents"])
  # Visual evidence must respect the same question boundary as text.
  visual_markers = question_boundary.filter_visual_items(visual_markers, boundary)
  raster = question_boundary.filter_visual_items(raster, boundary)
  discovered = regions.discover_response_regions(
    boundary=boundary, lines=lines, words=words, strong_markers=markers,
    visual_markers=visual_markers, raster_components=raster,
  )
  structure = response_structure.discover_response_structure(_observed_lines(lines))
  visual_shadow = {"visualAlternativeEvidence": visual_markers} if visual_markers else {}
  return fusion.fuse_response_evidence(boundary, structure, visual_shadow, discovered)


def _observed_lines(lines: list[dict[str, Any]]) -> list[Any]:
  return [
    response_structure.ObservedLine(
      text=str(line.get("text") or ""), page=int(line.get("page") or 0), top=float(line.get("top") or 0),
      bottom=float(line.get("bottom") or 0), x0=float(line.get("x0") or 0), x1=float(line.get("x1") or 0),
      line_index=int(line.get("lineIndex") or 0),
    )
    for line in lines
  ]


def era_of(year: int) -> str:
  if year <= 2009:
    return "2004-2009"
  if year <= 2014:
    return "2010-2014"
  if year <= 2019:
    return "2015-2019"
  return "2020-2025"


def render_markdown(report: dict[str, Any]) -> str:
  metrics = report["metrics"]
  lines = [
    "# Auditor V1 — Structural Holdout report", "",
    f"- protocol: {report['protocolVersion']}",
    f"- commit: {report['commit']}",
    f"- hashes: {report['hashes']}",
    "",
    "## Metrics",
    f"- questions: {metrics['questions']} (executable {metrics['executable']})",
    f"- classes: {metrics['classes']}",
    f"- coverage: {metrics['coverage']}  abstention: {metrics['abstention']}",
    f"- question-level emitted precision: {metrics['questionLevelEmittedPrecision']}",
    f"- optionCount: {metrics['optionCount']}",
    f"- optionLabels: {metrics['optionLabels']}",
    f"- unsafe_error: {metrics['unsafeError']} (low {metrics['unsafeErrorLowConfidence']} / medium-high {metrics['unsafeErrorMediumHighConfidence']})",
    f"- false conflict rate: {metrics['falseConflictRate']} ({metrics['conflicts']} conflicts)",
    "",
    "## Documents",
    f"- documents without unsafe_error ratio: {report['documents']['documentsWithoutUnsafeErrorRatio']}",
  ]
  return "\n".join(lines) + "\n"


def main() -> None:
  parser = argparse.ArgumentParser(description="Auditor V1 structural holdout runner (read-only over manifest/ground-truth).")
  parser.add_argument("--protocol", required=True)
  parser.add_argument("--manifest", required=True)
  parser.add_argument("--ground-truth", required=True)
  parser.add_argument("--question-index", required=True,
                      help="Frozen neutral question index used for intra-page question boundaries.")
  parser.add_argument("--out-dir", default=str(REPORT_DIR))
  args = parser.parse_args()

  protocol = schema.load_json(args.protocol)
  manifest = schema.load_json(args.manifest)
  ground_truth = schema.load_json(args.ground_truth)
  schema.validate_protocol(protocol)
  schema.validate_manifest(manifest)
  schema.validate_ground_truth(ground_truth)
  question_index = None
  if args.question_index:
    question_index = schema.load_json(args.question_index)
    schema.validate_question_index(question_index)
    schema.validate_bindings(manifest, question_index=question_index, ground_truth=ground_truth)
  else:
    schema.validate_bindings(manifest, ground_truth=ground_truth)

  report = evaluate_manifest(manifest, ground_truth, protocol, question_index=question_index)
  out_dir = Path(args.out_dir)
  out_dir.mkdir(parents=True, exist_ok=True)
  stamp = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
  schema.write_json(out_dir / f"run-{stamp}.json", report)
  (out_dir / f"run-{stamp}.md").write_text(render_markdown(report), encoding="utf-8")
  print(json.dumps({"outDir": str(out_dir), "stamp": stamp, "metrics": report["metrics"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
  main()
