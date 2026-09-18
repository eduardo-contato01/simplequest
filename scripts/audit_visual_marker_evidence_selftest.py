from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from PIL import Image, ImageDraw  # noqa: E402

import audit_visual_marker_evidence as visual  # noqa: E402

FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
  if condition:
    print(f"PASS {name}")
  else:
    print(f"FAIL {name} {detail}")
    FAILURES.append(name)


def canvas(width: int, height: int) -> Image.Image:
  return Image.new("L", (width, height), 255)


def draw_ring(draw: ImageDraw.ImageDraw, cx: float, cy: float, diameter: float, thickness: int = 2) -> None:
  half = diameter / 2.0
  draw.ellipse([cx - half, cy - half, cx + half, cy + half], outline=0, width=thickness)


def draw_disk(draw: ImageDraw.ImageDraw, cx: float, cy: float, diameter: float) -> None:
  half = diameter / 2.0
  draw.ellipse([cx - half, cy - half, cx + half, cy + half], fill=0)


def analyze(image: Image.Image, dpi: float = visual.REFERENCE_DPI) -> tuple[list, list, bool]:
  result = visual.analyze_image(image, dpi, 1)
  hypotheses, ambiguous = visual.build_response_set_hypotheses(result["evidence"], [])
  return result["evidence"], hypotheses, ambiguous


def test_five_outline_rings() -> None:
  image = canvas(120, 300)
  draw = ImageDraw.Draw(image)
  for index in range(5):
    draw_ring(draw, 45, 40 + index * 55, 30)
  evidence, hypotheses, ambiguous = analyze(image)
  check("rings5.evidence", len(evidence) == 5, evidence)
  check("rings5.fill", all(item["fill"] == "outline" for item in evidence), evidence)
  check("rings5.hypotheses", len(hypotheses) == 1, hypotheses)
  check("rings5.support", hypotheses and hypotheses[0]["support"] == 5, hypotheses)
  check("rings5.not_ambiguous", ambiguous is False, ambiguous)


def test_four_filled_disks() -> None:
  image = canvas(120, 250)
  draw = ImageDraw.Draw(image)
  for index in range(4):
    draw_disk(draw, 45, 40 + index * 55, 30)
  evidence, hypotheses, ambiguous = analyze(image)
  check("filled4.evidence", len(evidence) == 4, evidence)
  check("filled4.fill", all(item["fill"] == "filled" for item in evidence), evidence)
  check("filled4.hypotheses", len(hypotheses) == 1, hypotheses)
  check("filled4.support", hypotheses and hypotheses[0]["support"] == 4, hypotheses)


def test_letter_inside_outline_stays_outline() -> None:
  image = canvas(120, 300)
  draw = ImageDraw.Draw(image)
  for index in range(3):
    cy = 50 + index * 60
    draw_ring(draw, 45, cy, 30)
    draw.line([(41, cy + 5), (45, cy - 5)], fill=0, width=1)
    draw.line([(45, cy - 5), (49, cy + 5)], fill=0, width=1)
    draw.line([(42, cy + 2), (48, cy + 2)], fill=0, width=1)
  evidence, hypotheses, ambiguous = analyze(image)
  check("letter.evidence", len(evidence) == 3, evidence)
  check("letter.fill_outline", all(item["fill"] == "outline" for item in evidence), evidence)
  check("letter.hypotheses", len(hypotheses) == 1, hypotheses)


def test_isolated_ring_no_hypothesis() -> None:
  image = canvas(100, 100)
  draw_ring(ImageDraw.Draw(image), 50, 50, 30)
  evidence, hypotheses, ambiguous = analyze(image)
  check("isolated.evidence", len(evidence) == 1, evidence)
  check("isolated.no_hypothesis", hypotheses == [], hypotheses)


def test_two_rings_no_hypothesis() -> None:
  image = canvas(100, 180)
  draw = ImageDraw.Draw(image)
  draw_ring(draw, 45, 45, 30)
  draw_ring(draw, 45, 120, 30)
  evidence, hypotheses, ambiguous = analyze(image)
  check("pair.evidence", len(evidence) == 2, evidence)
  check("pair.no_hypothesis", hypotheses == [], hypotheses)


def test_scattered_graph_points_no_hypothesis() -> None:
  image = canvas(400, 340)
  draw = ImageDraw.Draw(image)
  xs = [25, 90, 160, 230, 300, 370]
  ys = [30, 90, 150, 210, 270, 320]
  for x, y in zip(xs, ys):
    draw_ring(draw, x, y, 30)
  evidence, hypotheses, ambiguous = analyze(image)
  check("scattered.no_hypothesis", hypotheses == [], hypotheses)


def test_two_plausible_clusters_ambiguous() -> None:
  image = canvas(220, 260)
  draw = ImageDraw.Draw(image)
  for index in range(3):
    draw_ring(draw, 45, 40 + index * 55, 30)
    draw_ring(draw, 150, 40 + index * 55, 30)
  evidence, hypotheses, ambiguous = analyze(image)
  check("clusters.hypotheses", len(hypotheses) == 2, hypotheses)
  check("clusters.ambiguous", ambiguous is True, ambiguous)
  check("clusters.supports", all(item["support"] == 3 for item in hypotheses), hypotheses)


def test_partially_broken_ring() -> None:
  image = canvas(100, 120)
  draw = ImageDraw.Draw(image)
  draw.arc([35, 35, 65, 65], start=20, end=300, fill=0, width=2)
  evidence, hypotheses, ambiguous = analyze(image)
  check("broken.no_hypothesis", hypotheses == [], hypotheses)


def test_long_frame_lines_rejected() -> None:
  image = canvas(300, 200)
  draw = ImageDraw.Draw(image)
  draw.line([(5, 15), (295, 15)], fill=0, width=2)
  draw.line([(5, 15), (5, 185)], fill=0, width=2)
  draw.line([(295, 15), (295, 185)], fill=0, width=2)
  evidence, hypotheses, ambiguous = analyze(image)
  check("frame.evidence_empty", evidence == [], evidence)


def test_dpi_normalization_equivalence() -> None:
  low = canvas(120, 300)
  draw_low = ImageDraw.Draw(low)
  for index in range(5):
    draw_ring(draw_low, 45, 40 + index * 55, 30)
  high = canvas(150, 375)
  draw_high = ImageDraw.Draw(high)
  for index in range(5):
    draw_ring(draw_high, 56, 50 + index * 69, 37.5)
  _, low_hypotheses, _ = analyze(low, dpi=160)
  _, high_hypotheses, _ = analyze(high, dpi=200)
  check("dpi.low", low_hypotheses and low_hypotheses[0]["support"] == 5, low_hypotheses)
  check("dpi.high", high_hypotheses and high_hypotheses[0]["support"] == 5, high_hypotheses)


def main() -> None:
  test_five_outline_rings()
  test_four_filled_disks()
  test_letter_inside_outline_stays_outline()
  test_isolated_ring_no_hypothesis()
  test_two_rings_no_hypothesis()
  test_scattered_graph_points_no_hypothesis()
  test_two_plausible_clusters_ambiguous()
  test_partially_broken_ring()
  test_long_frame_lines_rejected()
  test_dpi_normalization_equivalence()
  if FAILURES:
    print(f"\n{len(FAILURES)} checks falharam: {FAILURES}")
    raise SystemExit(1)
  print("\nTodos os checks da camada de evidencia visual passaram.")


if __name__ == "__main__":
  main()
