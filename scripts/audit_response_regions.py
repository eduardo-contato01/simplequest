from __future__ import annotations

import re
from dataclasses import dataclass, field
from statistics import median
from typing import Any


INSTRUCTION_RE = re.compile(
  r"\b(assinale|assinalar|correta|correto|julgue|julgar|op[çc][ãa]o|op[çc][õo]es|letra|"
  r"responda|responde|marque|indique|certo ou errado|verdadeiro ou falso|afirmativa|afirma[çc][ãa]o)\b",
  re.IGNORECASE,
)
PARENT_CHILD_LINE_RE = re.compile(r"^\s*(\d{1,3})\s*[-–—]\s*([A-Ea-e])\b")
ROMAN_LINE_RE = re.compile(r"^\s*\(?\s*(I{1,3}|IV|V)\s*(?:[\)\.\-–—:]\s*|\s+(?=[A-ZÀ-Ý(]))\S")
LOWER_ENUM_LINE_RE = re.compile(r"^\s*\(?\s*([a-e])\s*[\)\.\-–—:]\s*\S")
NUMERIC_ENUM_LINE_RE = re.compile(r"^\s*\(?\s*(\d{1,2})\s*[\)\.\-–—:]\s*\S")

SHORT_WORD_MAX = 4
WEAK_X_TOL = 6.0
WEAK_MIN_COUNT = 3
WEAK_NEIGHBOR_MAX_GAP = 60.0
X_TOL = 14.0
CONTROL_PAIR_DX_RATIO = 3.0
CONTROL_PAIR_DY_TOL = 6.0
CONTROL_MIN_ROWS = 3
MIN_SINGLE_COLUMN = 3
GRID_MIN_COLUMNS = 2
GRID_MIN_ROWS = 2
BAR_RATIO_MIN = 8.0
BAR_HEIGHT_MAX = 7.0
RASTER_MEDIA_MIN_AREA = 400


@dataclass
class ObservedResponseRegion:
  regionId: int
  page: int
  bbox: list[float]
  columnBand: int
  kind: str
  lineIndexes: list[int] = field(default_factory=list)
  wordIndexes: list[int] = field(default_factory=list)
  visualComponentIndexes: list[int] = field(default_factory=list)
  confidence: str = "low"
  evidence: list[str] = field(default_factory=list)

  def to_dict(self) -> dict[str, Any]:
    return {
      "regionId": self.regionId,
      "page": self.page,
      "bbox": [round(value, 2) for value in self.bbox],
      "columnBand": self.columnBand,
      "kind": self.kind,
      "lineIndexes": self.lineIndexes,
      "wordIndexes": self.wordIndexes,
      "visualComponentIndexes": self.visualComponentIndexes,
      "confidence": self.confidence,
      "evidence": self.evidence,
    }


@dataclass
class ResponseSlotHypothesis:
  slotId: int
  page: int
  bbox: list[float]
  markerObservations: list[dict[str, Any]]
  contentRegionId: int | None
  role: str
  label: str | None
  parentLabel: str | None
  confidence: str
  evidence: list[str] = field(default_factory=list)

  def to_dict(self) -> dict[str, Any]:
    return {
      "slotId": self.slotId,
      "page": self.page,
      "bbox": [round(value, 2) for value in self.bbox],
      "markerObservations": self.markerObservations,
      "contentRegionId": self.contentRegionId,
      "role": self.role,
      "label": self.label,
      "parentLabel": self.parentLabel,
      "confidence": self.confidence,
      "evidence": self.evidence,
    }


@dataclass
class QuestionResponsePattern:
  pattern: str
  slotIds: list[int] = field(default_factory=list)
  confidence: str = "low"
  evidence: list[str] = field(default_factory=list)

  def to_dict(self) -> dict[str, Any]:
    return {
      "pattern": self.pattern,
      "slotIds": self.slotIds,
      "confidence": self.confidence,
      "evidence": self.evidence,
    }


def _center_y(bbox: list[float]) -> float:
  return (float(bbox[1]) + float(bbox[3])) / 2.0


def _center_x(bbox: list[float]) -> float:
  return (float(bbox[0]) + float(bbox[2])) / 2.0


def _overlap(a0: float, a1: float, b0: float, b1: float) -> float:
  return max(0.0, min(a1, b1) - max(a0, b0))


