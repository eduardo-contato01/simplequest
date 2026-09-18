from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_response_structure as rs  # noqa: E402

FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
  if condition:
    print(f"PASS {name}")
  else:
    print(f"FAIL {name} {detail}")
    FAILURES.append(name)


def lines(entries: list[tuple[str, float, float]], page: int = 1) -> list[rs.ObservedLine]:
  result = []
  for index, (text, top, x0) in enumerate(entries):
    result.append(rs.ObservedLine(
      text=text, page=page, top=top, bottom=top + 10.0,
      x0=x0, x1=x0 + 120.0, confidence=0.9, line_index=index, role="alternative",
    ))
  return result


def structure(entries, **kwargs):
  return rs.discover_response_structure(lines(entries), **kwargs)


def test_vertical_abcde() -> None:
  result = structure([
    ("A) doze", 100, 50), ("B) treze", 120, 50), ("C) quatorze", 140, 50),
    ("D) quinze", 160, 50), ("E) dezesseis", 180, 50),
  ])
  s = result["inferredResponseStructure"]
  check("abcde.mode", s["mode"] == "single_choice", s)
  check("abcde.options", s["optionLabels"] == "A-E", s)
  check("abcde.count", s["expectedOptionCount"] == 5, s)
  check("abcde.confidence", s["confidence"] == "high", s)


def test_vertical_abcd() -> None:
  result = structure([
    ("A) um", 100, 50), ("B) dois", 120, 50), ("C) tres", 140, 50), ("D) quatro", 160, 50),
  ])
  s = result["inferredResponseStructure"]
  check("abcd.options", s["optionLabels"] == "A-D", s)
  check("abcd.count", s["expectedOptionCount"] == 4, s)
  check("abcd.mode_high", s["modeConfidence"] == "high", s)
  check("abcd.count_not_high", s["optionCountConfidence"] != "high", s)


def test_vertical_abc() -> None:
  result = structure([("A) um", 100, 50), ("B) dois", 120, 50), ("C) tres", 140, 50)])
  s = result["inferredResponseStructure"]
  check("abc.options", s["optionLabels"] == "A-C", s)
  check("abc.count", s["expectedOptionCount"] == 3, s)


def test_lowercase() -> None:
  result = structure([
    ("a) um", 100, 50), ("b) dois", 120, 50), ("c) tres", 140, 50),
    ("d) quatro", 160, 50), ("e) cinco", 180, 50),
  ])
  s = result["inferredResponseStructure"]
  p = result["inferredAlternativeProfile"]
  check("lowercase.options", s["optionLabels"] == "A-E", s)
  check("lowercase.case", p["labelCase"] == "lower", p)


def test_parentheses_and_separators() -> None:
  paren = structure([("(A) um", 100, 50), ("(B) dois", 120, 50), ("(C) tres", 140, 50)])
  check("paren.shape", paren["inferredAlternativeProfile"]["markerShape"] == "parentheses", paren)
  dot = structure([("A. um", 100, 50), ("B. dois", 120, 50), ("C. tres", 140, 50)])
  check("dot.separator", dot["inferredAlternativeProfile"]["separator"] == "dot", dot)
  dash = structure([("A- um", 100, 50), ("B- dois", 120, 50), ("C- tres", 140, 50)])
  check("dash.separator", dash["inferredAlternativeProfile"]["separator"] == "dash", dash)


def test_response_fields() -> None:
  spaced = structure([("A ( ) um", 100, 50), ("B ( ) dois", 120, 50), ("C ( ) tres", 140, 50)])
  check("field.spaced", spaced["inferredAlternativeProfile"]["responseField"] == "present", spaced)
  dash = structure([("A-( ) um", 100, 50), ("B-( ) dois", 120, 50), ("C-( ) tres", 140, 50)])
  check("field.dash", dash["inferredAlternativeProfile"]["responseField"] == "present", dash)
  bare = structure([("A( ) um", 100, 50), ("B( ) dois", 120, 50), ("C( ) tres", 140, 50)])
  check("field.bare", bare["inferredAlternativeProfile"]["responseField"] == "present", bare)
  check("field.bare.options", bare["inferredResponseStructure"]["optionLabels"] == "A-C", bare)
  for name, form in [("underscore", "A(_ )"), ("dot_inside", "A(. )"), ("dot_sep", "A.( )"), ("dot_space", "A. ( )")]:
    variant = structure([(f"{form} um", 100, 50), (form.replace("A", "B", 1) + " dois", 120, 50), (form.replace("A", "C", 1) + " tres", 140, 50)])
    profile = variant["inferredAlternativeProfile"]
    s = variant["inferredResponseStructure"]
    check(f"field.{name}", profile["responseField"] == "present", profile)
    check(f"field.{name}.options", s["optionLabels"] == "A-C", s)
  field_text = structure([("A(_ ) um", 100, 50), ("B(_ ) dois", 120, 50), ("C(_ ) tres", 140, 50)])
  texts = [c["text"] for c in field_text["alternativeMarkerCandidates"]]
  check("field.content_not_text", texts == ["um", "dois", "tres"], texts)


