from __future__ import annotations

import re
from dataclasses import dataclass, field
from statistics import median
from typing import Any

try:
  from PIL import Image
except Exception:  # pragma: no cover
  Image = None


CIRCLED_UPPER_START = 0x24B6
CIRCLED_LOWER_START = 0x24D0
CIRCLED_COUNT = 26
CIRCLED_RANGE = "\u24b6-\u24cf\u24d0-\u24e9"
LEAD_ARTIFACTS_RE = re.compile(r"^[\s\|\[\]\{\}~^]+")

FIELD_CONTENT = r"\(\s*[_\s.]*\s*\)"

PARENT_CHILD_RE = re.compile(r"^(\d{1,3})\s*[-–—]\s*([A-Ea-e])\b\s*(.*)$")
PAREN_RE = re.compile(r"^\(([A-Ea-e])\)\s*(.*)$")
RIGHT_PAREN_RE = re.compile(r"^([A-Ea-e])\s*\)\s*(.*)$")
SEPARATOR_FIELD_RE = re.compile(r"^([A-Ea-e])\s*([.\-–—:])\s*" + FIELD_CONTENT + r"\s*(.*)$")
SEPARATOR_RE = re.compile(r"^([A-Ea-e])\s*([.\-–—:])\s*(.*)$")
FIELD_RE = re.compile(r"^([A-Ea-e])\s+" + FIELD_CONTENT + r"\s*(.*)$")
BARE_FIELD_RE = re.compile(r"^([A-Ea-e])" + FIELD_CONTENT + r"\s*(.*)$")

STRONG_MARKER_RE = re.compile(
  r"\(\s*[A-Ea-e]\s*\)"
  r"|[A-Ea-e]\s*\)"
  r"|[A-Ea-e]\s*[.\-–—:]\s*" + FIELD_CONTENT +
  r"|[A-Ea-e]\s*" + FIELD_CONTENT +
  r"|[A-Ea-e]" + FIELD_CONTENT +
  r"|[" + CIRCLED_RANGE + r"]"
)

TF_INSTRUCTION_RE = re.compile(
  r"\b(julgue|certo ou errado|certo/errado|verdadeiro ou falso|classifique as? (?:afirma|item)|assinale (?:certo|c|v|f))\b",
  re.IGNORECASE,
)
DISCURSIVE_INSTRUCTION_RE = re.compile(
  r"\b(justifique|explique|descreva|redija|escreva um texto|desenvolva|comente)\b",
  re.IGNORECASE,
)
NUMERIC_FIELD_RE = re.compile(r"^\s*(resposta|resultado|resposta final)\s*[:\-]", re.IGNORECASE)

SEPARATOR_NAMES = {".": "dot", "-": "dash", "–": "dash", "—": "dash", ":": "colon"}


@dataclass
class ObservedLine:
  text: str
  page: int
  top: float
  bottom: float
  x0: float
  x1: float
  confidence: float | None = None
  is_reconstructed: bool = False
  line_index: int = 0
  role: str = "stem"


@dataclass
class MarkerCandidate:
  label: str | None
  label_case: str
  separator: str
  marker_shape: str
  marker_fill: str
  response_field: str
  marker_kind: str
  parent_question: int | None
  subitem_label: str | None
  text: str
  page: int
  bbox: tuple[float, float, float, float]
  line_index: int
  evidence: list[str] = field(default_factory=list)
  cluster_id: int | None = None
  label_source: str = "explicit"
  content_kind: str = "unknown"
  ordinal_within_line: int = 0
  span: tuple[int, int] = (0, 0)

  def to_dict(self) -> dict[str, Any]:
    return {
      "label": self.label,
      "labelCase": self.label_case,
      "separator": self.separator,
      "markerShape": self.marker_shape,
      "markerFill": self.marker_fill,
      "responseField": self.response_field,
      "markerKind": self.marker_kind,
      "parentQuestion": self.parent_question,
      "subitemLabel": self.subitem_label,
      "text": self.text,
      "page": self.page,
      "bbox": [round(value, 2) for value in self.bbox],
      "lineIndex": self.line_index,
      "ordinalWithinLine": self.ordinal_within_line,
      "spanWithinLine": [int(self.span[0]), int(self.span[1])],
      "labelSource": self.label_source,
      "contentKind": self.content_kind,
      "clusterId": self.cluster_id,
      "evidence": self.evidence,
    }


