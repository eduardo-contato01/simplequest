from __future__ import annotations

from typing import Any


ORIGIN_BY_SOURCE = {
  "strong": "textual_marker",
  "single_letter": "textual_marker",
  "internal": "textual_marker",
  "native_text": "textual_marker",
  "instruction_context": "textual_marker",
  "symbol_control": "symbol_control",
  "visual": "visual_marker",
  "rendered_visual": "visual_marker",
  "weak": "weak_anchor",
  "ocr_word_geometry": "word_geometry",
}

ORIGIN_CONFIDENCE = {
  "textual_marker": "medium",
  "symbol_control": "medium",
  "visual_marker": "high",
  "weak_anchor": "low",
  "word_geometry": "low",
  "content_geometry": "low",
}

CONFIDENCE_ORDER = {"low": 0, "medium": 1, "high": 2}
CONFIDENCE_NAME = {0: "low", 1: "medium", 2: "high"}

AGREEMENT_ORDER = {"insufficient": 0, "single_source": 1, "partial": 2, "strong": 3}
AGREEMENT_BY_ORDER = {value: key for key, value in AGREEMENT_ORDER.items()}

OPTION_BLOCKING_HARD = {
  "competing_response_sets",
  "role_conflict",
  "label_conflict",
  "count_conflict",
  "parent_child_competing",
  "weak_anchor_only",
}

ANSWER_OPTION_PATTERNS = {"one_per_option", "grid_option_markers", "internal_enumeration_then_options"}


def _min_confidence(values: list[str]) -> str:
  if not values:
    return "low"
  return CONFIDENCE_NAME[min(CONFIDENCE_ORDER[value] for value in values)]


def _max_confidence(values: list[str]) -> str:
  if not values:
    return "low"
  return CONFIDENCE_NAME[max(CONFIDENCE_ORDER[value] for value in values)]


def _origin_confidence(origin: str, obs: dict[str, Any], visual_evidence: list[dict[str, Any]]) -> str:
  if origin == "visual_marker":
    index = obs.get("visualIndex")
    if isinstance(index, int) and 0 <= index < len(visual_evidence):
      return str(visual_evidence[index].get("confidence") or "medium")
    return "high"
  return ORIGIN_CONFIDENCE.get(origin, "medium")


def _slot_origins(slot: dict[str, Any]) -> dict[str, dict[str, Any]]:
  origins: dict[str, dict[str, Any]] = {}
  for observation in slot.get("markerObservations") or []:
    source = str(observation.get("source") or "")
    origin = ORIGIN_BY_SOURCE.get(source)
    if not origin:
      continue
    origins.setdefault(origin, observation)
  return origins


def _slot_agreement(origins: dict[str, dict[str, Any]], has_region: bool) -> str:
  if len(origins) >= 2:
    return "strong"
  if len(origins) == 1:
    return "partial" if has_region else "single_source"
  return "insufficient"


def _contiguous_labels(labels: list[str]) -> str:
  unique = set(labels)
  prefix: list[str] = []
  for expected in "ABCDE":
    if expected in unique:
      prefix.append(expected)
    else:
      break
  if len(prefix) == len(unique) and len(prefix) >= 3:
    return f"A-{prefix[-1]}"
  if unique == {"C", "E"}:
    return "CE"
  return "unknown"


