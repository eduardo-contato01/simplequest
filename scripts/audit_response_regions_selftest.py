from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_response_regions as regions  # noqa: E402
import audit_visual_marker_evidence as visual_evidence  # noqa: E402

try:
  import audit_observations as observations  # noqa: E402
except Exception:  # pragma: no cover
  observations = None

from PIL import Image, ImageDraw  # noqa: E402

FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
  if condition:
    print(f"PASS {name}")
  else:
    print(f"FAIL {name} {detail}")
    FAILURES.append(name)


def line(text: str, page: int, x0: float, y0: float, x1: float | None = None, y1: float | None = None, line_index: int = 0) -> dict:
  return {
    "text": text, "page": page, "x0": x0, "top": y0,
    "x1": (x1 if x1 is not None else x0 + 80.0),
    "bottom": (y1 if y1 is not None else y0 + 12.0),
    "lineIndex": line_index, "role": "stem",
  }


def marker(label: str, page: int, x0: float, y0: float, **kwargs) -> dict:
  return {
    "label": label, "markerKind": kwargs.get("markerKind", "answer_marker"),
    "subitemLabel": kwargs.get("subitemLabel"), "parentQuestion": kwargs.get("parentQuestion"),
    "labelCase": kwargs.get("labelCase", "upper"), "markerShape": kwargs.get("markerShape", "none"),
    "separator": kwargs.get("separator", "none"), "responseField": kwargs.get("responseField", "absent"),
    "text": kwargs.get("text", ""), "page": page,
    "bbox": [x0, y0, x0 + 30.0, y0 + 30.0], "lineIndex": kwargs.get("lineIndex"),
  }


def visual(page: int, x0: float, y0: float) -> dict:
  return {"page": page, "bbox": [x0, y0, x0 + 30.0, y0 + 30.0], "shape": "circle", "fill": "outline"}


def raster(page: int, x0: float, y0: float, x1: float, y1: float, area: float = 6000.0) -> dict:
  return {"page": page, "bbox": [x0, y0, x1, y1], "area": area, "width": x1 - x0, "height": y1 - y0, "fill": 0.6}


def analyze(lines, markers=None, visuals=None, rasters=None, reliable=True):
  return regions.discover_response_regions(
    boundary={"reliable": reliable, "pages": [1]},
    lines=lines, words=None, strong_markers=markers or [],
    visual_markers=visuals or [], raster_components=rasters or [],
  )


def test_marker_text() -> None:
  lines, markers = [], []
  for index, label in enumerate("ABCDE"):
    y = 100 + index * 60
    markers.append(marker(label, 1, 50, y, lineIndex=index))
    lines.append(line(f"opcao {label} com texto", 1, 90, y + 4, line_index=100 + index))
  result = analyze(lines, markers)
  pattern = result["questionResponsePattern"]["pattern"]
  slots = result["responseSlotHypotheses"]
  check("text.pattern", pattern == "one_per_option", pattern)
  check("text.roles", all(slot["role"] == "answer_option" for slot in slots), slots)
  check("text.regions", len(result["observedResponseRegions"]) == 5, result["observedResponseRegions"])
  check("text.kind", all(region["kind"] == "text" for region in result["observedResponseRegions"]), result["observedResponseRegions"])


def test_marker_fraction() -> None:
  lines, markers = [], []
  for index, label in enumerate("ABCDE"):
    y = 100 + index * 80
    markers.append(marker(label, 1, 50, y, lineIndex=index))
    lines.append(line("1", 1, 90, y + 2, x1=100, y1=y + 12, line_index=100 + index * 3))
    lines.append(line("-", 1, 88, y + 14, x1=132, y1=y + 17, line_index=101 + index * 3))
    lines.append(line("6", 1, 90, y + 19, x1=100, y1=y + 31, line_index=102 + index * 3))
  result = analyze(lines, markers)
  kinds = {region["kind"] for region in result["observedResponseRegions"]}
  check("fraction.kind_math", kinds == {"math"}, kinds)
  check("fraction.evidence", any("fraction_bar" in region["evidence"] for region in result["observedResponseRegions"]), result["observedResponseRegions"])


def test_circle_text() -> None:
  lines, visuals = [], []
  for index, _ in enumerate("ABCDE"):
    y = 100 + index * 60
    visuals.append(visual(1, 50, y))
    lines.append(line(f"texto da alternativa {index}", 1, 90, y + 4, line_index=index))
  result = analyze(lines, visuals=visuals)
  pattern = result["questionResponsePattern"]["pattern"]
  check("circle.pattern", pattern == "one_per_option", pattern)
  check("circle.roles", all(slot["role"] == "answer_option" for slot in result["responseSlotHypotheses"]), result["responseSlotHypotheses"])
  check("circle.kind", all(region["kind"] == "text" for region in result["observedResponseRegions"]), result["observedResponseRegions"])