def _circled_label(character: str) -> tuple[str, str] | None:
  code = ord(character)
  if CIRCLED_UPPER_START <= code < CIRCLED_UPPER_START + CIRCLED_COUNT:
    return chr(ord("A") + code - CIRCLED_UPPER_START), "upper"
  if CIRCLED_LOWER_START <= code < CIRCLED_LOWER_START + CIRCLED_COUNT:
    return chr(ord("a") + code - CIRCLED_LOWER_START), "lower"
  return None


def _descriptor(
  label: str | None,
  label_case: str,
  separator: str,
  marker_shape: str,
  response_field: str,
  marker_kind: str,
  parent_question: int | None,
  subitem_label: str | None,
  text: str,
  evidence: list[str],
  span_start: int,
  span_end: int,
  text_start: int,
) -> dict[str, Any]:
  return {
    "label": label,
    "labelCase": label_case,
    "separator": separator,
    "markerShape": marker_shape,
    "markerFill": "unknown" if marker_shape == "circle" else "none",
    "responseField": response_field,
    "markerKind": marker_kind,
    "parentQuestion": parent_question,
    "subitemLabel": subitem_label,
    "text": text,
    "evidence": evidence,
    "spanStart": span_start,
    "spanEnd": span_end,
    "textStart": text_start,
  }


def parse_marker(text: str) -> dict[str, Any] | None:
  raw = str(text or "")
  stripped = LEAD_ARTIFACTS_RE.sub("", raw)
  if not stripped:
    return None
  lead = len(raw) - len(stripped)
  first = stripped[0]
  circled = _circled_label(first)
  if circled:
    label, case = circled
    return _descriptor(
      label.upper(), case, "none", "circle", "absent", "answer_marker", None, None,
      stripped[1:].strip(), ["circled_unicode"], lead, lead + 1, lead + 1,
    )
  parent_child = PARENT_CHILD_RE.match(stripped)
  if parent_child:
    label = parent_child.group(2)
    return _descriptor(
      None, "upper" if label.isupper() else "lower", "dash", "none", "absent", "parent_child",
      int(parent_child.group(1)), label.upper(), parent_child.group(3).strip(), ["parent_child"],
      lead, lead + parent_child.end(0), lead + parent_child.start(3),
    )
  paren = PAREN_RE.match(stripped)
  if paren:
    label = paren.group(1)
    return _descriptor(
      label.upper(), "upper" if label.isupper() else "lower", "none", "parentheses", "absent",
      "answer_marker", None, None, paren.group(2).strip(), ["explicit_marker"],
      lead, lead + paren.start(2), lead + paren.start(2),
    )
  right_paren = RIGHT_PAREN_RE.match(stripped)
  if right_paren:
    label = right_paren.group(1)
    return _descriptor(
      label.upper(), "upper" if label.isupper() else "lower", "right_parenthesis", "none", "absent",
      "answer_marker", None, None, right_paren.group(2).strip(), ["explicit_marker"],
      lead, lead + right_paren.start(2), lead + right_paren.start(2),
    )
  separator_field = SEPARATOR_FIELD_RE.match(stripped)
  if separator_field:
    label = separator_field.group(1)
    return _descriptor(
      label.upper(), "upper" if label.isupper() else "lower",
      SEPARATOR_NAMES.get(separator_field.group(2), "other"), "none", "present",
      "answer_marker", None, None, separator_field.group(3).strip(), ["explicit_marker"],
      lead, lead + separator_field.start(3), lead + separator_field.start(3),
    )
  separator = SEPARATOR_RE.match(stripped)
  if separator:
    label = separator.group(1)
    remainder = separator.group(3)
    field = "present" if re.match(r"^" + FIELD_CONTENT, remainder) else "absent"
    remainder = re.sub(r"^" + FIELD_CONTENT + r"\s*", "", remainder)
    return _descriptor(
      label.upper(), "upper" if label.isupper() else "lower",
      SEPARATOR_NAMES.get(separator.group(2), "other"), "none", field,
      "answer_marker", None, None, remainder.strip(), ["explicit_marker"],
      lead, lead + separator.start(3), lead + separator.start(3),
    )
  field = FIELD_RE.match(stripped)
  if field:
    label = field.group(1)
    return _descriptor(
      label.upper(), "upper" if label.isupper() else "lower", "none", "none", "present",
      "answer_marker", None, None, field.group(2).strip(), ["explicit_marker"],
      lead, lead + field.start(2), lead + field.start(2),
    )
  bare_field = BARE_FIELD_RE.match(stripped)
  if bare_field:
    label = bare_field.group(1)
    return _descriptor(
      label.upper(), "upper" if label.isupper() else "lower", "none", "none", "present",
      "answer_marker", None, None, bare_field.group(2).strip(), ["explicit_marker"],
      lead, lead + bare_field.start(2), lead + bare_field.start(2),
    )
  return None


