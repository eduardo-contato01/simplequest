from __future__ import annotations

import math
from pathlib import Path
from statistics import mean, median
from typing import Any

try:
  from PIL import Image
except Exception:  # pragma: no cover
  Image = None


REFERENCE_DPI = 160.0
FIXED_THRESHOLD = 128
THRESHOLD_CLAMP = (150, 200)
THRESHOLD_METHOD = "otsu"

NORMALIZED_DIAMETER_MIN = 24.0
NORMALIZED_DIAMETER_MAX = 42.0

ASPECT_MIN = 0.78
ASPECT_MAX = 1.4

MIN_COMPONENT_AREA = 18

RING_DENSITY_MIN = 0.12
CENTER_FRACTION = 0.5
OUTLINE_TOTAL_MAX = 0.45
OUTLINE_CENTER_MAX = 0.45
FILLED_TOTAL_MIN = 0.5
FILLED_CENTER_MIN = 0.5

X_ALIGN_TOL_RATIO = 0.6
SIZE_TOL_RATIO = 0.35
MIN_CLUSTER_SUPPORT = 3


CONFIDENCE_HIGH_ASPECT = 1.2
CONFIDENCE_HIGH_DIAM_MIN = 25.0
CONFIDENCE_HIGH_DIAM_MAX = 36.0


def otsu_threshold(histogram: list[int]) -> int:
  total = sum(histogram)
  if total <= 0:
    return FIXED_THRESHOLD
  sum_all = sum(index * count for index, count in enumerate(histogram))
  weight_background = 0
  sum_background = 0
  best = 0.0
  threshold = FIXED_THRESHOLD
  for level in range(256):
    weight_background += histogram[level]
    if weight_background == 0:
      continue
    weight_foreground = total - weight_background
    if weight_foreground == 0:
      break
    sum_background += level * histogram[level]
    mean_background = sum_background / weight_background
    mean_foreground = (sum_all - sum_background) / weight_foreground
    between = weight_background * weight_foreground * (mean_background - mean_foreground) ** 2
    if between > best:
      best = between
      threshold = level
  low, high = THRESHOLD_CLAMP
  return min(max(threshold, low), high)


def binarize(gray: "Image.Image") -> tuple[bytearray, int, int, int]:
  width, height = gray.size
  histogram = gray.histogram()
  threshold = otsu_threshold(histogram) if THRESHOLD_METHOD == "otsu" else FIXED_THRESHOLD
  pixels = gray.load()
  binary = bytearray(width * height)
  for y in range(height):
    row = y * width
    for x in range(width):
      if pixels[x, y] < threshold:
        binary[row + x] = 1
  return binary, width, height, threshold


def connected_components(binary: bytearray, width: int, height: int) -> list[tuple[int, int, int, int, int]]:
  visited = bytearray(width * height)
  components: list[tuple[int, int, int, int, int]] = []
  for start in range(width * height):
    if not binary[start] or visited[start]:
      continue
    stack = [start]
    visited[start] = 1
    area = 0
    min_x = width
    max_x = -1
    min_y = height
    max_y = -1
    while stack:
      index = stack.pop()
      y = index // width
      x = index - y * width
      area += 1
      if x < min_x:
        min_x = x
      if x > max_x:
        max_x = x
      if y < min_y:
        min_y = y
      if y > max_y:
        max_y = y
      neighbors = (
        (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1),
        (x - 1, y - 1), (x + 1, y - 1), (x - 1, y + 1), (x + 1, y + 1),
      )
      for nx, ny in neighbors:
        if 0 <= nx < width and 0 <= ny < height:
          neighbor = ny * width + nx
          if binary[neighbor] and not visited[neighbor]:
            visited[neighbor] = 1
            stack.append(neighbor)
    components.append((area, min_x, min_y, max_x - min_x + 1, max_y - min_y + 1))
  return components


def _density(binary: bytearray, width: int, x0: int, y0: int, x1: int, y1: int) -> tuple[int, int]:
  dark = 0
  for y in range(y0, y1):
    row = y * width
    for x in range(x0, x1):
      dark += binary[row + x]
  return dark, max(1, (x1 - x0) * (y1 - y0))


