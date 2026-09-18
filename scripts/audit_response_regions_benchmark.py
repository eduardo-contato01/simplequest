from __future__ import annotations

import argparse
import glob
import json
import os
from pathlib import Path
from typing import Any

import audit_observations as observations
import audit_ocr_content as ocr
import audit_response_fusion as fusion
import audit_response_regions as regions
import audit_response_structure as response_structure
import audit_visual_marker_evidence as visual_evidence

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_JSON = ROOT / "outputs" / "audit" / "response-regions-benchmark.json"
OUTPUT_MD = ROOT / "outputs" / "audit" / "response-regions-benchmark.md"

PDF_BASE = r"G:\Drives compartilhados\Secretaria e Editoração\PROVAS CMs E OUTRAS PROVAS"


def _pdf(pattern: str) -> str | None:
  hits = [p for p in glob.glob(PDF_BASE + pattern, recursive=True) if "GABARITO" not in p.upper()]
  return hits[0] if hits else None


# Evaluation-only benchmark list. Institution/year live here (external
# evaluation), never inside the detectors.
BENCHMARKS: list[dict[str, Any]] = [
  {"id": "CMBH17-Q2", "source": "ocr_cache", "slug": "cmbh-6ano-2017-2018-mat", "school": "CMBH", "year": 2017, "question": 2,
   "expected": {"pattern": "one_per_option", "answer_options": 5, "kinds_any": ["text", "math"]}},
  {"id": "CMBH17-Q5", "source": "ocr_cache", "slug": "cmbh-6ano-2017-2018-mat", "school": "CMBH", "year": 2017, "question": 5,
   "expected": {"pattern": "one_per_option", "answer_options": 5, "regions_min": 5, "kinds_any": ["math", "text", "unknown"]}},
  {"id": "CMBH17-Q19", "source": "ocr_cache", "slug": "cmbh-6ano-2017-2018-mat", "school": "CMBH", "year": 2017, "question": 19,
   "expected": {"pattern": "one_per_option", "answer_options": 5, "kinds_any": ["text", "mixed"]}},
  {"id": "CMC11-Q14", "source": "ocr_cache", "slug": "cmc-6ano-2011-2012-mat", "school": "CMC", "year": 2011, "question": 14,
   "expected": {"pattern": "one_per_option", "answer_options": 5, "kinds_any": ["math", "text", "unknown"]}},
  {"id": "CMBel17-Q7", "source": "ocr_words", "slug": "cmbel-6ano-2017-2018-mat", "school": "CMBel", "year": 2017, "question": 7,
   "window": {"page": 8, "top": 780, "bottom": 1660, "x0": 60, "x1": 1265},
   "expected": {"pattern": "grid_option_markers", "answer_options": 5, "kinds_any": ["media", "mixed", "unknown"]}},
  {"id": "CMBH18-Q2", "source": "native_pdf", "pdf": _pdf(r"\CMBH\**\CMBH - 6ANO - 2018_2019 (mat).pdf"), "pages": [2],
   "question": 2, "renderVisual": True,
   "window": {"page": 2, "top": 490, "bottom": 800},
   "expected": {"pattern": "internal_enumeration_then_options", "answer_options": 5, "subitems_min": 3}},
  {"id": "CMT22-Q15", "source": "native_pdf", "pdf": _pdf(r"\CMT\**\CMT - 6ANO - 2022_2023.pdf"), "pages": [11],
   "question": 15,
   "window": {"page": 11, "top": 330, "bottom": 690},
   "expected": {"pattern": "paired_controls_per_row", "subitems_min": 5, "answer_options": 0, "controls_min": 10, "controls_optional": True}},
  {"id": "CMT22-Q30", "source": "native_pdf", "pdf": _pdf(r"\CMT\**\CMT - 6ANO - 2022_2023.pdf"), "pages": [22],
   "question": 30,
   "window": {"page": 22, "top": 40, "bottom": 620},
   "expected": {"pattern": "paired_controls_per_row", "subitems_min": 5, "answer_options": 0, "controls_min": 10, "controls_optional": True}},
  {"id": "PAS19-item24", "source": "native_pdf", "pdf": _pdf(r"\PAS 2\**\PAS 2 - 2019.pdf"), "pages": [5],
   "question": 24, "instructionContext": True,
   "window": {"page": 5, "top": 680, "bottom": 805},
   "expected": {"pattern": "one_per_option", "answer_options": 4}},
  {"id": "PAS19-item75", "source": "native_pdf", "pdf": _pdf(r"\PAS 2\**\PAS 2 - 2019.pdf"), "pages": [10],
   "question": 75, "instructionContext": True,
   "window": {"page": 10, "top": 365, "bottom": 470},
   "expected": {"pattern": "unknown", "answer_options": 0, "regions": 0, "slots": 0}},
  {"id": "PAS19-item87", "source": "native_pdf", "pdf": _pdf(r"\PAS 2\**\PAS 2 - 2019.pdf"), "pages": [12],
   "question": 87, "instructionContext": True,
   "window": {"page": 12, "top": 350, "bottom": 770, "x0": 0, "x1": 292},
   "expected": {"pattern": "internal_enumeration", "answer_options": 0}},
  {"id": "PAS19-item90", "source": "native_pdf", "pdf": _pdf(r"\PAS 2\**\PAS 2 - 2019.pdf"), "pages": [12],
   "question": 90, "instructionContext": True,
   "window": {"page": 12, "top": 300, "bottom": 770, "x0": 295, "x1": 595},
   "expected": {"pattern": "one_per_option", "answer_options": 4}},
]