def _is_strong(parsed: dict[str, Any]) -> bool:
  return (
    parsed["markerShape"] in {"parentheses", "circle"}
    or parsed["responseField"] == "present"
    or parsed["separator"] == "right_parenthesis"
    or parsed["markerKind"] == "parent_child"
  )


def extract_candidates(lines: list[ObservedLine]) -> list[MarkerCandidate]:
  candidates: list[MarkerCandidate] = []
  for line in lines:
    raw = str(line.text or "")
    if not raw.strip():
      continue
    remaining = raw
    ordinal = 0
    while remaining.strip():
      parsed = parse_marker(remaining)
      if not parsed:
        break
      if ordinal > 0 and not _is_strong(parsed):
        break
      text_start = int(parsed["textStart"])
      tail = remaining[text_start:]
      match = STRONG_MARKER_RE.search(tail)
      segment_end = match.start() if match else len(tail)
      candidate = MarkerCandidate(
        label=parsed["label"],
        label_case=parsed["labelCase"],
        separator=parsed["separator"],
        marker_shape=parsed["markerShape"],
        marker_fill=parsed["markerFill"],
        response_field=parsed["responseField"],
        marker_kind=parsed["markerKind"],
        parent_question=parsed["parentQuestion"],
        subitem_label=parsed["subitemLabel"],
        text=tail[:segment_end].strip(),
        page=line.page,
        bbox=(line.x0, line.top, line.x1, line.bottom),
        line_index=line.line_index,
        evidence=list(parsed["evidence"]),
        ordinal_within_line=ordinal,
        span=(text_start, text_start + segment_end),
      )
      candidate.content_kind = "text" if candidate.text else "unknown"
      candidates.append(candidate)
      if not match:
        break
      next_remaining = tail[match.start():]
      if next_remaining == remaining:
        break
      remaining = next_remaining
      ordinal += 1
  return candidates


def _style_key(candidate: MarkerCandidate) -> tuple:
  return (candidate.marker_shape, candidate.response_field)