def test_lost_marker_merges_cluster() -> None:
  result = structure([
    ("A) um", 100, 50), ("B) dois", 120, 50),
    ("2990", 140, 50),
    ("D) quatro", 160, 50), ("E) cinco", 180, 50),
  ])
  s = result["inferredResponseStructure"]
  recovered = result["recoveredAlternativeMarkerCandidates"]
  check("lostmarker.one_cluster", len(result["responseSetCandidates"]) == 1, result["responseSetCandidates"])
  check("lostmarker.options", s["optionLabels"] == "custom", s)
  check("lostmarker.recovered", [entry["expectedLabel"] for entry in recovered] == ["C"], recovered)
  explicit = {candidate["label"] for candidate in result["alternativeMarkerCandidates"]}
  check("lostmarker.no_promotion", "C" not in explicit, explicit)


def test_circled() -> None:
  result = structure([("Ⓐ doze", 100, 50), ("Ⓑ treze", 120, 50), ("Ⓒ quatorze", 140, 50)])
  p = result["inferredAlternativeProfile"]
  s = result["inferredResponseStructure"]
  check("circled.shape", p["markerShape"] == "circle", p)
  check("circled.options", s["optionLabels"] == "A-C", s)
  fill = structure([("Ⓐ doze", 100, 50), ("Ⓑ treze", 120, 50), ("Ⓒ quatorze", 140, 50)])
  check("circled.fill_unknown_without_image", fill["inferredAlternativeProfile"]["markerFill"] == "unknown", fill)


def test_subitems_do_not_become_answer_set() -> None:
  result = structure([
    ("a) item um", 100, 50), ("b) item dois", 120, 50), ("c) item tres", 140, 50),
    ("Ⓐ alternativa um", 170, 300), ("Ⓑ alternativa dois", 190, 300),
    ("Ⓒ alternativa tres", 210, 300), ("Ⓓ alternativa quatro", 230, 300),
  ])
  s = result["inferredResponseStructure"]
  check("subitems.mode", s["mode"] == "mixed", s)
  check("subitems.options", s["optionLabels"] == "A-D", s)
  check("subitems.present", s["subitems"] == "present", s)
  check("subitems.internal_shape", result["internalEnumerationCandidates"][0]["markerShape"] == "none", result)


def test_parent_child_subitems() -> None:
  result = structure([
    ("15-A  afirmação um", 100, 50), ("15-B  afirmação dois", 120, 50),
    ("15-C  afirmação três", 140, 50), ("15-D  afirmação quatro", 160, 50),
  ])
  s = result["inferredResponseStructure"]
  kinds = {candidate["markerKind"] for candidate in result["alternativeMarkerCandidates"]}
  check("parentchild.mode", s["mode"] == "unknown", s)
  check("parentchild.subitems", s["subitems"] == "present", s)
  check("parentchild.kind", "parent_child" in kinds, result)
  check("parentchild.not_true_false", s["mode"] != "true_false_items", s)


def test_recovered_marker() -> None:
  result = structure([
    ("A) um", 100, 50), ("B) dois", 120, 50),
    ("texto sem marcador recuperavel", 140, 50),
    ("D) quatro", 160, 50), ("E) cinco", 180, 50),
  ])
  recovered = result["recoveredAlternativeMarkerCandidates"]
  check("recovered.present", len(recovered) == 1, result)
  check("recovered.label", recovered and recovered[0]["expectedLabel"] == "C", recovered)
  check("recovered.not_invented_label", recovered and recovered[0]["label"] is None, recovered)
  check("recovered.keeps_text", recovered and recovered[0]["text"] == "texto sem marcador recuperavel", recovered)
  explicit = {candidate["label"] for candidate in result["alternativeMarkerCandidates"]}
  check("recovered.no_mutation", "C" not in explicit, explicit)