_CONTEXT_CACHE: dict[str, Any] = {}


def _ocr_case(case: dict[str, Any]) -> dict[str, Any] | None:
  slug = case["slug"]
  if slug not in _CONTEXT_CACHE:
    payload = ocr.load_payload(slug)
    catalog = ocr.pilot.load_effective_catalog()
    expected = [
      int(question["number"]) for question in catalog
      if question.get("school") == case["school"] and int(question.get("year", 0)) == case["year"]
    ]
    context = ocr.build_pilot_context(payload, expected)
    context["slug"] = slug
    _CONTEXT_CACHE[slug] = context
  context = _CONTEXT_CACHE[slug]
  number = case["question"]
  start = ocr.find_question_marker(context["markers"], context["in_scope_pages"], number)
  if start is None:
    return None
  start_index = context["markers"].index(start)
  end = ocr.find_region_end(context["markers"], start_index, context["in_scope_pages"])
  start_page = int(start["page"])
  start_top = float(start.get("top") or 0)
  scope_end = int(context["scope"]["questionContentEnd"])
  if end:
    end_page = int(end["page"])
    end_top: float | None = float(end.get("top") or 0)
    end_role = context["scope_roles"].get(end_page)
    boundary_reliable = True
  else:
    end_page = scope_end
    end_top = None
    end_role = context["scope_roles"].get(scope_end)
    boundary_reliable = end_role not in {"answer_sheet_or_post_content"}
  recurring = ocr.pilot.recurring_edge_lines(list(context["pages"].values()))
  region = ocr.collect_region(context, start_page, start_top, end_page, end_top, recurring)
  structure_shadow = ocr.discover_response_structure_shadow(region, ocr.rendered_page_image(slug, start_page))
  visual_shadow = ocr.visual_evidence_shadow(region, context, start_page, end_page)
  pages_used = list(range(start_page, end_page + 1))
  shadow = ocr.response_regions_shadow(region, structure_shadow, visual_shadow, context, boundary_reliable, pages_used)
  fusion_result = fusion.fuse_response_evidence(
    {"reliable": boundary_reliable, "pages": pages_used}, structure_shadow, visual_shadow, shadow
  )
  return {"source": "ocr_cache", "pages": pages_used, "shadow": shadow, "fusion": fusion_result}