def cluster_candidates(candidates: list[MarkerCandidate], total_lines: int = 1) -> list[dict[str, Any]]:
  ordered = [c for c in candidates if c.marker_kind == "answer_marker" and c.label]
  ordered = sorted(ordered, key=lambda c: (c.page, c.bbox[1], c.bbox[0]))
  if not ordered:
    return []
  heights = [max(1.0, c.bbox[3] - c.bbox[1]) for c in ordered]
  median_height = median(heights)
  gap_limit = max(median_height * 4.0, 30.0)
  clusters: list[list[MarkerCandidate]] = []
  for candidate in ordered:
    placed = False
    for cluster in clusters:
      previous = cluster[-1]
      same_page = previous.page == candidate.page
      same_line = previous.line_index == candidate.line_index
      gap = candidate.bbox[1] - previous.bbox[3]
      style_ok = _style_key(previous) == _style_key(candidate)
      sequential = ord(candidate.label) > ord(previous.label)
      if same_page and style_ok and sequential and (same_line or -median_height * 1.5 <= gap <= gap_limit):
        cluster.append(candidate)
        placed = True
        break
    if not placed:
      clusters.append([candidate])
  result: list[dict[str, Any]] = []
  for index, cluster in enumerate(clusters):
    for candidate in cluster:
      candidate.cluster_id = index
    labels = [c.label for c in cluster]
    indices = [ord(label) - ord("A") for label in labels if label]
    x_values = [c.bbox[0] for c in cluster]
    gaps = [cluster[i + 1].bbox[1] - cluster[i].bbox[3] for i in range(len(cluster) - 1)]
    x_iqr = round((max(x_values) - min(x_values)), 4) if x_values else 0.0
    styles = {_style_key(c) for c in cluster}
    size = len(cluster)
    sequence_score = 10.0 if all(indices[i] < indices[i + 1] for i in range(len(indices) - 1)) else 0.0
    style_score = 6.0 / len(styles)
    alignment_score = max(0.0, 5.0 - x_iqr / 10.0)
    spatial_score = max(0.0, 3.0 - (max(gaps) - min(gaps)) / 20.0) if gaps else 3.0
    span = (max(indices) - min(indices) + 1) if indices else 0
    completeness = (len(set(indices)) / span) * 4.0 if span else 0.0
    start_bonus = 3.0 if (indices and min(indices) == 0 and size >= 2) else 0.0
    size_score = min(size, 5) * 0.6
    last_index = max(c.line_index for c in cluster)
    near_end = 3.0 * ((last_index + 1) / max(1, total_lines))
    case_bonus = 2.0 if cluster[0].label_case == "upper" else 0.0
    score = (
      sequence_score + style_score + alignment_score + spatial_score
      + completeness + start_bonus + size_score + near_end + case_bonus
    )
    from collections import Counter
    dominant_separator = Counter(c.separator for c in cluster).most_common(1)[0][0]
    dominant_case = Counter(c.label_case for c in cluster).most_common(1)[0][0]
    result.append({
      "clusterId": index,
      "labels": labels,
      "size": size,
      "score": round(score, 4),
      "style": list(next(iter(styles))) if styles else None,
      "xIqr": round(x_iqr, 4),
      "yGapMedian": round(median(gaps), 4) if gaps else None,
      "markerShape": cluster[0].marker_shape,
      "separator": dominant_separator,
      "labelCase": dominant_case,
      "candidates": [c.to_dict() for c in cluster],
      "lineStart": min(c.line_index for c in cluster),
      "lineEnd": last_index,
    })
  return sorted(result, key=lambda item: item["score"], reverse=True)


def _labels_option_set(labels: list[str]) -> str:
  unique = set(labels)
  if not unique:
    return "none"
  if unique == {"C", "E"}:
    return "CE"
  prefix = []
  for expected in "ABCDE":
    if expected in unique:
      prefix.append(expected)
    else:
      break
  if len(prefix) == len(unique) and len(prefix) >= 2:
    return f"A-{prefix[-1]}"
  return "custom"


def _selected_cluster(clusters: list[dict[str, Any]]) -> tuple[dict[str, Any] | None, bool]:
  if not clusters:
    return None, False
  best = clusters[0]
  ambiguous = False
  if len(clusters) > 1:
    second = clusters[1]
    if best["score"] - second["score"] < 2.0 and best["size"] >= 3 and second["size"] >= 3:
      ambiguous = True
  if best["size"] < 2:
    return None, ambiguous
  return best, ambiguous


def _internal_enumeration(clusters: list[dict[str, Any]], selected: dict[str, Any] | None) -> list[dict[str, Any]]:
  internal: list[dict[str, Any]] = []
  for cluster in clusters:
    if selected is not None and cluster["clusterId"] == selected["clusterId"]:
      continue
    if cluster["size"] < 2:
      continue
    labels = cluster["labels"]
    indices = [ord(label) - ord("A") for label in labels]
    contiguous_from_a = indices == list(range(len(indices)))
    if contiguous_from_a and cluster["labelCase"] != "lower":
      continue
    sequential = all(indices[i] < indices[i + 1] for i in range(len(indices) - 1))
    before_selected = selected is None or cluster["lineEnd"] < selected["lineStart"]
    if cluster["labelCase"] == "lower" and sequential and before_selected:
      internal.append(cluster)
  return internal