def _anchor_from_marker(marker: dict[str, Any]) -> dict[str, Any]:
  return {
    "source": marker.get("source") or "strong",
    "kind": marker.get("markerKind"),
    "label": marker.get("label"),
    "labelCase": marker.get("labelCase"),
    "subitemLabel": marker.get("subitemLabel"),
    "parentQuestion": marker.get("parentQuestion"),
    "markerShape": marker.get("markerShape"),
    "separator": marker.get("separator"),
    "responseField": marker.get("responseField"),
    "text": marker.get("text") or "",
    "page": int(marker.get("page") or 0),
    "bbox": [float(value) for value in marker.get("bbox") or (0, 0, 0, 0)],
    "lineIndex": marker.get("lineIndex"),
  }


def _anchor_from_visual(item: dict[str, Any], index: int) -> dict[str, Any]:
  return {
    "source": "visual",
    "kind": "visual_circle",
    "label": None,
    "labelCase": None,
    "subitemLabel": None,
    "parentQuestion": None,
    "markerShape": item.get("shape") or "circle",
    "separator": None,
    "responseField": "absent",
    "text": "",
    "page": int(item.get("page") or 0),
    "bbox": [float(value) for value in item.get("bbox") or (0, 0, 0, 0)],
    "lineIndex": None,
    "visualIndex": index,
    "fill": item.get("fill"),
  }


def _detect_weak_anchors(lines: list[dict[str, Any]], used_line_indexes: set[Any]) -> list[dict[str, Any]]:
  candidates = [
    line for line in lines
    if line.get("lineIndex") not in used_line_indexes
    and len(str(line.get("text") or "").split()) <= SHORT_WORD_MAX
    and str(line.get("text") or "").strip()
  ]
  if not candidates:
    return []
  by_page: dict[int, list[dict[str, Any]]] = {}
  for line in candidates:
    by_page.setdefault(int(line.get("page") or 0), []).append(line)
  page_lines: dict[int, list[dict[str, Any]]] = {}
  for line in lines:
    page_lines.setdefault(int(line.get("page") or 0), []).append(line)

  qualifying: list[tuple[float, list[dict[str, Any]]]] = []
  for page, page_candidates in by_page.items():
    tops = [float(line.get("top") or 0) for line in page_lines.get(page, [])]
    bottoms = [float(line.get("bottom") or 0) for line in page_lines.get(page, [])]
    if not tops or not bottoms:
      continue
    top_all = min(tops)
    span = max(bottoms) - top_all
    groups: dict[int, list[dict[str, Any]]] = {}
    for line in page_candidates:
      key = int(round(float(line.get("x0") or 0) / WEAK_X_TOL))
      groups.setdefault(key, []).append(line)
    for group in groups.values():
      ordered = sorted(group, key=lambda line: float(line.get("top") or 0))
      if len(ordered) < WEAK_MIN_COUNT:
        continue
      x_values = [float(line.get("x0") or 0) for line in ordered]
      if max(x_values) - min(x_values) > WEAK_X_TOL:
        continue
      if span > 0 and ordered[0]["top"] < top_all + 0.3 * span:
        continue
      if len(ordered) > 10:
        continue
      if any(INSTRUCTION_RE.search(str(line.get("text") or "")) for line in ordered):
        continue
      qualifying.append((median(x_values), ordered))
  # Keep only the leftmost qualifying column: weak anchors are a last-resort
  # fallback for the answer-marker column, not for every repeated short column.
  weak: list[dict[str, Any]] = []
  if qualifying:
    qualifying.sort(key=lambda entry: (entry[1][0].get("page"), entry[0]))
    for line in qualifying[0][1]:
      weak.append({
        "source": "weak",
        "kind": "weak_region_anchor",
        "label": None,
        "labelCase": None,
        "subitemLabel": None,
        "parentQuestion": None,
        "markerShape": None,
        "separator": None,
        "responseField": "absent",
        "text": line.get("text") or "",
        "page": int(line.get("page") or 0),
        "bbox": [float(line.get("x0") or 0), float(line.get("top") or 0), float(line.get("x1") or 0), float(line.get("bottom") or 0)],
        "lineIndex": line.get("lineIndex"),
        "weakAnchorReason": f"short_repeated_column:{len(qualifying[0][1])}",
      })
  return weak