def test_circle_fraction() -> None:
  lines, visuals = [], []
  for index in range(5):
    y = 100 + index * 80
    visuals.append(visual(1, 50, y))
    lines.append(line("1", 1, 90, y + 2, x1=100, y1=y + 12, line_index=index * 3))
    lines.append(line("-", 1, 88, y + 14, x1=132, y1=y + 17, line_index=index * 3 + 1))
    lines.append(line("6", 1, 90, y + 19, x1=100, y1=y + 31, line_index=index * 3 + 2))
  result = analyze(lines, visuals=visuals)
  kinds = {region["kind"] for region in result["observedResponseRegions"]}
  check("circlefrac.kind_math", kinds == {"math"}, kinds)


def test_marker_media() -> None:
  lines, markers, rasters = [], [], []
  for index, label in enumerate("ABCDE"):
    y = 100 + index * 80
    markers.append(marker(label, 1, 50, y, lineIndex=index))
    rasters.append(raster(1, 90, y, 300, y + 60))
  result = analyze(lines, markers, rasters=rasters)
  kinds = {region["kind"] for region in result["observedResponseRegions"]}
  check("media.kind", kinds <= {"media", "mixed"} and kinds, kinds)
  check("media.no_stem_figure", len(result["observedResponseRegions"]) == 5, result["observedResponseRegions"])


def test_grid() -> None:
  lines, markers = [], []
  positions = [("A", 50, 100), ("B", 400, 100), ("C", 50, 300), ("D", 400, 300), ("E", 225, 500)]
  for index, (label, x, y) in enumerate(positions):
    markers.append(marker(label, 1, x, y, lineIndex=index))
    lines.append(line(f"grafico {label}", 1, x + 40, y + 20, x1=x + 40, y1=y + 30, line_index=100 + index))
  result = analyze(lines, markers)
  pattern = result["questionResponsePattern"]["pattern"]
  check("grid.pattern", pattern == "grid_option_markers", pattern)
  check("grid.slots", len(result["responseSlotHypotheses"]) == 5, result["responseSlotHypotheses"])


def test_internal_then_options() -> None:
  lines = [
    line("a) primeiro item do enunciado", 1, 50, 100, line_index=0),
    line("b) segundo item do enunciado", 1, 50, 130, line_index=1),
    line("c) terceiro item do enunciado", 1, 50, 160, line_index=2),
    line("assinale a opcao correta", 1, 50, 200, line_index=3),
  ]
  markers = []
  for index, label in enumerate("ABCDE"):
    y = 240 + index * 50
    markers.append(marker(label, 1, 50, y, lineIndex=10 + index))
    lines.append(line(f"alternativa {label}", 1, 90, y + 4, line_index=20 + index))
  result = analyze(lines, markers)
  pattern = result["questionResponsePattern"]["pattern"]
  roles = {slot["role"] for slot in result["responseSlotHypotheses"]}
  check("internal.options.pattern", pattern == "internal_enumeration_then_options", pattern)
  check("internal.options.roles", "subitem" in roles and "answer_option" in roles, roles)


def test_internal_only() -> None:
  lines = [
    line("Responda aos itens a seguir.", 1, 50, 100, line_index=0),
    line("I) primeira resposta", 1, 50, 140, line_index=1),
    line("II) segunda resposta", 1, 50, 180, line_index=2),
  ]
  result = analyze(lines)
  pattern = result["questionResponsePattern"]["pattern"]
  check("internal_only.pattern", pattern == "internal_enumeration", pattern)
  check("internal_only.subitems", len(result["responseSlotHypotheses"]) == 2, result["responseSlotHypotheses"])
  check("internal_only.role", all(slot["role"] == "subitem" for slot in result["responseSlotHypotheses"]), result["responseSlotHypotheses"])