def recover_missing_markers(selected: dict[str, Any] | None, lines: list[ObservedLine]) -> list[dict[str, Any]]:
  if not selected or selected["size"] < 2:
    return []
  candidates = selected["candidates"]
  present = {candidate["label"] for candidate in candidates if candidate["label"]}
  if not present:
    return []
  indices = sorted(ord(label) - ord("A") for label in present)
  missing = [chr(ord("A") + index) for index in range(indices[0], indices[-1] + 1) if chr(ord("A") + index) not in present]
  recovered: list[dict[str, Any]] = []
  x_values = [candidate["bbox"][0] for candidate in candidates]
  x_reference = median(x_values) if x_values else 0.0
  for label in missing:
    position = ord(label) - ord("A")
    before = [c for c in candidates if c["label"] and ord(c["label"]) - ord("A") < position]
    after = [c for c in candidates if c["label"] and ord(c["label"]) - ord("A") > position]
    if not before or not after:
      continue
    previous = max(before, key=lambda c: c["bbox"][1])
    following = min(after, key=lambda c: c["bbox"][1])
    for line in lines:
      if not (previous["bbox"][3] <= line.top <= following["bbox"][1]):
        continue
      if parse_marker(line.text):
        continue
      if abs(line.x0 - x_reference) <= 12.0 and line.text.strip():
        recovered.append({
          "expectedLabel": label,
          "label": None,
          "labelSource": "recovered_geometry",
          "page": line.page,
          "bbox": [round(line.x0, 2), round(line.top, 2), round(line.x1, 2), round(line.bottom, 2)],
          "lineIndex": line.line_index,
          "text": line.text,
          "evidence": ["sequence_gap", "alignment", "spatial_cluster"],
        })
        break
  return recovered


def _layout(candidates: list[dict[str, Any]]) -> tuple[str, bool]:
  x_values = sorted(candidate["bbox"][0] for candidate in candidates)
  if len(x_values) < 2:
    return "vertical", False
  gaps = [x_values[i + 1] - x_values[i] for i in range(len(x_values) - 1)]
  if any(gap >= 60 for gap in gaps):
    bands = 1
    previous = x_values[0]
    for value in x_values[1:]:
      if value - previous >= 60:
        bands += 1
      previous = value
    if bands == 2:
      return "two_columns", False
    if bands > 2:
      return "grid", True
    return "two_columns", False
  return "vertical", False


def _response_mode(
  selected: dict[str, Any] | None,
  internal: list[dict[str, Any]],
  lines: list[ObservedLine],
) -> dict[str, Any]:
  evidence: list[str] = []
  parent_sublabels: list[str] = []
  for line in lines:
    parsed = parse_marker(line.text)
    if parsed and parsed["markerKind"] == "parent_child" and parsed["subitemLabel"]:
      parent_sublabels.append(parsed["subitemLabel"])
  parent_sublabels = sorted(set(parent_sublabels))
  parent_present = len(parent_sublabels) >= 2
  internal_present = len(internal) >= 1
  subitem_labels = list(parent_sublabels)
  for cluster in internal:
    subitem_labels.extend(cluster["labels"])
  subitems_present = parent_present or internal_present
  if parent_present:
    evidence.append("parent_child_subitems")
  if internal_present:
    evidence.append("internal_enumeration")
  tf_instruction = any(TF_INSTRUCTION_RE.search(line.text) for line in lines)
  if tf_instruction:
    evidence.append("tf_instruction")
  discursive_instruction = any(DISCURSIVE_INSTRUCTION_RE.search(line.text) for line in lines)
  numeric_field = any(NUMERIC_FIELD_RE.search(line.text) for line in lines)

  if selected:
    evidence.append(f"selected_cluster:{selected['clusterId']}")
    labels = set(selected["labels"])
    if labels == {"C", "E"}:
      if tf_instruction or parent_present:
        mode = "true_false_items"
      else:
        mode = "unknown"
        evidence.append("ce_without_context")
      option_labels = "CE"
    elif subitems_present:
      mode = "mixed"
      option_labels = _labels_option_set(selected["labels"])
    else:
      mode = "single_choice"
      option_labels = _labels_option_set(selected["labels"])
    subitems = "present" if subitems_present else "absent"
    return {"mode": mode, "optionLabels": option_labels, "subitems": subitems, "subitemLabels": subitem_labels, "evidence": evidence}

  if subitems_present:
    if tf_instruction:
      evidence.append("subitems_with_tf_instruction")
      return {"mode": "true_false_items", "optionLabels": "custom", "subitems": "present", "subitemLabels": subitem_labels, "evidence": evidence}
    return {"mode": "unknown", "optionLabels": "none", "subitems": "present", "subitemLabels": subitem_labels, "evidence": evidence}
  if numeric_field:
    evidence.append("numeric_field")
    return {"mode": "numeric_response", "optionLabels": "none", "subitems": "absent", "subitemLabels": [], "evidence": evidence}
  if discursive_instruction:
    evidence.append("discursive_instruction")
    return {"mode": "discursive", "optionLabels": "none", "subitems": "absent", "subitemLabels": [], "evidence": evidence}
  return {"mode": "unknown", "optionLabels": "none", "subitems": "unknown", "subitemLabels": [], "evidence": evidence}