def _candidate_metrics(binary: bytearray, width: int, component: tuple[int, int, int, int, int], dpi: float) -> dict[str, Any] | None:
  area, x, y, w, h = component
  if area < MIN_COMPONENT_AREA:
    return None
  aspect = w / h if h else 0.0
  if not (ASPECT_MIN <= aspect <= ASPECT_MAX):
    return None
  diameter = (w + h) / 2.0
  diameter_normalized = diameter / max(dpi, 1.0) * REFERENCE_DPI
  if not (NORMALIZED_DIAMETER_MIN <= diameter_normalized <= NORMALIZED_DIAMETER_MAX):
    return None
  total_dark, total_area = _density(binary, width, x, y, x + w, y + h)
  total_density = total_dark / total_area
  center_w = max(1, int(round(w * CENTER_FRACTION)))
  center_h = max(1, int(round(h * CENTER_FRACTION)))
  center_x0 = x + (w - center_w) // 2
  center_y0 = y + (h - center_h) // 2
  center_dark, center_area = _density(binary, width, center_x0, center_y0, center_x0 + center_w, center_y0 + center_h)
  center_density = center_dark / center_area
  ring_dark = total_dark - center_dark
  ring_area = max(1, total_area - center_area)
  ring_density = ring_dark / ring_area

  if total_density <= OUTLINE_TOTAL_MAX and ring_density >= RING_DENSITY_MIN and center_density <= OUTLINE_CENTER_MAX:
    fill = "outline"
  elif total_density >= FILLED_TOTAL_MIN and center_density >= FILLED_CENTER_MIN:
    fill = "filled"
  else:
    return None

  evidence = ["aspect_ok", "size_normalized", "ring_like" if fill == "outline" else "disk_like"]
  confidence = "high" if (
    aspect <= CONFIDENCE_HIGH_ASPECT
    and CONFIDENCE_HIGH_DIAM_MIN <= diameter_normalized <= CONFIDENCE_HIGH_DIAM_MAX
  ) else "medium"
  return {
    "width": w,
    "height": h,
    "aspectRatio": round(aspect, 4),
    "diameterNormalized": round(diameter_normalized, 4),
    "fill": fill,
    "ringDensity": round(ring_density, 4),
    "centerDensity": round(center_density, 4),
    "totalDensity": round(total_density, 4),
    "confidence": confidence,
    "evidence": evidence,
  }


def detect_candidates(
  binary: bytearray,
  width: int,
  height: int,
  dpi: float,
  page: int,
  offset: tuple[int, int],
  components: list[tuple[int, int, int, int, int]] | None = None,
) -> list[dict[str, Any]]:
  evidence: list[dict[str, Any]] = []
  for component in (components if components is not None else connected_components(binary, width, height)):
    metrics = _candidate_metrics(binary, width, component, dpi)
    if metrics is None:
      continue
    area, x, y, w, h = component
    evidence.append({
      "page": page,
      "bbox": [x + offset[0], y + offset[1], x + w + offset[0], y + h + offset[1]],
      "shape": "circle",
      "fill": metrics["fill"],
      "enclosedGlyph": "unknown",
      "source": "raster_geometry",
      "confidence": metrics["confidence"],
      "metrics": {
        "widthNormalized": round(w / max(dpi, 1.0) * REFERENCE_DPI, 4),
        "heightNormalized": round(h / max(dpi, 1.0) * REFERENCE_DPI, 4),
        "aspectRatio": metrics["aspectRatio"],
        "diameterNormalized": metrics["diameterNormalized"],
        "ringDensity": metrics["ringDensity"],
        "centerDensity": metrics["centerDensity"],
        "totalDensity": metrics["totalDensity"],
      },
      "nearestOcrLineIndex": None,
      "nearestOcrLineText": None,
      "nearestOcrDistance": None,
      "evidence": list(metrics["evidence"]),
    })
  return evidence


def associate_with_ocr(evidence: list[dict[str, Any]], ocr_lines: list[dict[str, Any]]) -> None:
  if not ocr_lines:
    return
  for item in evidence:
    bx0, by0, bx1, by1 = item["bbox"]
    cx = (bx0 + bx1) / 2.0
    cy = (by0 + by1) / 2.0
    best = None
    best_distance = None
    for line in ocr_lines:
      if int(line.get("page") or 0) != int(item["page"]):
        continue
      if line.get("bbox") is not None:
        raw = line.get("bbox")
      elif line.get("x0") is not None:
        raw = (line.get("x0"), line.get("top"), line.get("x1"), line.get("bottom"))
      else:
        continue
      try:
        lx0, ly0, lx1, ly1 = (float(v or 0) for v in raw)
      except Exception:
        continue
      dy = max(ly0 - cy, cy - ly1, 0.0)
      dx = max(lx0 - cx, cx - lx1, 0.0)
      distance = math.hypot(dx, dy)
      if best_distance is None or distance < best_distance:
        best_distance = distance
        best = line
    if best is not None:
      item["nearestOcrLineIndex"] = best.get("lineIndex")
      item["nearestOcrLineText"] = best.get("text")
      item["nearestOcrDistance"] = round(float(best_distance), 4)
      item["evidence"].append("ocr_line_associated")