def test_paired_controls() -> None:
  lines = [line("julgue as afirmacoes e assinale C ou E", 1, 50, 60, line_index=0)]
  markers = []
  for index, sub in enumerate("ABCDE"):
    y = 120 + index * 60
    markers.append(marker(None, 1, 50, y, markerKind="parent_child", subitemLabel=sub, parentQuestion=15, labelCase="upper", lineIndex=index))
    lines.append(line(f"afirmacao {sub} do subitem", 1, 110, y + 4, line_index=100 + index))
  visuals = []
  for index in range(5):
    y = 120 + index * 60
    visuals.append(visual(1, 170, y))
    visuals.append(visual(1, 220, y))
  result = analyze(lines, markers, visuals=visuals)
  pattern = result["questionResponsePattern"]["pattern"]
  roles = {}
  for slot in result["responseSlotHypotheses"]:
    roles[slot["role"]] = roles.get(slot["role"], 0) + 1
  check("controls.pattern", pattern == "paired_controls_per_row", pattern)
  check("controls.not_options", not any(slot["role"] == "answer_option" for slot in result["responseSlotHypotheses"]), roles)
  check("controls.counts", roles.get("response_control") == 10 and roles.get("subitem") == 5, roles)


def test_numeric_no_local_slot() -> None:
  lines = [
    line("Calcule o valor solicitado.", 1, 50, 100, line_index=0),
    line("Espaco livre", 1, 50, 140, line_index=1),
  ]
  result = analyze(lines)
  check("numeric.no_regions", result["observedResponseRegions"] == [], result["observedResponseRegions"])
  check("numeric.no_slots", result["responseSlotHypotheses"] == [], result["responseSlotHypotheses"])
  check("numeric.pattern_unknown", result["questionResponsePattern"]["pattern"] == "unknown", result["questionResponsePattern"])


def test_boundary_uncertain() -> None:
  lines, markers = [], []
  for index, label in enumerate("ABCDE"):
    y = 100 + index * 60
    markers.append(marker(label, 1, 50, y, lineIndex=index))
    lines.append(line(f"opcao {label}", 1, 90, y + 4, line_index=100 + index))
  result = analyze(lines, markers, reliable=False)
  check("boundary.blocker", "boundary_uncertain" in result["blockers"], result["blockers"])
  check("boundary.low_conf", all(slot["confidence"] == "low" for slot in result["responseSlotHypotheses"]), result["responseSlotHypotheses"])


def test_weak_anchors() -> None:
  lines = [line("14. Bianca comecou a descer a escada e Fernanda a subir", 1, 50, 100, line_index=0)]
  for index in range(5):
    y = 300 + index * 30
    lines.append(line("marker-ish", 1, 86, y, x1=100, line_index=10 + index * 2))
    lines.append(line(str(index + 1), 1, 130, y + 2, x1=140, line_index=11 + index * 2))
  result = analyze(lines)
  weak = result["weakRegionAnchors"]
  pattern = result["questionResponsePattern"]["pattern"]
  check("weak.detected", len(weak) == 5, weak)
  check("weak.not_marker", all(anchor["source"] == "weak" and anchor["label"] is None for anchor in weak), weak)
  check("weak.pattern", pattern == "one_per_option", pattern)
  check("weak.slots", len(result["responseSlotHypotheses"]) == 5, result["responseSlotHypotheses"])


def test_two_concurrent_clusters() -> None:
  visuals = []
  for index in range(3):
    y = 100 + index * 60
    visuals.append(visual(1, 50, y))
    visuals.append(visual(1, 400, y))
  result = analyze([], visuals=visuals)
  slots = result["responseSlotHypotheses"]
  check("concurrent.slots", len(slots) == 6, slots)
  check("concurrent.pattern", result["questionResponsePattern"]["pattern"] != "unknown", result["questionResponsePattern"])


def test_marker_without_content() -> None:
  markers = [marker("A", 1, 50, 100, lineIndex=0)]
  result = analyze([], markers)
  slots = result["responseSlotHypotheses"]
  check("nocontent.slot_null", slots and slots[0]["contentRegionId"] is None, slots)


def test_ce_instruction_only() -> None:
  lines = [line("assinale C para certo e E para errado", 1, 50, 60, line_index=0)]
  visuals = []
  for index in range(5):
    y = 120 + index * 60
    visuals.append(visual(1, 170, y))
    visuals.append(visual(1, 220, y))
  result = analyze(lines, visuals=visuals)
  roles = {slot["role"] for slot in result["responseSlotHypotheses"]}
  check("ce_only.controls", roles == {"response_control"}, roles)
  check("ce_only.pattern", result["questionResponsePattern"]["pattern"] == "paired_controls_per_row", result["questionResponsePattern"])