def _detect_single_letter_anchors(words: list[dict[str, Any]]) -> list[dict[str, Any]]:
  candidates: list[dict[str, Any]] = []
  for word in words:
    text = str(word.get("text") or "").strip()
    if len(text) == 1 and text.isupper() and text in list("ABCDE"):
      candidates.append(word)
  if len(candidates) < 3:
    return []
  by_page: dict[int, list[dict[str, Any]]] = {}
  for word in candidates:
    by_page.setdefault(int(word.get("page") or 0), []).append(word)
  for page, page_candidates in by_page.items():
    groups: dict[int, list[dict[str, Any]]] = {}
    for word in page_candidates:
      key = int(round(float(word.get("bbox")[0]) / WEAK_X_TOL))
      groups.setdefault(key, []).append(word)
    for group in groups.values():
      ordered = sorted(group, key=lambda word: float(word.get("bbox")[1]))
      # Greedy longest consecutive run A, B, C, ... so that stray single
      # letters from surrounding text do not break the option column.
      run: list[dict[str, Any]] = []
      expected = 0
      for word in ordered:
        label = str(word.get("text") or "").strip().upper()
        if expected < len("ABCDE") and label == "ABCDE"[expected]:
          run.append(word)
          expected += 1
      if len(run) < 3:
        continue
      x_values = [float(word.get("bbox")[0]) for word in run]
      if max(x_values) - min(x_values) > WEAK_X_TOL:
        continue
      ordered = run
      labels = [str(word.get("text") or "").strip().upper() for word in ordered]
      anchors: list[dict[str, Any]] = []
      for word, label in zip(ordered, labels):
        bbox = [float(value) for value in word.get("bbox")]
        anchors.append({
          "source": "single_letter",
          "kind": "single_letter_column",
          "label": label,
          "labelCase": "upper",
          "subitemLabel": None,
          "parentQuestion": None,
          "markerShape": None,
          "separator": None,
          "responseField": "absent",
          "text": "",
          "page": int(word.get("page") or 0),
          "bbox": bbox,
          "lineIndex": None,
          "role": "answer_option",
        })
      return anchors
  return []


def _detect_symbol_controls(lines: list[dict[str, Any]]) -> list[dict[str, Any]]:
  # Symbol fonts (e.g. C/E answer controls) are often encoded in the Unicode
  # private-use area; two such glyphs on a parent-child row are response
  # controls, not answer options. Font-agnostic: any PUA glyph qualifies.
  controls: list[dict[str, Any]] = []
  labels = ["C", "E"]
  for line in lines:
    text = str(line.get("text") or "")
    if not PARENT_CHILD_LINE_RE.match(text.strip()):
      continue
    pua = [index for index, char in enumerate(text) if 0xE000 <= ord(char) <= 0xF8FF]
    if len(pua) < 2:
      continue
    x0 = float(line.get("x0") or 0)
    x1 = float(line.get("x1") or 0)
    top = float(line.get("top") or 0)
    bottom = float(line.get("bottom") or 0)
    length = max(1, len(text))
    for position, index in enumerate(pua[:2]):
      control_x = x0 + (index / length) * (x1 - x0)
      controls.append({
        "source": "symbol_control",
        "kind": "response_control",
        "label": labels[position] if position < len(labels) else None,
        "labelCase": "upper",
        "subitemLabel": None,
        "parentQuestion": None,
        "markerShape": None,
        "separator": None,
        "responseField": "absent",
        "text": "",
        "page": int(line.get("page") or 0),
        "bbox": [control_x, top, control_x + 6.0, bottom],
        "lineIndex": line.get("lineIndex"),
        "role": "response_control",
      })
  return controls


def _column_bands(anchors: list[dict[str, Any]]) -> list[int]:
  bands: list[float] = []
  result: list[int] = []
  for anchor in anchors:
    x = float(anchor["bbox"][0])
    assigned = None
    for index, reference in enumerate(bands):
      if abs(x - reference) <= X_TOL:
        assigned = index
        break
    if assigned is None:
      bands.append(x)
      assigned = len(bands) - 1
    result.append(assigned)
  return result


def _line_matches(line: dict[str, Any], regex: re.Pattern[str], used: set[Any]) -> bool:
  if line.get("lineIndex") in used:
    return False
  return bool(regex.match(str(line.get("text") or "").strip()))


def _detect_subitem_lines(lines: list[dict[str, Any]], used: set[Any]) -> list[tuple[int, str, str]]:
  found: list[tuple[int, str, str]] = []
  for line in lines:
    index = line.get("lineIndex")
    if index in used:
      continue
    text = str(line.get("text") or "").strip()
    if ROMAN_LINE_RE.match(text) or LOWER_ENUM_LINE_RE.match(text):
      found.append((index, line.get("text"), "subitem"))
  return found