def fuse_response_evidence(
  boundary: dict[str, Any],
  structure: dict[str, Any] | None,
  visual: dict[str, Any] | None,
  regions: dict[str, Any] | None,
) -> dict[str, Any]:
  structure = structure or {}
  visual = visual or {}
  regions = regions or {}
  reliable = bool(boundary.get("reliable", True))

  visual_evidence = visual.get("visualAlternativeEvidence") or []
  visual_hypotheses = visual.get("visualResponseSetHypotheses") or []
  slot_hypotheses = regions.get("responseSlotHypotheses") or []
  region_list = regions.get("observedResponseRegions") or []
  pattern = regions.get("questionResponsePattern") or {}
  pattern_name = str(pattern.get("pattern") or "unknown")
  pattern_confidence = str(pattern.get("confidence") or "low")
  structure_info = structure.get("inferredResponseStructure") or {}

  slots: list[dict[str, Any]] = []
  answer_slot_indexes: list[int] = []
  for index, slot in enumerate(slot_hypotheses):
    origins = _slot_origins(slot)
    content_region_id = slot.get("contentRegionId")
    has_region = content_region_id is not None
    agreement = _slot_agreement(origins, has_region)
    association = "medium" if slot.get("confidence") == "medium" else "low"
    if slot.get("confidence") == "high":
      association = "high"
    blockers: list[str] = []
    if not has_region and slot.get("role") == "answer_option":
      blockers.append("content_region_missing")
    if set(origins.keys()) == {"weak_anchor"}:
      blockers.append("weak_anchor_only")
    slots.append({
      "slotId": slot.get("slotId"),
      "role": slot.get("role"),
      "label": slot.get("label"),
      "contentRegionId": content_region_id,
      "textualMarkerRefs": [
        {"source": observation.get("source"), "lineIndex": observation.get("lineIndex")}
        for origin, observation in origins.items()
        if origin in {"textual_marker", "symbol_control"}
      ],
      "visualEvidenceRefs": [
        observation.get("visualIndex")
        for origin, observation in origins.items()
        if origin == "visual_marker"
      ],
      "origins": sorted(origins.keys()),
      "associationConfidence": association,
      "agreement": agreement,
      "evidence": [f"origins:{'+'.join(sorted(origins.keys())) or 'none'}"],
      "blockers": blockers,
    })
    if slot.get("role") == "answer_option":
      answer_slot_indexes.append(index)

  # ---- structural blockers -------------------------------------------------
  hard_blockers: list[str] = []
  soft_blockers: list[str] = []
  if not reliable:
    hard_blockers.append("boundary_uncertain")
  if len([h for h in visual_hypotheses if int(h.get("support") or 0) >= 3]) >= 2:
    hard_blockers.append("competing_response_sets")
  if pattern_name == "paired_controls_per_row" and answer_slot_indexes:
    hard_blockers.append("role_conflict")
    if any(slot.get("role") == "subitem" for slot in slots):
      hard_blockers.append("parent_child_competing")

  for slot in slots:
    for blocker in slot.get("blockers") or []:
      if blocker == "content_region_missing":
        soft_blockers.append(blocker)
      elif blocker == "weak_anchor_only":
        pass
  if any("content_region_missing" in (slot.get("blockers") or []) for slot in slots):
    soft_blockers.append("content_region_missing")
  if pattern_name == "unknown" and (visual_evidence or visual_hypotheses):
    soft_blockers.append("visual_pattern_unknown")
  if pattern_name == "grid_option_markers" and pattern_confidence == "low":
    soft_blockers.append("grid_order_uncertain")
  if pattern_name in {"internal_enumeration", "internal_enumeration_then_options"} and not answer_slot_indexes:
    soft_blockers.append("missing_marker_observation")

  # count conflict: explicit option markers vs answer_option slots disagree
  text_markers = [
    marker for marker in (structure.get("alternativeMarkerCandidates") or [])
    if marker.get("markerKind") == "answer_marker"
    and str(marker.get("label") or "").upper() in list("ABCDE")
  ]
  # label conflict inside a merged slot
  label_conflict = any(
    len({str(o.get("label")) for o in (slot.get("markerObservations") or []) if o.get("label")}) > 1
    for slot in slot_hypotheses
  )
  count_conflict = (
    len(text_markers) >= 3
    and len(answer_slot_indexes) >= 3
    and len(text_markers) != len(answer_slot_indexes)
  )
  if label_conflict:
    hard_blockers.append("label_conflict")
  if count_conflict:
    hard_blockers.append("count_conflict")

  hard_blockers = sorted(set(hard_blockers))
  soft_blockers = sorted(set(soft_blockers))

  all_weak = bool(answer_slot_indexes) and all(
    set(slots[index]["origins"]) == {"weak_anchor"} for index in answer_slot_indexes
  )
  if all_weak:
    hard_blockers.append("weak_anchor_only")
    hard_blockers = sorted(set(hard_blockers))

  # ---- sources -------------------------------------------------------------
  sources: list[str] = []
  textual_signal = bool(
    structure.get("alternativeMarkerCandidates")
    or structure.get("internalEnumerationCandidates")
    or structure.get("instructionContext")
    or str(structure_info.get("mode") or "unknown") not in {"unknown", "None"}
    or any(origin in {"textual_marker", "symbol_control"} for slot in slots for origin in slot["origins"])
  )
  if textual_signal:
    sources.append("textual")
  if visual_evidence:
    sources.append("visual")
  if region_list or slot_hypotheses:
    sources.append("spatial")

  # ---- option count hypothesis --------------------------------------------
  allow_count = (
    pattern_name in ANSWER_OPTION_PATTERNS
    and len(answer_slot_indexes) >= 3
    and reliable
    and not (OPTION_BLOCKING_HARD & set(hard_blockers))
    and not all_weak
  )
  option_count = len(answer_slot_indexes) if allow_count else None

  # ---- option labels hypothesis -------------------------------------------
  labels_applicable = bool(answer_slot_indexes)
  option_labels: str | None
  if not labels_applicable:
    option_labels = None
  else:
    observed = [slots[index]["label"] for index in answer_slot_indexes]
    if any(not label for label in observed):
      option_labels = "unknown"
    else:
      option_labels = _contiguous_labels([str(label).upper() for label in observed])

  # ---- agreement -----------------------------------------------------------
  conflict = bool({"role_conflict", "label_conflict", "count_conflict"} & set(hard_blockers))
  if count_conflict:
    conflict = True
  if not sources:
    agreement = "insufficient"
  elif conflict:
    agreement = "conflict"
  elif option_count is not None:
    agreement = _min_agreement([slots[index]["agreement"] for index in answer_slot_indexes])
  else:
    distinct = sorted({origin for slot in slots for origin in slot["origins"]})
    if set(distinct) == {"weak_anchor"}:
      agreement = "single_source"
    elif len(distinct) >= 2:
      agreement = "strong"
    elif distinct:
      agreement = "partial" if region_list else "single_source"
    else:
      agreement = "single_source"

  # ---- confidences ---------------------------------------------------------
  if option_count is not None:
    observation_confidence = _max_confidence([
      _max_confidence([
        _origin_confidence(origin, observation, visual_evidence)
        for origin, observation in _slot_origins(slot_hypotheses[index]).items()
      ])
      for index in answer_slot_indexes
    ])
    association_confidence = _min_confidence([slots[index]["associationConfidence"] for index in answer_slot_indexes])
  else:
    necessary = [
      _origin_confidence(origin, observation, visual_evidence)
      for slot in slots
      for origin, observation in _slot_origins(slot_hypotheses[slot["slotId"]]).items()
    ] if slots else []
    observation_confidence = _min_confidence(necessary) if necessary else "low"
    association_confidence = _min_confidence([slot["associationConfidence"] for slot in slots]) if slots else "low"

  interpretation_confidence = "low"
  if agreement in {"strong", "partial"} and not conflict:
    if observation_confidence == "high" and association_confidence in {"high", "medium"}:
      interpretation_confidence = "medium" if "boundary_uncertain" in hard_blockers else "high"
    else:
      interpretation_confidence = "medium" if "boundary_uncertain" not in hard_blockers else "low"
  elif agreement == "single_source":
    interpretation_confidence = "medium" if observation_confidence in {"high", "medium"} and "boundary_uncertain" not in hard_blockers else "low"
  else:
    interpretation_confidence = "low"
  if pattern_confidence == "low" and interpretation_confidence == "high":
    interpretation_confidence = "medium"
  if option_count is not None and option_labels == "unknown" and interpretation_confidence == "high":
    interpretation_confidence = "medium"
  if "boundary_uncertain" in hard_blockers:
    interpretation_confidence = "low"

  evidence: list[str] = [
    f"pattern:{pattern_name}",
    f"answer_option_slots:{len(answer_slot_indexes)}",
    f"origins:{'+'.join(sorted({origin for slot in slots for origin in slot['origins']})) or 'none'}",
  ]
  if option_count is not None:
    evidence.append(f"optionCountHypothesis:{option_count}")
  if option_labels is not None:
    evidence.append(f"optionLabelsHypothesis:{option_labels}")

  return {
    "agreement": agreement,
    "sources": sources,
    "slots": slots,
    "optionCountHypothesis": option_count,
    "optionLabelsHypothesis": option_labels,
    "observationConfidence": observation_confidence,
    "associationConfidence": association_confidence,
    "interpretationConfidence": interpretation_confidence,
    "evidence": evidence,
    "blockers": hard_blockers + soft_blockers,
    "hardBlockers": hard_blockers,
    "softBlockers": soft_blockers,
  }


def _min_agreement(values: list[str]) -> str:
  if not values:
    return "insufficient"
  return AGREEMENT_BY_ORDER[min(AGREEMENT_ORDER[value] for value in values)]