def test_ocr_adapter() -> None:
  payload = {"pages": [{"page": 1, "width": 1000, "height": 1500, "pdfWidth": 500, "pdfHeight": 750,
                        "lines": [{"text": "A) um", "bbox": [10, 10, 100, 30], "words": [{"text": "A)", "bbox": [10, 10, 30, 30]}, {"text": "um", "bbox": [35, 10, 80, 30]}]}]}]}
  bundle = observations.from_ocr_payload(payload, [1])
  check("adapter.ocr.lines", len(bundle.lines) == 1, bundle.lines)
  check("adapter.ocr.words", len(bundle.words) == 2, bundle.words)
  check("adapter.ocr.geometry", bundle.page_geometry[1]["scaleX"] == 2.0, bundle.page_geometry)


def test_native_line_grouping() -> None:
  words = [
    observations.ObservedWord(page=1, text="A", bbox=(10, 10, 20, 25)),
    observations.ObservedWord(page=1, text="texto", bbox=(25, 10, 60, 25)),
    observations.ObservedWord(page=1, text="B", bbox=(10, 40, 20, 55)),
    observations.ObservedWord(page=1, text="outro", bbox=(25, 40, 60, 55)),
    observations.ObservedWord(page=1, text="coluna", bbox=(300, 10, 360, 25)),
  ]
  lines = observations.group_words_into_lines(words, page_width=600)
  texts = sorted(line.text for line in lines)
  check("adapter.group.count", len(lines) == 3, texts)
  check("adapter.group.columns", any("A texto" in t for t in texts) and any("B outro" in t for t in texts), texts)
  check("adapter.group.separate_column", any(t == "coluna" for t in texts), texts)


def test_math_region_from_raster_without_ocr() -> None:
  result = analyze(
    [],
    visuals=[visual_marker(1, 50, 100)],
    rasters=[
      {"page": 1, "bbox": [90, 104, 130, 107], "area": 120, "width": 40, "height": 3, "fill": 1.0},
      {"page": 1, "bbox": [95, 108, 105, 122], "area": 90, "width": 10, "height": 14, "fill": 0.6},
    ],
  )
  region = result["observedResponseRegions"][0]
  check("rastermath.kind", region["kind"] == "math", region)
  check("rastermath.no_lines", region["lineIndexes"] == [], region)


def test_weak_never_high() -> None:
  lines = [line("enunciado", 1, 50, 100, line_index=0)]
  for index in range(4):
    y = 300 + index * 30
    lines.append(line("x", 1, 86, y, x1=100, line_index=10 + index * 2))
    lines.append(line(str(index), 1, 130, y + 2, x1=140, line_index=11 + index * 2))
  result = analyze(lines)
  slots = result["responseSlotHypotheses"]
  check("weak.not_high", slots and all(slot["confidence"] == "low" for slot in slots), slots)
  check("weak.reason", all("weakAnchorReason" in anchor for anchor in result["weakRegionAnchors"]), result["weakRegionAnchors"])


def test_raw_component_reuse() -> None:
  image = Image.new("L", (200, 200), 255)
  draw = ImageDraw.Draw(image)
  draw.ellipse([40, 40, 70, 70], outline=0, width=2)
  draw.rectangle([100, 100, 150, 140], fill=0)
  standalone = visual_evidence.analyze_raw_components(image, 1)
  analysis = visual_evidence.analyze_image(image, 160.0, 1)
  check("reuse.same_raw", [c["bbox"] for c in standalone] == [c["bbox"] for c in analysis["rawComponents"]],
        (standalone, analysis["rawComponents"]))


def visual_marker(page: int, x0: float, y0: float) -> dict:
  return {"page": page, "bbox": [x0, y0, x0 + 30.0, y0 + 30.0], "shape": "circle", "fill": "outline"}


def main() -> None:
  test_marker_text()
  test_marker_fraction()
  test_circle_text()
  test_circle_fraction()
  test_marker_media()
  test_grid()
  test_internal_then_options()
  test_internal_only()
  test_paired_controls()
  test_numeric_no_local_slot()
  test_boundary_uncertain()
  test_weak_anchors()
  test_two_concurrent_clusters()
  test_marker_without_content()
  test_ce_instruction_only()
  if observations is not None:
    test_ocr_adapter()
    test_native_line_grouping()
  test_math_region_from_raster_without_ocr()
  test_weak_never_high()
  test_raw_component_reuse()
  if FAILURES:
    print(f"\n{len(FAILURES)} checks falharam: {FAILURES}")
    raise SystemExit(1)
  print("\nTodos os checks da camada de regioes/slots passaram.")


if __name__ == "__main__":
  main()