def _internal_label(text: str) -> str | None:
  roman = ROMAN_LINE_RE.match(text)
  if roman:
    return roman.group(1).upper()
  lower = LOWER_ENUM_LINE_RE.match(text)
  if lower:
    return lower.group(1).upper()
  numeric = NUMERIC_ENUM_LINE_RE.match(text)
  if numeric:
    return numeric.group(1)
  return None


def _build_internal_anchors(lines: list[dict[str, Any]], used: set[Any]) -> list[dict[str, Any]]:
  anchors: list[dict[str, Any]] = []
  for line in lines:
    index = line.get("lineIndex")
    if index in used:
      continue
    text = str(line.get("text") or "").strip()
    if not (ROMAN_LINE_RE.match(text) or LOWER_ENUM_LINE_RE.match(text)):
      continue
    anchors.append({
      "source": "internal",
      "kind": "internal_enumeration",
      "label": _internal_label(text),
      "labelCase": "upper",
      "subitemLabel": _internal_label(text),
      "parentQuestion": None,
      "markerShape": None,
      "separator": None,
      "responseField": "absent",
      "text": line.get("text") or "",
      "page": int(line.get("page") or 0),
      "bbox": [float(line.get("x0") or 0), float(line.get("top") or 0), float(line.get("x1") or 0), float(line.get("bottom") or 0)],
      "lineIndex": index,
      "role": "subitem",
    })
  return anchors


def _find_merge_target(anchors: list[dict[str, Any]], visual_anchor: dict[str, Any]) -> dict[str, Any] | None:
  best: dict[str, Any] | None = None
  best_distance: float | None = None
  vx0 = float(visual_anchor["bbox"][0])
  for anchor in anchors:
    if anchor.get("source") == "visual":
      continue
    if int(anchor["page"]) != int(visual_anchor["page"]):
      continue
    if _overlap(float(anchor["bbox"][1]), float(anchor["bbox"][3]), float(visual_anchor["bbox"][1]), float(visual_anchor["bbox"][3])) <= 0:
      continue
    if vx0 < float(anchor["bbox"][0]) - X_TOL or vx0 > float(anchor["bbox"][2]):
      continue
    distance = abs(_center_x(visual_anchor["bbox"]) - _center_x(anchor["bbox"]))
    if best_distance is None or distance < best_distance:
      best_distance = distance
      best = anchor
  return best