def discover_response_structure(
  lines: list[ObservedLine],
  image_path: str | None = None,
  document_profile: dict[str, Any] | None = None,
  section_profile: dict[str, Any] | None = None,
) -> dict[str, Any]:
  candidates = extract_candidates(lines)
  clusters = cluster_candidates(candidates, max(1, len(lines)))
  selected, ambiguous = _selected_cluster(clusters)
  internal = _internal_enumeration(clusters, selected)
  recovered = recover_missing_markers(selected, lines)
  mode_info = _response_mode(selected, internal, lines)
  mode = mode_info["mode"]
  option_labels = mode_info["optionLabels"]
  subitems_present = mode_info["subitems"] == "present"

  if selected:
    layout, layout_ambiguous = _layout(selected["candidates"])
    marker_shape = selected["markerShape"]
    separator = selected["separator"]
    label_case = selected["labelCase"]
    selected_styles = {
      (candidate["markerShape"], candidate["responseField"])
      for candidate in selected["candidates"]
    }
    style_consistency = len(selected_styles) == 1
  else:
    layout, layout_ambiguous = "unknown", False
    marker_shape, separator, label_case = "none", "none", "mixed"
    style_consistency = None

  if image_path and selected:
    for candidate in selected["candidates"]:
      if candidate["markerShape"] == "circle":
        candidate["markerFill"] = _visual_circle_fill(image_path, candidate["bbox"])

  sequence_indices = [ord(label) - ord("A") for label in selected["labels"]] if selected else []
  contiguous = bool(sequence_indices) and sequence_indices == list(range(sequence_indices[0], sequence_indices[-1] + 1))
  recovered_labels = {entry["expectedLabel"] for entry in recovered}
  terminal_ok = bool(sequence_indices) and sequence_indices[-1] in {2, 3, 4}
  count_confident = bool(
    selected
    and contiguous
    and terminal_ok
    and not ambiguous
    and not recovered_labels
    and selected["size"] == len(sequence_indices)
  )
  option_count = selected["size"] if count_confident else None

  if mode == "unknown":
    mode_confidence = "low"
  elif ambiguous:
    mode_confidence = "low"
  elif mode == "single_choice":
    mode_confidence = "high" if (selected and contiguous and style_consistency and not subitems_present and selected["markerShape"] != "circle") else "medium"
  elif mode == "mixed":
    mode_confidence = "medium"
  elif mode == "true_false_items":
    mode_confidence = "medium" if ("tf_instruction" in mode_info["evidence"] or "parent_child_subitems" in mode_info["evidence"]) else "low"
  else:
    mode_confidence = "low"

  if count_confident and option_labels == "A-E":
    option_labels_confidence = "high"
  elif option_labels in {"A-E", "A-D", "A-C"}:
    option_labels_confidence = "medium"
  else:
    option_labels_confidence = "low"

  if option_count is None:
    option_count_confidence = "low"
  elif count_confident and option_labels == "A-E":
    option_count_confidence = "high"
  elif count_confident:
    option_count_confidence = "medium"
  else:
    option_count_confidence = "low"

  profile_confidence = "low"
  if selected and not layout_ambiguous:
    profile_confidence = "high" if style_consistency and mode_confidence == "high" else "medium"

  evidence: list[str] = list(mode_info["evidence"])
  if selected:
    evidence.append(f"sequence_continuous:{contiguous}")
    evidence.append(f"layout:{layout}")
  if recovered:
    evidence.append(f"recovered_markers:{len(recovered)}")
  if ambiguous:
    evidence.append("ambiguous_clusters")

  structure = {
    "mode": mode,
    "modeConfidence": mode_confidence,
    "optionLabels": option_labels,
    "optionLabelsConfidence": option_labels_confidence,
    "expectedOptionCount": option_count,
    "optionCountConfidence": option_count_confidence,
    "subitems": mode_info["subitems"],
    "subitemLabels": mode_info["subitemLabels"],
    "confidence": mode_confidence,
    "evidence": evidence,
  }
  profile = {
    "labelCase": label_case,
    "separator": separator,
    "markerShape": marker_shape,
    "markerFill": selected["candidates"][0]["markerFill"] if selected and selected["candidates"] else "none",
    "responseField": selected["candidates"][0]["responseField"] if selected and selected["candidates"] else "unknown",
    "spacing": "spaced" if separator == "none" and marker_shape == "parentheses" else "tight",
    "layout": layout,
    "optionLabels": option_labels,
    "optionCount": option_count,
    "geometry": {
      "xMedianRel": round(median([c["bbox"][0] for c in selected["candidates"]]), 4) if selected and selected["candidates"] else None,
      "xIqr": selected["xIqr"] if selected else None,
      "yGapMedian": selected["yGapMedian"] if selected else None,
      "alignment": "left" if selected and (selected["xIqr"] or 0) < 12 else "unknown",
    },
    "confidence": profile_confidence,
    "evidence": evidence,
  }
  return {
    "inferredResponseStructure": structure,
    "inferredAlternativeProfile": profile,
    "responseSetCandidates": clusters,
    "internalEnumerationCandidates": internal,
    "recoveredAlternativeMarkerCandidates": recovered,
    "alternativeMarkerCandidates": [candidate.to_dict() for candidate in candidates],
    "documentAlternativeProfile": document_profile,
    "sectionAlternativeProfile": section_profile,
    "shadowOnly": True,
    "ambiguous": ambiguous or layout_ambiguous,
  }