def test_two_columns() -> None:
  result = structure([
    ("A) um", 100, 50), ("B) dois", 100, 300),
    ("C) tres", 130, 50), ("D) quatro", 130, 300),
    ("E) cinco", 160, 50),
  ])
  p = result["inferredAlternativeProfile"]
  check("columns.layout", p["layout"] == "two_columns", p)


def test_media_only_alternative_not_absence() -> None:
  result = structure([("Ⓐ ", 100, 50), ("Ⓑ ", 120, 50), ("Ⓒ ", 140, 50)])
  kinds = {candidate["contentKind"] for candidate in result["alternativeMarkerCandidates"]}
  s = result["inferredResponseStructure"]
  check("media.no_absence_claim", kinds == {"unknown"}, kinds)
  check("media.still_structure", s["mode"] == "single_choice", s)


def test_profile_does_not_feed_back() -> None:
  entries = [("A) um", 100, 50), ("B) dois", 120, 50), ("C) tres", 140, 50)]
  baseline = structure(entries)
  primed = structure(entries, document_profile={"dominantOptionLabels": "A-E"}, section_profile={"dominantOptionLabels": "A-E"})
  check(
    "no_feedback.structure",
    baseline["inferredResponseStructure"] == primed["inferredResponseStructure"],
    baseline["inferredResponseStructure"],
  )
  check(
    "no_feedback.profile",
    baseline["inferredAlternativeProfile"] == primed["inferredAlternativeProfile"],
    baseline["inferredAlternativeProfile"],
  )


def test_document_profiles() -> None:
  document, section = rs.build_document_profiles([
    {"markerShape": "circle", "separator": "none", "labelCase": "upper", "optionLabels": "A-E"},
    {"markerShape": "circle", "separator": "none", "labelCase": "upper", "optionLabels": "A-E"},
    {"markerShape": "none", "separator": "dot", "labelCase": "lower", "optionLabels": "A-D"},
  ])
  check("docprof.support", document and document["support"] == 3, document)
  check("docprof.purity", document and document["purity"] == round(2 / 3, 4), document)
  check("docprof.dominant", document and document["dominantStyle"]["markerShape"] == "circle", document)
  check("docprof.shadow_only", section is None, section)


def test_long_body_is_unknown_not_discursive() -> None:
  result = structure([
    ("Este e um enunciado bastante longo com muitas palavras para simular corpo textual", 100, 50),
    ("A segunda linha tambem possui um numero elevado de palavras no conteudo escrito", 120, 50),
    ("A terceira linha continua o texto com muitas palavras distintas para o teste", 140, 50),
    ("A quarta linha reforca o corpo longo sem apresentar qualquer marcador de alternativa", 160, 50),
    ("A quinta linha mantem o paragrafo extenso sem estrutura de resposta visivel", 180, 50),
    ("A sexta linha encerra o texto longo sem alternativas nem instrucao discursiva", 200, 50),
  ])
  s = result["inferredResponseStructure"]
  check("longbody.unknown", s["mode"] == "unknown", s)
  check("longbody.not_discursive", s["mode"] != "discursive", s)


def test_discursive_positive_evidence() -> None:
  result = structure([
    ("Leia o texto e responda ao que se pede a seguir", 100, 50),
    ("Justifique sua resposta apresentando todos os calculos necessarios", 120, 50),
  ])
  s = result["inferredResponseStructure"]
  check("discursive.positive", s["mode"] == "discursive", s)


def test_numeric_positive_evidence() -> None:
  result = structure([
    ("Qual o valor final obtido na operacao descrita anteriormente", 100, 50),
    ("Resposta: ______", 120, 50),
  ])
  s = result["inferredResponseStructure"]
  check("numeric.positive", s["mode"] == "numeric_response", s)


def test_ce_without_context_is_unknown() -> None:
  result = structure([("C) primeiro item", 100, 50), ("E) segundo item", 120, 50)])
  s = result["inferredResponseStructure"]
  check("ce.unknown", s["mode"] == "unknown", s)
  check("ce.labels", s["optionLabels"] == "CE", s)
  check("ce.count_null", s["expectedOptionCount"] is None, s)


def test_singleton_is_unknown() -> None:
  result = structure([("E) ie3", 100, 50)])
  s = result["inferredResponseStructure"]
  check("singleton.unknown", s["mode"] == "unknown", s)
  check("singleton.no_labels", s["optionLabels"] == "none", s)