def discover_response_regions(
  boundary: dict[str, Any],
  lines: list[dict[str, Any]],
  words: list[dict[str, Any]] | None,
  strong_markers: list[dict[str, Any]],
  visual_markers: list[dict[str, Any]] | None = None,
  raster_components: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
  visual_markers = visual_markers or []
  raster_components = raster_components or []
  words = words or []
  blockers: list[str] = []
  reliable = bool(boundary.get("reliable", True))
  if not reliable:
    blockers.append("boundary_uncertain")

  used_lines: set[Any] = set()
  text_anchors = [
    _anchor_from_marker(marker)
    for marker in strong_markers
    if marker.get("markerKind") == "answer_marker" and marker.get("label")
  ]
  parent_anchors = [
    _anchor_from_marker(marker)
    for marker in strong_markers
    if marker.get("markerKind") == "parent_child" and marker.get("subitemLabel")
  ]
  for anchor in text_anchors + parent_anchors:
    if anchor.get("lineIndex") is not None:
      used_lines.add(anchor["lineIndex"])
  visual_anchors = [_anchor_from_visual(item, index) for index, item in enumerate(visual_markers)]

  weak_anchors: list[dict[str, Any]] = []
  single_letter_anchors: list[dict[str, Any]] = []
  instruction_tops = [
    float(line.get("top") or 0) for line in lines
    if INSTRUCTION_RE.search(str(line.get("text") or ""))
  ]
  instruction_top = max(instruction_tops) if instruction_tops else None
  lower_run: list[dict[str, Any]] = []
  if instruction_top is not None:
    lower_run = [
      anchor for anchor in text_anchors
      if str(anchor.get("labelCase")) == "lower"
      and str(anchor.get("label") or "").upper() in list("ABC")
      and float(anchor["bbox"][1]) < instruction_top
    ]
    if len(lower_run) >= 2:
      for anchor in lower_run:
        anchor["role"] = "subitem"
        anchor["subitemLabel"] = anchor.get("label")

  if not text_anchors and not parent_anchors and not visual_anchors:
    single_letter_anchors = _detect_single_letter_anchors(words)
    if not single_letter_anchors:
      weak_anchors = _detect_weak_anchors(lines, used_lines)
  weak_diagnostic = [dict(anchor) for anchor in weak_anchors]

  internal_anchors = _build_internal_anchors(lines, used_lines)

  symbol_controls = _detect_symbol_controls(lines)
  primary_anchors = text_anchors + parent_anchors + single_letter_anchors + weak_anchors + internal_anchors + symbol_controls
  leftover_visuals: list[dict[str, Any]] = []
  for visual_anchor in visual_anchors:
    target = _find_merge_target(primary_anchors, visual_anchor)
    if target is not None:
      target.setdefault("additionalObservations", []).append({
        "source": "visual",
        "visualIndex": visual_anchor.get("visualIndex"),
        "fill": visual_anchor.get("fill"),
        "bbox": list(visual_anchor["bbox"]),
      })
      target.setdefault("evidence", []).append("visual_marker_merged")
    else:
      leftover_visuals.append(visual_anchor)

  # A question whose answer markers were read textually should not gain extra
  # option slots from stray raster circles (candidate-level visual false positives).
  # Lowercase stem subitems (a/b/c) do not count as answer markers here.
  effective_text_options = len(text_anchors) - len(lower_run)
  if effective_text_options >= MIN_SINGLE_COLUMN:
    leftover_visuals = []

  anchors = primary_anchors + leftover_visuals
  anchors.sort(key=lambda anchor: (int(anchor["page"]), float(anchor["bbox"][1]), float(anchor["bbox"][0])))

  page_bottom: dict[int, float] = {}
  for line in lines:
    page = int(line.get("page") or 0)
    page_bottom[page] = max(page_bottom.get(page, 0.0), float(line.get("bottom") or 0))

  column_bands = _column_bands(anchors)
  for anchor, band in zip(anchors, column_bands):
    anchor["columnBand"] = band

  # ---- role classification -------------------------------------------------
  rows: dict[tuple[int, int], list[dict[str, Any]]] = {}
  for anchor in visual_anchors:
    row_key = (int(anchor["page"]), int(round(float(anchor["bbox"][1]) / 6.0)))
    rows.setdefault(row_key, []).append(anchor)
  control_pairs = 0
  for row in rows.values():
    if len(row) == 2:
      left, right = sorted(row, key=lambda anchor: float(anchor["bbox"][0]))
      gap = float(right["bbox"][0]) - float(left["bbox"][2])
      diameter = max(1.0, float(left["bbox"][3]) - float(left["bbox"][1]))
      if gap <= CONTROL_PAIR_DX_RATIO * diameter:
        control_pairs += 1
  has_ce_instruction = any(re.search(r"\bC\b.*\bE\b|C\s*\(|assinale\s+C", str(line.get("text") or ""), re.IGNORECASE) for line in lines)
  symbol_pair_rows = len(symbol_controls) // 2
  if symbol_pair_rows >= CONTROL_MIN_ROWS and bool(parent_anchors):
    control_pairs = max(control_pairs, symbol_pair_rows)
  controls_active = control_pairs >= CONTROL_MIN_ROWS and (bool(parent_anchors) or has_ce_instruction)

  internal_lines = _detect_subitem_lines(lines, used_lines)
  internal_present = len(internal_lines) >= 2

  answer_label_anchors = [
    anchor for anchor in text_anchors
    if anchor.get("label") and str(anchor.get("label")).upper() in list("ABCDE")
  ]
  option_anchors = list(answer_label_anchors)
  if visual_anchors and not controls_active:
    option_anchors.extend(visual_anchors)
  if weak_anchors:
    option_anchors.extend(weak_anchors)

  if controls_active:
    for anchor in visual_anchors:
      anchor["role"] = "response_control"
    for anchor in parent_anchors:
      anchor["role"] = "subitem"
      anchor["label"] = anchor.get("subitemLabel")
      anchor["parentLabel"] = str(anchor.get("parentQuestion"))
  for anchor in text_anchors:
    if anchor.get("role"):
      continue
    if anchor.get("responseField") == "present" and not str(anchor.get("text") or "").strip():
      anchor["role"] = "response_field"
    else:
      anchor["role"] = "answer_option"
  for anchor in visual_anchors:
    anchor.setdefault("role", "answer_option")
  for anchor in weak_anchors:
    anchor["role"] = "answer_option"
  for anchor in parent_anchors:
    anchor.setdefault("role", "subitem")
    anchor.setdefault("label", anchor.get("subitemLabel"))
    anchor.setdefault("parentLabel", str(anchor.get("parentQuestion")))

  # ---- regions -------------------------------------------------------------
  regions: list[ObservedResponseRegion] = []
  region_lookup: dict[int, int] = {}
  raster_in_cell_cache: dict[tuple[int, int], list[int]] = {}
  visual_marker_boxes = [[float(value) for value in anchor["bbox"]] for anchor in visual_anchors]

  def _overlaps_visual_marker(component: dict[str, Any]) -> bool:
    cx0, cy0, cx1, cy1 = (float(value) for value in component.get("bbox") or (0, 0, 0, 0))
    component_area = max(1.0, (cx1 - cx0) * (cy1 - cy0))
    for marker_box in visual_marker_boxes:
      overlap_x = _overlap(cx0, cx1, marker_box[0], marker_box[2])
      overlap_y = _overlap(cy0, cy1, marker_box[1], marker_box[3])
      if overlap_x * overlap_y >= 0.5 * component_area:
        return True
    return False

  def _right_limit(anchor: dict[str, Any], band_end: float) -> float:
    limit = float("inf")
    for other in anchors:
      if other is anchor or int(other["page"]) != int(anchor["page"]):
        continue
      if float(other["bbox"][0]) <= float(anchor["bbox"][0]):
        continue
      if _overlap(float(anchor["bbox"][1]), band_end, float(other["bbox"][1]), float(other["bbox"][3])) <= 0:
        continue
      limit = min(limit, float(other["bbox"][0]) - 2.0)
    return limit

  def _band_end(anchor: dict[str, Any]) -> float:
    candidates = [
      float(other["bbox"][1]) for other in anchors
      if other is not anchor
      and int(other["page"]) == int(anchor["page"])
      and other.get("columnBand") == anchor.get("columnBand")
      and float(other["bbox"][1]) > float(anchor["bbox"][1]) + 1
    ]
    if candidates:
      return min(candidates)
    return page_bottom.get(int(anchor["page"]), float(anchor["bbox"][3]) + 50.0)

  for anchor in anchors:
    if anchor.get("role") == "response_control":
      continue
    band_end = _band_end(anchor)
    right_limit = _right_limit(anchor, band_end)
    content: list[dict[str, Any]] = []
    for line in lines:
      if int(line.get("page") or 0) != int(anchor["page"]):
        continue
      cy = (float(line.get("top") or 0) + float(line.get("bottom") or 0)) / 2.0
      if cy < float(anchor["bbox"][1]) - 2 or cy >= band_end:
        continue
      x0 = float(line.get("x0") or 0)
      if x0 < float(anchor["bbox"][0]) - X_TOL:
        continue
      if x0 >= right_limit:
        continue
      content.append(line)
    content.sort(key=lambda line: (float(line.get("top") or 0), float(line.get("x0") or 0)))

    cell_key = (int(anchor["page"]), int(anchor.get("columnBand") or 0))
    if cell_key not in raster_in_cell_cache:
      cell_components = []
      for index, component in enumerate(raster_components):
        if int(component.get("page") or 0) != int(anchor["page"]):
          continue
        cx0, cy0, cx1, cy1 = (float(value) for value in component.get("bbox") or (0, 0, 0, 0))
        if cx0 >= float(anchor["bbox"][0]) - X_TOL and cx0 < right_limit and not _overlaps_visual_marker(component):
          cell_components.append(index)
      raster_in_cell_cache[cell_key] = cell_components
    visual_indexes = [
      index for index in raster_in_cell_cache[cell_key]
      if _overlap(float(anchor["bbox"][1]), band_end, float(raster_components[index]["bbox"][1]), float(raster_components[index]["bbox"][3])) > 0
    ]

    if not content and not visual_indexes:
      anchor["contentRegionId"] = None
      continue

    kind, kind_evidence = _classify_kind(content, visual_indexes, raster_components)
    x0 = min([float(line.get("x0") or 0) for line in content] + [float(anchor["bbox"][0])])
    x1 = max([float(line.get("x1") or 0) for line in content] + [float(anchor["bbox"][2])])
    y0 = min([float(line.get("top") or 0) for line in content] + [float(anchor["bbox"][1])])
    y1 = max([float(line.get("bottom") or 0) for line in content] + [band_end])
    confidence = "medium" if kind in {"text", "math", "media", "mixed"} else "low"
    if not reliable:
      confidence = "low"
    region = ObservedResponseRegion(
      regionId=len(regions),
      page=int(anchor["page"]),
      bbox=[x0, y0, x1, y1],
      columnBand=int(anchor.get("columnBand") or 0),
      kind=kind,
      lineIndexes=[line.get("lineIndex") for line in content],
      wordIndexes=_word_indexes_for(content, words),
      visualComponentIndexes=visual_indexes,
      confidence=confidence,
      evidence=kind_evidence + (["boundary_uncertain"] if not reliable else []),
    )
    regions.append(region)
    anchor["contentRegionId"] = region.regionId

  # ---- slots ---------------------------------------------------------------
  slots: list[ResponseSlotHypothesis] = []
  for anchor in anchors:
    role = anchor.get("role") or "unknown"
    evidence = [f"source:{anchor.get('source')}"]
    if anchor.get("markerShape"):
      evidence.append(f"shape:{anchor['markerShape']}")
    if anchor.get("fill"):
      evidence.append(f"fill:{anchor['fill']}")
    confidence = "medium" if anchor.get("source") in {"strong", "visual"} else "low"
    if not reliable:
      confidence = "low"
      evidence.append("boundary_uncertain")
    if anchor.get("contentRegionId") is None and role not in {"response_control"}:
      evidence.append("no_content_region")
      confidence = "low"
    observations = [{
      "source": anchor.get("source"),
      "kind": anchor.get("kind"),
      "label": anchor.get("label"),
      "lineIndex": anchor.get("lineIndex"),
      "visualIndex": anchor.get("visualIndex"),
      "fill": anchor.get("fill"),
    }]
    observations.extend(anchor.get("additionalObservations") or [])
    slot = ResponseSlotHypothesis(
      slotId=len(slots),
      page=int(anchor["page"]),
      bbox=[float(value) for value in anchor["bbox"]],
      markerObservations=observations,
      contentRegionId=anchor.get("contentRegionId"),
      role=role,
      label=anchor.get("subitemLabel") if role == "subitem" else anchor.get("label"),
      parentLabel=anchor.get("parentLabel"),
      confidence=confidence,
      evidence=evidence,
    )
    slots.append(slot)

  # ---- pattern -------------------------------------------------------------
  pattern = _classify_pattern(
    anchors=anchors,
    slots=slots,
    controls_active=controls_active,
    control_pairs=control_pairs,
    internal_present=internal_present,
    parent_present=bool(parent_anchors),
    internal_lines=internal_lines,
    reliable=reliable,
  )

  return {
    "observedResponseRegions": [region.to_dict() for region in regions],
    "responseSlotHypotheses": [slot.to_dict() for slot in slots],
    "questionResponsePattern": pattern.to_dict(),
    "weakRegionAnchors": [dict(anchor) for anchor in weak_diagnostic],
    "blockers": blockers,
  }


def _word_indexes_for(content_lines: list[dict[str, Any]], words: list[dict[str, Any]]) -> list[int]:
  if not words or not content_lines:
    return []
  indexes: list[int] = []
  for word_index, word in enumerate(words):
    wpage = int(word.get("page") or 0)
    wbbox = [float(value) for value in word.get("bbox") or (0, 0, 0, 0)]
    for line in content_lines:
      if int(line.get("page") or 0) != wpage:
        continue
      if float(line.get("top") or 0) - 2 <= _center_y(wbbox) < float(line.get("bottom") or 0) + 2:
        indexes.append(word_index)
        break
  return indexes


def _is_bar(line: dict[str, Any]) -> bool:
  width = float(line.get("x1") or 0) - float(line.get("x0") or 0)
  height = float(line.get("bottom") or 0) - float(line.get("top") or 0)
  if height <= 0:
    return False
  text = str(line.get("text") or "").strip()
  if text and set(text) <= set("-–—_."):
    return True
  return width / height >= BAR_RATIO_MIN and height <= BAR_HEIGHT_MAX and width >= 15


def _x_aligned(lines: list[dict[str, Any]]) -> bool:
  xs = [float(line.get("x0") or 0) for line in lines]
  if len(xs) < 2:
    return False
  return (max(xs) - min(xs)) <= 8.0


def _is_bar_component(component: dict[str, Any]) -> bool:
  width = float(component.get("width") or 0)
  height = float(component.get("height") or 0)
  if height <= 0:
    return False
  return width / height >= BAR_RATIO_MIN and height <= BAR_HEIGHT_MAX + 4 and width >= 15


def _classify_kind(
  content: list[dict[str, Any]],
  visual_indexes: list[int],
  raster_components: list[dict[str, Any]],
) -> tuple[str, list[str]]:
  words_total = sum(len(str(line.get("text") or "").split()) for line in content)
  short = sum(1 for line in content if len(str(line.get("text") or "").split()) <= 3)
  numeric = sum(1 for line in content if re.search(r"\d", str(line.get("text") or "")) and len(str(line.get("text") or "").split()) <= 3)
  has_bar_line = any(_is_bar(line) for line in content)
  components = [raster_components[index] for index in visual_indexes]
  has_bar_component = any(_is_bar_component(component) for component in components)
  has_block_component = any(
    max(float(component.get("width") or 0), float(component.get("height") or 0)) >= 35
    and float(component.get("area") or 0) >= 300
    for component in components
  )
  aligned = numeric >= 2 and _x_aligned([line for line in content if re.search(r"\d", str(line.get("text") or ""))])
  stacked = short >= 2 and numeric >= 2
  evidence: list[str] = []
  if has_bar_line or has_bar_component:
    evidence.append("fraction_bar")
  if aligned:
    evidence.append("aligned_numeric_components")
  if stacked:
    evidence.append("stacked_lines")
  if components:
    evidence.append("raster_component")
  math_strong = bool(has_bar_line or has_bar_component or (aligned and numeric >= 2) or (stacked and words_total <= 8))
  media_strong = has_block_component and not (has_bar_line or has_bar_component)
  # Math evidence takes precedence over partial text so that a stacked numeric
  # layout is not demoted to plain text just because a few OCR tokens exist.
  if math_strong:
    return ("mixed" if words_total >= 6 else "math"), evidence
  if media_strong:
    return ("mixed" if words_total >= 4 else "media"), evidence
  if words_total > 0:
    return "text", evidence
  return "unknown", evidence


def _classify_pattern(
  anchors: list[dict[str, Any]],
  slots: list[ResponseSlotHypothesis],
  controls_active: bool,
  control_pairs: int,
  internal_present: bool,
  parent_present: bool,
  internal_lines: list[tuple[int, str, str]],
  reliable: bool,
) -> QuestionResponsePattern:
  option_slots = [slot for slot in slots if slot.role == "answer_option"]
  subitem_slots = [slot for slot in slots if slot.role == "subitem"]
  control_slots = [slot for slot in slots if slot.role == "response_control"]
  evidence: list[str] = []
  pattern = "unknown"

  if controls_active and control_pairs >= CONTROL_MIN_ROWS:
    pattern = "paired_controls_per_row"
    evidence.append(f"control_pairs:{control_pairs}")
  elif internal_present and len(option_slots) >= 2:
    pattern = "internal_enumeration_then_options"
    evidence.append("internal_enumeration")
    evidence.append(f"options:{len(option_slots)}")
  elif (internal_present or parent_present or subitem_slots) and not option_slots:
    pattern = "internal_enumeration"
    evidence.append("subitems_without_options")
  elif subitem_slots and option_slots:
    pattern = "internal_enumeration_then_options"
    evidence.append("subitems_then_options")
  elif len(option_slots) >= MIN_SINGLE_COLUMN:
    column_counts: dict[int, int] = {}
    for anchor in anchors:
      if anchor.get("role") != "answer_option":
        continue
      band = int(anchor.get("columnBand") or 0)
      column_counts[band] = column_counts.get(band, 0) + 1
    strong_columns = [band for band, count in column_counts.items() if count >= 2]
    rows = {int(round(float(anchor["bbox"][1]) / 6.0)) for anchor in anchors if anchor.get("role") == "answer_option"}
    if len(strong_columns) >= GRID_MIN_COLUMNS and len(rows) >= GRID_MIN_ROWS:
      pattern = "grid_option_markers"
      evidence.extend([f"columns:{len(strong_columns)}", f"rows:{len(rows)}"])
    else:
      pattern = "one_per_option"
      evidence.append(f"options:{len(option_slots)}")
  elif option_slots or control_slots or subitem_slots:
    pattern = "repeated_markers_unknown_role"
    evidence.append("insufficient_geometry")
  else:
    pattern = "unknown"
    evidence.append("no_markers")

  if not reliable:
    confidence = "low"
  elif pattern in {"paired_controls_per_row", "internal_enumeration_then_options", "internal_enumeration"}:
    confidence = "medium"
  elif pattern in {"one_per_option"} and len(option_slots) >= 3:
    confidence = "medium"
  elif pattern == "grid_option_markers":
    confidence = "medium"
  else:
    confidence = "low"
  return QuestionResponsePattern(
    pattern=pattern,
    slotIds=[slot.slotId for slot in slots],
    confidence=confidence,
    evidence=evidence,
  )