def _native_case(case: dict[str, Any]) -> dict[str, Any] | None:
  pdf_path = case.get("pdf")
  if not pdf_path or not os.path.exists(pdf_path):
    return None
  bundle = observations.from_native_pdf(pdf_path, case["pages"])
  window = case.get("window")
  all_lines = bundle.lines_as_region_input()
  context_lines: list[dict[str, Any]] = []
  if case.get("instructionContext") and case.get("question") is not None:
    context_lines = observations.extract_instruction_context(all_lines, case["question"])
  lines = [line for line in all_lines if _in_window(line["page"], line["top"], line["x0"], window)]
  known = {(line["page"], round(line["top"], 1), line["text"]) for line in lines}
  for line in context_lines:
    key = (line["page"], round(line["top"], 1), line["text"])
    if key not in known:
      lines.append(line)
      known.add(key)
  lines.sort(key=lambda line: (line["page"], line["top"], line["x0"]))
  words = [word for word in bundle.words_as_region_input() if _in_window(word["page"], word["bbox"][1], word["bbox"][0], window)]
  raster = [component for component in bundle.visual_as_region_input() if _in_window(component["page"], component["bbox"][1], component["bbox"][0], window)]
  for index, line in enumerate(lines):
    line["lineIndex"] = index
  markers = observations.extract_text_markers(lines)
  visual_markers: list[dict[str, Any]] = []
  if case.get("renderVisual"):
    visual_markers, rendered_raw = _native_rendered_visual(case)
    raster.extend(rendered_raw)
  shadow = regions.discover_response_regions(
    boundary={"reliable": True, "pages": case["pages"]},
    lines=lines,
    words=words,
    strong_markers=markers,
    visual_markers=visual_markers,
    raster_components=raster,
  )
  observed_lines = [
    response_structure.ObservedLine(
      text=str(line["text"]), page=int(line["page"]), top=float(line["top"]),
      bottom=float(line["bottom"]), x0=float(line["x0"]), x1=float(line["x1"]),
      line_index=int(line["lineIndex"]),
    )
    for line in lines
  ]
  structure_shadow = response_structure.discover_response_structure(observed_lines)
  if context_lines:
    structure_shadow["instructionContext"] = [{"text": line["text"], "page": line["page"], "top": line["top"]} for line in context_lines]
  visual_shadow = {"visualAlternativeEvidence": visual_markers} if visual_markers else {}
  fusion_result = fusion.fuse_response_evidence(
    {"reliable": True, "pages": case["pages"]}, structure_shadow, visual_shadow, shadow
  )
  return {"source": "native_pdf", "pages": case["pages"], "shadow": shadow, "fusion": fusion_result, "markerCount": len(markers)}


