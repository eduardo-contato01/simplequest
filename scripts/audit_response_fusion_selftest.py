from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_response_fusion as fusion  # noqa: E402

FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
  if condition:
    print(f"PASS {name}")
  else:
    print(f"FAIL {name} {detail}")
    FAILURES.append(name)


def obs(source: str, label: str | None = None, visual_index: int | None = None) -> dict:
  return {"source": source, "label": label, "visualIndex": visual_index, "lineIndex": 0}


def slot(slot_id: int, role: str = "answer_option", label: str | None = None,
         content: int | None = None, observations: list[dict] | None = None, confidence: str = "medium") -> dict:
  return {
    "slotId": slot_id, "role": role, "label": label, "contentRegionId": content,
    "markerObservations": observations if observations is not None else [obs("strong", label)],
    "confidence": confidence,
  }


def structure(mode: str = "single_choice", markers: list[dict] | None = None, internal: list[dict] | None = None) -> dict:
  return {
    "inferredResponseStructure": {"mode": mode, "confidence": "medium"},
    "alternativeMarkerCandidates": markers or [],
    "internalEnumerationCandidates": internal or [],
  }


def markers(count: int, labels: str = "ABCDE") -> list[dict]:
  return [{"markerKind": "answer_marker", "label": labels[index], "lineIndex": index} for index in range(count)]


def visual(evidence_count: int = 0, hypotheses: list[dict] | None = None) -> dict:
  evidence = [{"confidence": "high", "page": 1, "bbox": [0, index * 40, 30, index * 40 + 30]} for index in range(evidence_count)]
  return {"visualAlternativeEvidence": evidence, "visualResponseSetHypotheses": hypotheses or []}


def regions(slots: list[dict], region_kinds: list[str] | None = None, pattern: str = "one_per_option",
            confidence: str = "medium", weak: list[dict] | None = None) -> dict:
  region_list = [{"regionId": index, "kind": kind} for index, kind in enumerate(region_kinds or [])]
  return {
    "responseSlotHypotheses": slots,
    "observedResponseRegions": region_list,
    "questionResponsePattern": {"pattern": pattern, "confidence": confidence},
    "weakRegionAnchors": weak or [],
    "blockers": [],
  }


def test_text_plus_visual_independent_strong() -> None:
  slots = [
    slot(0, observations=[obs("strong", "A"), obs("visual", visual_index=0)], content=0),
    slot(1, observations=[obs("strong", "B"), obs("visual", visual_index=1)], content=1),
    slot(2, observations=[obs("strong", "C"), obs("visual", visual_index=2)], content=2),
  ]
  result = fusion.fuse_response_evidence({"reliable": True}, structure(markers=markers(3)), visual(3), regions(slots, ["text", "text", "text"]))
  check("indep.slot_strong", result["slots"][0]["agreement"] == "strong", result["slots"][0])
  check("indep.question_strong", result["agreement"] == "strong", result["agreement"])
  check("indep.count", result["optionCountHypothesis"] == 3, result)


def test_visual_spatial_double_count_not_strong() -> None:
  slots = [slot(index, observations=[obs("visual", visual_index=index)], content=index) for index in range(3)]
  result = fusion.fuse_response_evidence({"reliable": True}, structure(), visual(3), regions(slots, ["text", "text", "text"]))
  check("double.slot_partial", result["slots"][0]["agreement"] == "partial", result["slots"][0])
  check("double.question_partial", result["agreement"] == "partial", result["agreement"])
  check("double.count", result["optionCountHypothesis"] == 3, result)


def test_text_spatial_double_count_not_strong() -> None:
  slots = [slot(index, label="ABCD"[index], observations=[obs("strong", "ABCD"[index])], content=index) for index in range(4)]
  result = fusion.fuse_response_evidence({"reliable": True}, structure(markers=markers(4)), visual(), regions(slots, ["text"] * 4))
  check("textspace.slot_partial", result["slots"][0]["agreement"] == "partial", result["slots"][0])
  check("textspace.not_conflict", result["agreement"] != "conflict", result["agreement"])


def test_absence_visual_not_conflict() -> None:
  slots = [slot(index, label="ABCD"[index], observations=[obs("single_letter", "ABCD"[index])], content=index) for index in range(4)]
  result = fusion.fuse_response_evidence({"reliable": True}, structure(markers=markers(4)), visual(), regions(slots, ["text"] * 4))
  check("absence.no_conflict", result["agreement"] != "conflict", result["agreement"])
  check("absence.count", result["optionCountHypothesis"] == 4, result)


