from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_observations as observations  # noqa: E402
import audit_response_fusion as fusion  # noqa: E402
import audit_response_regions as regions  # noqa: E402
import audit_visual_marker_evidence as visual_evidence  # noqa: E402

from PIL import Image, ImageDraw  # noqa: E402

FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
  if condition:
    print(f"PASS {name}")
  else:
    print(f"FAIL {name} {detail}")
    FAILURES.append(name)


def line(text: str, page: int, top: float, x0: float, bottom: float | None = None, x1: float | None = None) -> dict:
  return {"text": text, "page": page, "top": top, "bottom": bottom if bottom is not None else top + 12.0,
          "x0": x0, "x1": x1 if x1 is not None else x0 + 200.0, "lineIndex": 0}


def word(text: str, page: int, x0: float, top: float, x1: float | None = None, bottom: float | None = None) -> dict:
  return {"page": page, "text": text, "bbox": [x0, top, x1 if x1 else x0 + 12.0, bottom if bottom else top + 14.0], "wordIndex": 0}


def visual(page: int, x0: float, y0: float) -> dict:
  return {"page": page, "bbox": [x0, y0, x0 + 30.0, y0 + 30.0], "shape": "circle", "fill": "outline"}


def test_instruction_context() -> None:
  lines = [
    line("Tendo como referencia a situacao, julgue os itens 73 e 74 e faca o que se pede no item 75, que e do tipo B.", 1, 100, 30),
    line("75 Calcule a distancia solicitada.", 1, 200, 30),
  ]
  context = observations.extract_instruction_context(lines, 75)
  check("ctx.reference_found", len(context) == 1 and "item 75" in context[0]["text"], context)
  check("ctx.no_reference_empty", observations.extract_instruction_context(lines, 12) == [], "not empty")


def test_espaco_livre_not_field() -> None:
  result = regions.discover_response_regions(
    boundary={"reliable": True, "pages": [1]},
    lines=[line("Espaco livre", 1, 200, 50)],
    words=[], strong_markers=[], visual_markers=[], raster_components=[],
  )
  roles = {slot["role"] for slot in result["responseSlotHypotheses"]}
  check("espaco.no_field", "response_field" not in roles, roles)
  check("espaco.no_slots", result["responseSlotHypotheses"] == [], result["responseSlotHypotheses"])


def test_rendered_visual_circles() -> None:
  image = Image.new("L", (160, 300), 255)
  draw = ImageDraw.Draw(image)
  for index in range(3):
    draw.ellipse([50, 40 + index * 60, 80, 70 + index * 60], outline=0, width=2)
  result = visual_evidence.analyze_image(image, 160.0, 1)
  check("render.circles", len(result["evidence"]) == 3, result["evidence"])
  check("render.glyph_unknown", all(item["enclosedGlyph"] == "unknown" for item in result["evidence"]), result["evidence"])


def test_internal_then_circles() -> None:
  lines = [
    line("a) primeiro item", 1, 100, 50),
    line("b) segundo item", 1, 130, 50),
    line("c) terceiro item", 1, 160, 50),
    line("assinale a opcao correta", 1, 200, 50),
  ]
  circles = [visual(1, 50, 240 + index * 50) for index in range(3)]
  result = regions.discover_response_regions(
    boundary={"reliable": True, "pages": [1]},
    lines=lines, words=[], strong_markers=[], visual_markers=circles, raster_components=[],
  )
  pattern = result["questionResponsePattern"]["pattern"]
  check("internal.then_options", pattern == "internal_enumeration_then_options", pattern)


def test_collapsed_words_grid() -> None:
  words = [
    word("(a)", 1, 50, 100), word("(b)", 1, 400, 100),
    word("(c)", 1, 50, 300), word("(d)", 1, 400, 300),
    word("(e)", 1, 225, 500),
  ]
  cells = observations.resegment_words_into_cells(words, region={"page": 1, "top": 0, "bottom": 600})
  check("grid.cells", len(cells) == 5, cells)
  check("grid.columns", len({cell["column"] for cell in cells}) == 3, cells)
  check("grid.rows", len({cell["row"] for cell in cells}) == 3, cells)


def test_stem_media_not_option() -> None:
  circles = [visual(1, 50, 300 + index * 60) for index in range(3)]
  stem_component = {"page": 1, "bbox": [400, 50, 600, 150], "area": 20000, "width": 200, "height": 100, "fill": 0.4}
  result = regions.discover_response_regions(
    boundary={"reliable": True, "pages": [1]},
    lines=[], words=[], strong_markers=[], visual_markers=circles, raster_components=[stem_component],
  )
  referenced = [index for region in result["observedResponseRegions"] for index in region["visualComponentIndexes"]]
  check("stem.not_option", 0 not in referenced, referenced)
  check("stem.slots", len(result["responseSlotHypotheses"]) == 3, result["responseSlotHypotheses"])


def test_same_parser_independent() -> None:
  slots = [{
    "slotId": 0, "role": "subitem", "label": "A", "contentRegionId": 0,
    "markerObservations": [{"source": "strong", "label": "A"}, {"source": "symbol_control", "label": "C"}],
    "confidence": "medium",
  }]
  result = fusion.fuse_response_evidence({"reliable": True}, {}, {}, {
    "responseSlotHypotheses": slots,
    "observedResponseRegions": [{"regionId": 0, "kind": "text"}],
    "questionResponsePattern": {"pattern": "internal_enumeration", "confidence": "medium"},
  })
  check("sameparser.strong", result["slots"][0]["agreement"] == "strong", result["slots"][0])
  check("sameparser.origins", set(result["slots"][0]["origins"]) == {"textual_marker", "symbol_control"}, result["slots"][0])


def test_derived_spatial_not_double() -> None:
  slots = [{
    "slotId": 0, "role": "answer_option", "label": None, "contentRegionId": 0,
    "markerObservations": [{"source": "rendered_visual", "visualIndex": 0}],
    "confidence": "medium",
  }]
  result = fusion.fuse_response_evidence(
    {"reliable": True}, {},
    {"visualAlternativeEvidence": [{"confidence": "high"}]},
    {"responseSlotHypotheses": slots, "observedResponseRegions": [{"regionId": 0, "kind": "media"}],
     "questionResponsePattern": {"pattern": "one_per_option", "confidence": "medium"}},
  )
  check("derived.partial", result["slots"][0]["agreement"] == "partial", result["slots"][0])
  check("derived.origin", result["slots"][0]["origins"] == ["visual_marker"], result["slots"][0])


def main() -> None:
  test_instruction_context()
  test_espaco_livre_not_field()
  test_rendered_visual_circles()
  test_internal_then_circles()
  test_collapsed_words_grid()
  test_stem_media_not_option()
  test_same_parser_independent()
  test_derived_spatial_not_double()
  if FAILURES:
    print(f"\n{len(FAILURES)} checks falharam: {FAILURES}")
    raise SystemExit(1)
  print("\nTodos os checks da camada de observacoes passaram.")


if __name__ == "__main__":
  main()