def _native_rendered_visual(case: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
  from PIL import Image
  evidence: list[dict[str, Any]] = []
  raw: list[dict[str, Any]] = []
  window = case.get("window")
  for page in case["pages"]:
    try:
      info = observations.render_pdf_page(case["pdf"], page, 160.0)
    except Exception:
      continue
    scale = float(info["scale"])
    with Image.open(info["path"]) as image:
      width, height = image.size
      x0 = int(float(window.get("x0", 0)) * scale)
      y0 = int(float(window.get("top", 0)) * scale)
      x1 = int(float(window.get("x1", width / scale)) * scale)
      y1 = int(float(window.get("bottom", height / scale)) * scale)
      crop = image.crop((max(0, x0), max(0, y0), min(width, x1), min(height, y1)))
      page_result = visual_evidence.analyze_image(crop, 160.0, page, offset=(max(0, x0), max(0, y0)))
    for item in page_result["evidence"]:
      converted = dict(item)
      converted["bbox"] = [value / scale for value in item["bbox"]]
      converted["source"] = "rendered_visual"
      evidence.append(converted)
    for item in page_result["rawComponents"]:
      converted = dict(item)
      converted["bbox"] = [value / scale for value in item["bbox"]]
      converted["width"] = item["width"] / scale
      converted["height"] = item["height"] / scale
      raw.append(converted)
  return evidence, raw


def _ocr_words_case(case: dict[str, Any]) -> dict[str, Any] | None:
  slug = case["slug"]
  payload = ocr.load_payload(slug)
  bundle = observations.from_ocr_payload(payload, [case["window"]["page"]])
  window = case["window"]
  lines = [line for line in bundle.lines_as_region_input() if _in_window(line["page"], line["top"], line["x0"], window)]
  words = [word for word in bundle.words_as_region_input() if _in_window(word["page"], word["bbox"][1], word["bbox"][0], window)]
  for index, line in enumerate(lines):
    line["lineIndex"] = index
  cells = observations.resegment_words_into_cells(words, region=window)
  markers = [
    {
      "markerKind": "answer_marker", "label": cell["label"], "labelCase": "upper",
      "markerShape": "none", "separator": "none", "responseField": "absent", "text": "",
      "page": window["page"], "bbox": cell["bbox"], "lineIndex": None, "source": "ocr_word_geometry",
    }
    for cell in cells
  ]
  raster: list[dict[str, Any]] = []
  image_path = ocr.rendered_page_image(slug, window["page"])
  if image_path:
    from PIL import Image
    with Image.open(image_path) as image:
      crop = image.crop((window.get("x0", 0), window.get("top", 0), window.get("x1", image.size[0]), window.get("bottom", image.size[1])))
      page_result = visual_evidence.analyze_image(crop, 160.0, window["page"], offset=(window.get("x0", 0), window.get("top", 0)))
    raster = page_result["rawComponents"]
  # Graph content makes circle detection unreliable here; cell geometry is the
  # observation of record. Raw raster components still feed region content.
  visual_markers: list[dict[str, Any]] = []
  shadow = regions.discover_response_regions(
    boundary={"reliable": True, "pages": [window["page"]]},
    lines=lines,
    words=words,
    strong_markers=markers,
    visual_markers=visual_markers,
    raster_components=raster,
  )
  visual_shadow = {"visualAlternativeEvidence": visual_markers} if visual_markers else {}
  fusion_result = fusion.fuse_response_evidence(
    {"reliable": True, "pages": [window["page"]]}, {"instructionContext": []}, visual_shadow, shadow
  )
  return {"source": "ocr_words", "pages": [window["page"]], "shadow": shadow, "fusion": fusion_result, "markerCount": len(markers), "cells": len(cells)}


def _in_window(page: int, top: float, x0: float, window: dict[str, Any] | None) -> bool:
  if window is None:
    return True
  if int(window.get("page") or 0) != int(page):
    return False
  if top < float(window.get("top", 0)) - 2 or top > float(window.get("bottom", 10 ** 9)) + 2:
    return False
  if "x0" in window and x0 < float(window["x0"]) - 2:
    return False
  if "x1" in window and x0 > float(window["x1"]):
    return False
  return True


def _fusion_summary(fusion_result: dict[str, Any] | None) -> dict[str, Any] | None:
  if not fusion_result:
    return None
  return {
    "agreement": fusion_result.get("agreement"),
    "sources": fusion_result.get("sources"),
    "optionCountHypothesis": fusion_result.get("optionCountHypothesis"),
    "optionLabelsHypothesis": fusion_result.get("optionLabelsHypothesis"),
    "observationConfidence": fusion_result.get("observationConfidence"),
    "associationConfidence": fusion_result.get("associationConfidence"),
    "interpretationConfidence": fusion_result.get("interpretationConfidence"),
    "hardBlockers": fusion_result.get("hardBlockers"),
    "softBlockers": fusion_result.get("softBlockers"),
  }


def _summary(shadow: dict[str, Any]) -> dict[str, Any]:
  regions_list = shadow.get("observedResponseRegions") or []
  slots = shadow.get("responseSlotHypotheses") or []
  roles: dict[str, int] = {}
  for slot in slots:
    roles[slot["role"]] = roles.get(slot["role"], 0) + 1
  kinds: dict[str, int] = {}
  for region in regions_list:
    kinds[region["kind"]] = kinds.get(region["kind"], 0) + 1
  pattern = shadow.get("questionResponsePattern") or {}
  return {
    "regions": len(regions_list),
    "kinds": kinds,
    "slots": len(slots),
    "roles": roles,
    "pattern": pattern.get("pattern"),
    "patternConfidence": pattern.get("confidence"),
    "weakAnchors": len(shadow.get("weakRegionAnchors") or []),
    "blockers": shadow.get("blockers") or [],
  }


def _classify(case: dict[str, Any], observed: dict[str, Any] | None) -> str:
  if observed is None:
    return "not_run"
  expected = case["expected"]
  summary = observed["summary"]
  roles = summary["roles"]
  answer_options = roles.get("answer_option", 0)
  subitems = roles.get("subitem", 0)
  controls = roles.get("response_control", 0)
  pattern = summary["pattern"]

  if expected.get("answer_options") is not None and "answer_options" in expected and expected["answer_options"] == 0 and answer_options > 0:
    return "false_structure"
  if expected.get("controls_min") and answer_options > 0:
    return "false_structure"

  checks: list[bool] = []
  if "pattern" in expected:
    checks.append(pattern == expected["pattern"])
  if "answer_options" in expected:
    checks.append(answer_options == expected["answer_options"])
  if "subitems_min" in expected:
    checks.append(subitems >= expected["subitems_min"])
  if "controls_min" in expected and not expected.get("controls_optional"):
    checks.append(controls >= expected["controls_min"])
  if "regions" in expected:
    checks.append(summary["regions"] == expected["regions"])
  if "regions_min" in expected:
    checks.append(summary["regions"] >= expected["regions_min"])
  if "slots" in expected:
    checks.append(summary["slots"] == expected["slots"])

  if all(checks):
    return "correct"
  if pattern == "unknown" and expected.get("pattern") not in {None, "unknown"}:
    return "uncertain_safe"
  if any(checks):
    return "partial"
  return "uncertain_safe"


def run() -> dict[str, Any]:
  results: list[dict[str, Any]] = []
  for case in BENCHMARKS:
    if case["source"] == "ocr_cache":
      observed = _ocr_case(case)
    elif case["source"] == "native_pdf":
      observed = _native_case(case)
    elif case["source"] == "ocr_words":
      observed = _ocr_words_case(case)
    else:
      observed = None
    if observed is None:
      results.append({
        "id": case["id"], "source": case["source"], "status": "unavailable",
        "classification": "not_run", "reason": case.get("unavailableReason", "no observations"),
        "fusion": _fusion_summary(fusion.fuse_response_evidence({"reliable": True}, {}, {}, {})),
      })
      continue
    summary = _summary(observed["shadow"])
    classification = _classify(case, {"summary": summary})
    results.append({
      "id": case["id"],
      "source": observed["source"],
      "status": "observed",
      "pages": observed.get("pages"),
      "markerCount": observed.get("markerCount"),
      "observed": summary,
      "fusion": _fusion_summary(observed.get("fusion")),
      "expected": case["expected"],
      "classification": classification,
      "weakRegionAnchors": (observed["shadow"].get("weakRegionAnchors") or [])[:12],
    })
  return {"benchmarks": results}


def render_markdown(report: dict[str, Any]) -> str:
  lines = ["# Response Regions / Slots — Benchmark (shadow)", "",
           "Avaliação externa. `expected` nunca alimenta o detector.", ""]
  counts: dict[str, int] = {}
  for item in report["benchmarks"]:
    counts[item["classification"]] = counts.get(item["classification"], 0) + 1
  lines.append("Resumo: " + ", ".join(f"{key}={value}" for key, value in sorted(counts.items())))
  lines.append("")
  lines.append("| id | source | pattern | answers | fusion agreement | sources | optCount | optLabels | obsConf | interpConf | hard/soft blockers | class |")
  lines.append("|----|--------|---------|---------|------------------|---------|----------|-----------|---------|------------|--------------------|-------|")
  for item in report["benchmarks"]:
    if item["status"] != "observed":
      lines.append(f'| {item["id"]} | {item["source"]} | - | - | - | - | - | - | - | - | - | {item["classification"]} |')
      continue
    observed = item["observed"]
    roles = observed["roles"]
    fused = item.get("fusion") or {}
    lines.append(
      f'| {item["id"]} | {item["source"]} | {observed["pattern"]} | {roles.get("answer_option", 0)} | '
      f'{fused.get("agreement")} | {fused.get("sources")} | {fused.get("optionCountHypothesis")} | '
      f'{fused.get("optionLabelsHypothesis")} | {fused.get("observationConfidence")} | '
      f'{fused.get("interpretationConfidence")} | {fused.get("hardBlockers")}/{fused.get("softBlockers")} | '
      f'{item["classification"]} |'
    )
  lines.append("")
  return "\n".join(lines)


def main() -> None:
  parser = argparse.ArgumentParser(description="Response regions/slots benchmark (shadow, read-only).")
  parser.add_argument("--output-dir", default=str(ROOT / "outputs" / "audit"))
  args = parser.parse_args()
  report = run()
  output_dir = Path(args.output_dir)
  output_dir.mkdir(parents=True, exist_ok=True)
  (output_dir / OUTPUT_JSON.name).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
  (output_dir / OUTPUT_MD.name).write_text(render_markdown(report), encoding="utf-8")
  print(json.dumps({
    "json": str(output_dir / OUTPUT_JSON.name),
    "markdown": str(output_dir / OUTPUT_MD.name),
    "classifications": {item["id"]: item["classification"] for item in report["benchmarks"]},
  }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
  main()