def test_numeric_textual_single_source() -> None:
  result = fusion.fuse_response_evidence({"reliable": True}, structure(mode="numeric_response"), visual(), regions([]))
  check("numeric.single_source", result["agreement"] == "single_source", result["agreement"])
  check("numeric.sources", result["sources"] == ["textual"], result["sources"])
  check("numeric.count_null", result["optionCountHypothesis"] is None, result)


def test_weak_anchor_only_blocks_count() -> None:
  slots = [slot(index, observations=[obs("weak")], content=index, confidence="low") for index in range(5)]
  weak = [{"weakAnchorReason": "short_repeated_column:5"}]
  result = fusion.fuse_response_evidence({"reliable": True}, structure(), visual(), regions(slots, ["text"] * 5, weak=weak))
  check("weak.count_null", result["optionCountHypothesis"] is None, result)
  check("weak.blocker", "weak_anchor_only" in result["hardBlockers"], result["hardBlockers"])
  check("weak.labels_unknown", result["optionLabelsHypothesis"] == "unknown", result)


def test_visual_without_glyph_count_labels() -> None:
  slots = [slot(index, observations=[obs("visual", visual_index=index)], content=index) for index in range(5)]
  result = fusion.fuse_response_evidence({"reliable": True}, structure(), visual(5), regions(slots, ["text"] * 5))
  check("glyph.count", result["optionCountHypothesis"] == 5, result)
  check("glyph.labels_unknown", result["optionLabelsHypothesis"] == "unknown", result)


def test_textual_labels_ad() -> None:
  slots = [slot(index, label="ABCD"[index], observations=[obs("single_letter", "ABCD"[index])], content=index) for index in range(4)]
  result = fusion.fuse_response_evidence({"reliable": True}, structure(markers=markers(4, "ABCD")), visual(), regions(slots, ["text"] * 4))
  check("labelsAD.count", result["optionCountHypothesis"] == 4, result)
  check("labelsAD.labels", result["optionLabelsHypothesis"] == "A-D", result)


def test_paired_controls_no_option_count() -> None:
  slots = [slot(index, role="subitem", label="ABCDE"[index], observations=[obs("strong", "ABCDE"[index])], content=index) for index in range(5)]
  slots += [slot(5 + index, role="response_control", label="CE"[index % 2], observations=[obs("symbol_control", "CE"[index % 2])]) for index in range(10)]
  result = fusion.fuse_response_evidence({"reliable": True}, structure(), visual(), regions(slots, ["text"] * 5, pattern="paired_controls_per_row"))
  check("controls.count_null", result["optionCountHypothesis"] is None, result)
  check("controls.labels_null", result["optionLabelsHypothesis"] is None, result)


def test_parent_child_beats_circle_cluster() -> None:
  slots = [slot(index, role="answer_option", observations=[obs("visual", visual_index=index)], content=index) for index in range(5)]
  slots += [slot(5, role="subitem", label="A", observations=[obs("strong", "A")], content=5)]
  result = fusion.fuse_response_evidence({"reliable": True}, structure(), visual(5), regions(slots, ["text"] * 5, pattern="paired_controls_per_row"))
  check("parentchild.count_null", result["optionCountHypothesis"] is None, result)
  check("parentchild.role_conflict", "role_conflict" in result["hardBlockers"], result["hardBlockers"])


def test_slot_without_region_kept() -> None:
  slots = [slot(index, observations=[obs("visual", visual_index=index)], content=None) for index in range(3)]
  result = fusion.fuse_response_evidence({"reliable": True}, structure(), visual(3), regions(slots, []))
  check("noregion.slots_kept", len(result["slots"]) == 3, result["slots"])
  check("noregion.count", result["optionCountHypothesis"] == 3, result)
  check("noregion.soft", "content_region_missing" in result["softBlockers"], result["softBlockers"])


def test_region_kind_unknown_keeps_slot() -> None:
  slots = [slot(index, observations=[obs("visual", visual_index=index)], content=index) for index in range(3)]
  result = fusion.fuse_response_evidence({"reliable": True}, structure(), visual(3), regions(slots, ["unknown", "unknown", "unknown"]))
  check("unknownkind.slots", len(result["slots"]) == 3, result["slots"])
  check("unknownkind.count", result["optionCountHypothesis"] == 3, result)