def build_response_set_hypotheses(evidence: list[dict[str, Any]], ocr_lines: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], bool]:
  by_page: dict[int, list[dict[str, Any]]] = {}
  for index, item in enumerate(evidence):
    by_page.setdefault(int(item["page"]), []).append((index, item))
  clusters: list[list[tuple[int, dict[str, Any]]]] = []
  for page in sorted(by_page):
    items = sorted(by_page[page], key=lambda pair: (pair[1]["bbox"][1], pair[1]["bbox"][0]))
    open_clusters: list[list[tuple[int, dict[str, Any]]]] = []
    for pair in items:
      placed = False
      for cluster in open_clusters:
        last = cluster[-1][1]
        if pair[1]["bbox"][1] < last["bbox"][3] - 2:
          continue
        diameters = [entry[1]["metrics"]["diameterNormalized"] for entry in cluster]
        median_diameter = median(diameters)
        tolerance = max(6.0, X_ALIGN_TOL_RATIO * median_diameter)
        if abs(pair[1]["bbox"][0] - median([entry[1]["bbox"][0] for entry in cluster])) > tolerance:
          continue
        if abs(pair[1]["metrics"]["diameterNormalized"] - median_diameter) > SIZE_TOL_RATIO * median_diameter:
          continue
        cluster.append(pair)
        placed = True
        break
      if not placed:
        open_clusters.append([pair])
    clusters.extend(open_clusters)

  hypotheses: list[dict[str, Any]] = []
  for cluster in clusters:
    if len(cluster) < MIN_CLUSTER_SUPPORT:
      continue
    items = [entry[1] for entry in cluster]
    indexes = [entry[0] for entry in cluster]
    x_values = [item["bbox"][0] for item in items]
    diameters = [item["metrics"]["diameterNormalized"] for item in items]
    gaps = [
      items[i + 1]["bbox"][1] - items[i]["bbox"][3]
      for i in range(len(items) - 1)
    ]
    median_diameter = median(diameters) or 1.0
    x_spread = max(x_values) - min(x_values)
    alignment_score = max(0.0, 1.0 - x_spread / max(6.0, X_ALIGN_TOL_RATIO * median_diameter))
    size_spread = max(diameters) - min(diameters)
    size_consistency = max(0.0, 1.0 - size_spread / median_diameter)
    if gaps:
      positive = [gap for gap in gaps if gap >= 0]
      gap_mean = mean(positive) if positive else 0.0
      if gap_mean > 0:
        gap_std = math.sqrt(sum((gap - gap_mean) ** 2 for gap in positive) / len(positive))
        spacing_consistency = max(0.0, 1.0 - gap_std / gap_mean)
      else:
        spacing_consistency = 0.0
    else:
      spacing_consistency = 0.0
    fill_counter: dict[str, int] = {}
    for item in items:
      fill_counter[item["fill"]] = fill_counter.get(item["fill"], 0) + 1
    dominant_fill, dominant_count = max(fill_counter.items(), key=lambda entry: entry[1])
    fill_consistency = dominant_count / len(items)
    associated = sum(1 for item in items if item.get("nearestOcrLineIndex") is not None)
    adjacent_content = associated / len(items)

    evidence_list = [f"support:{len(items)}", f"fill:{dominant_fill}"]
    if alignment_score >= 0.6:
      evidence_list.append("aligned_x")
    if size_consistency >= 0.6:
      evidence_list.append("consistent_size")
    if spacing_consistency >= 0.5:
      evidence_list.append("plausible_spacing")
    if adjacent_content >= 0.6:
      evidence_list.append("adjacent_content")

    if len(items) >= 5 and alignment_score >= 0.6 and size_consistency >= 0.5:
      confidence = "high"
    elif len(items) >= MIN_CLUSTER_SUPPORT:
      confidence = "medium"
    else:
      confidence = "low"

    hypotheses.append({
      "markerIndexes": indexes,
      "pages": sorted({int(item["page"]) for item in items}),
      "support": len(items),
      "alignmentScore": round(alignment_score, 4),
      "sizeConsistency": round(size_consistency, 4),
      "spacingConsistency": round(spacing_consistency, 4),
      "fillConsistency": round(fill_consistency, 4),
      "adjacentContentEvidence": round(adjacent_content, 4),
      "dominantFill": dominant_fill,
      "confidence": confidence,
      "ambiguous": False,
      "evidence": evidence_list,
    })

  hypotheses.sort(key=lambda item: (item["support"], item["confidence"]), reverse=True)
  ambiguous = len(hypotheses) > 1
  for hypothesis in hypotheses:
    hypothesis["ambiguous"] = ambiguous
  return hypotheses, ambiguous