def _visual_circle_fill(image_path: str, bbox: list[float]) -> str:
  if Image is None:
    return "unknown"
  try:
    with Image.open(image_path) as image:
      gray = image.convert("L")
      x0, top, x1, bottom = (int(round(value)) for value in bbox)
      padding = 2
      crop = gray.crop((max(0, x0 - padding), max(0, top - padding), x1 + padding, bottom + padding))
      pixels = list(crop.getdata())
    if not pixels:
      return "unknown"
    dark = sum(1 for value in pixels if value < 110)
    ratio = dark / len(pixels)
    if ratio >= 0.45:
      return "filled"
    if ratio >= 0.12:
      return "outline"
    return "unknown"
  except Exception:
    return "unknown"


def build_document_profiles(per_question: list[dict[str, Any]]) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
  styles: list[tuple] = []
  option_sets: list[str] = []
  for profile in per_question:
    if not profile:
      continue
    styles.append((profile.get("markerShape"), profile.get("separator"), profile.get("labelCase")))
    option_sets.append(profile.get("optionLabels") or "none")
  if not styles:
    return None, None
  from collections import Counter
  style_counter = Counter(styles)
  option_counter = Counter(option_sets)
  dominant_style, style_support = style_counter.most_common(1)[0]
  dominant_options, option_support = option_counter.most_common(1)[0]
  return {
    "support": len(styles),
    "purity": round(style_support / len(styles), 4),
    "confidence": "high" if style_support / len(styles) >= 0.7 else "medium" if style_support / len(styles) >= 0.5 else "low",
    "dominantStyle": {"markerShape": dominant_style[0], "separator": dominant_style[1], "labelCase": dominant_style[2]},
    "dominantOptionLabels": dominant_options,
    "dominantOptionSupport": option_support,
  }, None