def test_singleton_never_subitem() -> None:
  result = structure([("a) item solto", 100, 50)])
  s = result["inferredResponseStructure"]
  check("singleton.no_internal", result["internalEnumerationCandidates"] == [], result)
  check("singleton.not_true_false", s["mode"] != "true_false_items", s)


def test_gap_count_null_with_recovered() -> None:
  result = structure([
    ("A) um", 100, 50), ("B) dois", 120, 50),
    ("linha sem marcador no meio", 140, 50),
    ("D) quatro", 160, 50), ("E) cinco", 180, 50),
  ])
  s = result["inferredResponseStructure"]
  recovered = result["recoveredAlternativeMarkerCandidates"]
  check("gap.mode", s["mode"] == "single_choice", s)
  check("gap.labels_conf_low", s["optionLabelsConfidence"] == "low", s)
  check("gap.count_null", s["expectedOptionCount"] is None, s)
  check("gap.count_conf_low", s["optionCountConfidence"] == "low", s)
  check("gap.recovered", [entry["expectedLabel"] for entry in recovered] == ["C"], recovered)
  check("gap.mode_conf", s["modeConfidence"] == "medium", s)


def test_multiple_markers_same_line() -> None:
  result = structure([("(A) um (B) dois (C) tres", 100, 50)])
  s = result["inferredResponseStructure"]
  labels = [candidate["label"] for candidate in result["alternativeMarkerCandidates"]]
  ordinals = [candidate["ordinalWithinLine"] for candidate in result["alternativeMarkerCandidates"]]
  check("multi.labels", labels == ["A", "B", "C"], labels)
  check("multi.ordinals", ordinals == [0, 1, 2], ordinals)
  check("multi.mode", s["mode"] == "single_choice", s)
  check("multi.count", s["expectedOptionCount"] == 3, s)
  check("multi.texts", [c["text"] for c in result["alternativeMarkerCandidates"]] == ["um", "dois", "tres"], result)


def test_gap_without_recovered_count_null() -> None:
  result = structure([("A) um", 100, 50), ("B) dois", 120, 50), ("E) cinco", 140, 50)])
  s = result["inferredResponseStructure"]
  check("norecover.mode", s["mode"] == "single_choice", s)
  check("norecover.count_null", s["expectedOptionCount"] is None, s)


def test_same_line_tall_marker_cluster() -> None:
  observed = [
    rs.ObservedLine(text="(A) um", page=1, top=100, bottom=110, x0=50, x1=170, line_index=0),
    rs.ObservedLine(text="(B) (C) texto", page=1, top=120, bottom=160, x0=50, x1=300, line_index=1),
    rs.ObservedLine(text="(D) quatro", page=1, top=170, bottom=180, x0=50, x1=170, line_index=2),
    rs.ObservedLine(text="(E) cinco", page=1, top=190, bottom=200, x0=50, x1=170, line_index=3),
  ]
  result = rs.discover_response_structure(observed)
  s = result["inferredResponseStructure"]
  labels = [candidate["label"] for candidate in result["alternativeMarkerCandidates"]]
  check("tall.labels", labels == ["A", "B", "C", "D", "E"], labels)
  check("tall.mode", s["mode"] == "single_choice", s)
  check("tall.count", s["expectedOptionCount"] == 5, s)


def main() -> None:
  test_vertical_abcde()
  test_vertical_abcd()
  test_vertical_abc()
  test_lowercase()
  test_parentheses_and_separators()
  test_response_fields()
  test_lost_marker_merges_cluster()
  test_circled()
  test_subitems_do_not_become_answer_set()
  test_parent_child_subitems()
  test_recovered_marker()
  test_two_columns()
  test_media_only_alternative_not_absence()
  test_profile_does_not_feed_back()
  test_document_profiles()
  test_long_body_is_unknown_not_discursive()
  test_discursive_positive_evidence()
  test_numeric_positive_evidence()
  test_ce_without_context_is_unknown()
  test_singleton_is_unknown()
  test_singleton_never_subitem()
  test_gap_count_null_with_recovered()
  test_multiple_markers_same_line()
  test_gap_without_recovered_count_null()
  test_same_line_tall_marker_cluster()
  if FAILURES:
    print(f"\n{len(FAILURES)} checks falharam: {FAILURES}")
    raise SystemExit(1)
  print("\nTodos os checks da camada de descoberta de estrutura passaram.")


if __name__ == "__main__":
  main()