def analyze_raw_components(
  image: "Image.Image",
  page: int,
  offset: tuple[int, int] = (0, 0),
  min_area: int = 30,
) -> list[dict[str, Any]]:
  # Generic, unopinionated raster components for downstream region discovery.
  # It makes no decision about media/options; callers interpret them.
  gray = image.convert("L")
  binary, width, height, _ = binarize(gray)
  raw = _raw_from_components(connected_components(binary, width, height), page, offset)
  return [component for component in raw if component["area"] >= min_area]


def _raw_from_components(
  components: list[tuple[int, int, int, int, int]],
  page: int,
  offset: tuple[int, int],
  min_area: int = 30,
) -> list[dict[str, Any]]:
  result: list[dict[str, Any]] = []
  for area, x, y, w, h in components:
    if area < min_area:
      continue
    result.append({
      "page": page,
      "bbox": [x + offset[0], y + offset[1], x + w + offset[0], y + h + offset[1]],
      "area": area,
      "width": w,
      "height": h,
      "fill": round(area / max(1, w * h), 4),
    })
  return result


def analyze_image(
  image: "Image.Image",
  dpi: float,
  page: int,
  ocr_lines: list[dict[str, Any]] | None = None,
  offset: tuple[int, int] = (0, 0),
) -> dict[str, Any]:
  gray = image.convert("L")
  binary, width, height, threshold = binarize(gray)
  components = connected_components(binary, width, height)
  evidence = detect_candidates(binary, width, height, dpi, page, offset, components=components)
  associate_with_ocr(evidence, ocr_lines or [])
  raw = _raw_from_components(components, page, offset)
  return {"evidence": evidence, "rawComponents": raw, "thresholdValue": threshold, "width": width, "height": height}


def analyze_question_region(
  region_lines: list[dict[str, Any]],
  image_paths: dict[int, str],
  page_geometry: dict[int, dict[str, Any]],
  dpi: float,
  padding: int = 6,
) -> dict[str, Any]:
  by_page: dict[int, list[dict[str, Any]]] = {}
  for line in region_lines:
    by_page.setdefault(int(line.get("page") or 0), []).append(line)

  all_evidence: list[dict[str, Any]] = []
  all_raw: list[dict[str, Any]] = []
  geometry_report: list[dict[str, Any]] = []
  for page in sorted(by_page):
    lines = by_page[page]
    image_path = image_paths.get(page)
    if not image_path or not Path(image_path).exists() or Image is None:
      continue
    x_values = [float(line.get("x0") or 0) for line in lines]
    x1_values = [float(line.get("x1") or 0) for line in lines]
    top_values = [float(line.get("top") or 0) for line in lines]
    bottom_values = [float(line.get("bottom") or 0) for line in lines]
    x0 = max(0, int(math.floor(min(x_values))) - padding)
    y0 = max(0, int(math.floor(min(top_values))) - padding)
    x1 = int(math.ceil(max(x1_values))) + padding
    y1 = int(math.ceil(max(bottom_values))) + padding
    with Image.open(image_path) as image:
      image_width, image_height = image.size
      x1 = min(x1, image_width)
      y1 = min(y1, image_height)
      crop = image.crop((x0, y0, x1, y1))
      page_result = analyze_image(crop, dpi, page, ocr_lines=lines, offset=(x0, y0))
    all_evidence.extend(page_result["evidence"])
    all_raw.extend(page_result["rawComponents"])
    geometry = page_geometry.get(page) or {}
    pdf_width = geometry.get("pdfWidth")
    pdf_height = geometry.get("pdfHeight")
    geometry_report.append({
      "page": page,
      "imageWidth": image_width,
      "imageHeight": image_height,
      "pdfWidth": pdf_width,
      "pdfHeight": pdf_height,
      "dpi": dpi,
      "scaleX": round(image_width / pdf_width, 6) if pdf_width else None,
      "scaleY": round(image_height / pdf_height, 6) if pdf_height else None,
      "crop": [x0, y0, x1, y1],
      "thresholdValue": page_result["thresholdValue"],
    })

  hypotheses, ambiguous = build_response_set_hypotheses(all_evidence, region_lines)
  return {
    "visualAlternativeEvidence": all_evidence,
    "visualResponseSetHypotheses": hypotheses,
    "visualResponseSetAmbiguous": ambiguous,
    "visualPageGeometry": geometry_report,
    "visualRawComponents": all_raw,
  }