def test_count_conflict() -> None:
  slots = [slot(index, observations=[obs("strong", "ABCD"[index])], content=index) for index in range(4)]
  result = fusion.fuse_response_evidence({"reliable": True}, structure(markers=markers(5)), visual(), regions(slots, ["text"] * 4))
  check("countconflict.conflict", result["agreement"] == "conflict", result["agreement"])
  check("countconflict.blocker", "count_conflict" in result["hardBlockers"], result["hardBlockers"])
  check("countconflict.count_null", result["optionCountHypothesis"] is None, result)


def test_label_conflict() -> None:
  slots = [slot(0, observations=[obs("strong", "A"), obs("strong", "B")], content=0)]
  result = fusion.fuse_response_evidence({"reliable": True}, structure(), visual(), regions(slots, ["text"]))
  check("labelconflict.conflict", result["agreement"] == "conflict", result["agreement"])
  check("labelconflict.blocker", "label_conflict" in result["hardBlockers"], result["hardBlockers"])


def test_boundary_uncertain_blocks_strong() -> None:
  slots = [slot(index, observations=[obs("visual", visual_index=index)], content=index) for index in range(5)]
  result = fusion.fuse_response_evidence({"reliable": False}, structure(), visual(5), regions(slots, ["text"] * 5))
  check("boundary.blocker", "boundary_uncertain" in result["hardBlockers"], result["hardBlockers"])
  check("boundary.count_null", result["optionCountHypothesis"] is None, result)
  check("boundary.interp_low", result["interpretationConfidence"] == "low", result["interpretationConfidence"])


def test_low_auxiliary_does_not_drag_hypothesis() -> None:
  slots = [slot(index, observations=[obs("visual", visual_index=index)], content=index) for index in range(3)]
  slots.append(slot(3, role="subitem", label="I", observations=[obs("weak")], confidence="low"))
  result = fusion.fuse_response_evidence({"reliable": True}, structure(), visual(3), regions(slots, ["text"] * 3, pattern="one_per_option"))
  check("aux.observation_high", result["observationConfidence"] == "high", result["observationConfidence"])


def test_insufficient_like_cmbel() -> None:
  result = fusion.fuse_response_evidence({"reliable": True}, {}, {}, {})
  check("insufficient.agreement", result["agreement"] == "insufficient", result["agreement"])
  check("insufficient.count", result["optionCountHypothesis"] is None, result)
  check("insufficient.labels", result["optionLabelsHypothesis"] is None, result)
  check("insufficient.interp", result["interpretationConfidence"] == "low", result)


def test_subitems_not_option_labels() -> None:
  internal = [{"labels": ["I", "II"]}]
  slots = [slot(0, role="subitem", label="I", observations=[obs("internal", "I")], content=0),
           slot(1, role="subitem", label="II", observations=[obs("internal", "II")], content=1)]
  result = fusion.fuse_response_evidence({"reliable": True}, structure(mode="discursive", internal=internal), visual(), regions(slots, ["text", "text"], pattern="internal_enumeration"))
  check("subitems.count_null", result["optionCountHypothesis"] is None, result)
  check("subitems.labels_null", result["optionLabelsHypothesis"] is None, result)


def main() -> None:
  test_text_plus_visual_independent_strong()
  test_visual_spatial_double_count_not_strong()
  test_text_spatial_double_count_not_strong()
  test_absence_visual_not_conflict()
  test_numeric_textual_single_source()
  test_weak_anchor_only_blocks_count()
  test_visual_without_glyph_count_labels()
  test_textual_labels_ad()
  test_paired_controls_no_option_count()
  test_parent_child_beats_circle_cluster()
  test_slot_without_region_kept()
  test_region_kind_unknown_keeps_slot()
  test_count_conflict()
  test_label_conflict()
  test_boundary_uncertain_blocks_strong()
  test_low_auxiliary_does_not_drag_hypothesis()
  test_insufficient_like_cmbel()
  test_subitems_not_option_labels()
  if FAILURES:
    print(f"\n{len(FAILURES)} checks falharam: {FAILURES}")
    raise SystemExit(1)
  print("\nTodos os checks da camada de fusao passaram.")


if __name__ == "__main__":
  main()
