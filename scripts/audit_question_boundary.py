from __future__ import annotations

import re
import statistics
import unicodedata
from typing import Any

import audit_holdout_question_index as indexer
import audit_observations as observations

"""Neutral intra-page question boundary.

This module separates the region of a single selected question from the other
questions that share the same page(s). It uses only neutral information:

- the frozen question index (document order, questionId, questionNumber,
  pageStart, pageEnd, sequenceRun);
- the page numbers of the question;
- the text and geometry of observed question-start markers and words.

It never uses option labels, option count, response mode or Ground
Truth content to locate the boundary. When the current or the next question
marker cannot be located unambiguously the boundary is declared
``reliable=False`` so downstream fusion withholds unsafe emissions.

Global markers retain the frozen index grammar. Current, next and peer matching
share anchored target-aware grammar. Only uniquely matched same-page entries
from the frozen document index can prove a parallel question/column.
Lines have priority; word fallback cannot override a line ambiguity. Local line
reconstruction consumes only words already filtered by a reliable boundary.
"""

# Families ordered by the neutral hierarchy used by the question index.
_FAMILY_ORDER = ("keyword", "separator", "bare")

# Conservative parallel-column detection. The boundary becomes 2D only when
# two question-start markers are strongly separated in X while remaining
# approximately aligned in Y.
COLUMN_MIN_X_GAP_ABS = 120.0
COLUMN_MIN_X_GAP_RATIO = 0.25
COLUMN_MAX_Y_GAP_ABS = 60.0
COLUMN_MAX_Y_GAP_RATIO = 0.10
COLUMN_MIN_SIDE_RATIO = 0.20

_KEYWORD_SEPARATOR_RE = re.compile(r"^(?:QUEST[ÃA]O|ITEM)\s*[:\-–—]\s*0*(\d{1,3})\b", re.IGNORECASE)
_ORDINAL_ITEM_RE = re.compile(r"^0*(\d{1,3})\.?[º°]\s+ITEM\b", re.IGNORECASE)
_TARGET_NUMERIC_RE = re.compile(r"^0*(\d{1,3})(?!\d)\s*[.)\-–—]\s*(?=\S)")


def _valid_printed_number(value: Any) -> int | None:
  # Never truncate floats or treat booleans as question numbers.
  if type(value) is int:
    number = value
  elif isinstance(value, str) and re.fullmatch(r"[0-9]{1,3}", value):
    number = int(value)
  else:
    return None
  return number if 1 <= number <= indexer.MAX_QUESTION_NUMBER else None


def _observed_question_number(question: dict[str, Any]) -> int:
  printed = _valid_printed_number(question.get("printedQuestionNumber"))
  return printed if printed is not None else int(question["questionNumber"])


def _question_identity(question: dict[str, Any]) -> dict[str, Any]:
  return {"canonicalQuestionNumber": int(question["questionNumber"]),
          "observedQuestionNumber": _observed_question_number(question),
          "numberSource": "printed" if _valid_printed_number(question.get("printedQuestionNumber")) is not None else "canonical"}


def _keyword_header(text: str) -> tuple[re.Match | None, str]:
  match = indexer.QUESTAO_RE.match(text) or indexer.ITEM_RE.match(text)
  if match:
    return match, "legacy_keyword"
  return _KEYWORD_SEPARATOR_RE.match(text), "keyword_separator"


def _leading_keyword_decoration(text: str) -> tuple[str, bool]:
  # Only a decoration-only prefix immediately before an anchored keyword.
  # Leave all body text and the original observation untouched.
  offset = 0
  saw_decoration = False
  for char in text:
    if char.isspace():
      offset += 1
    elif unicodedata.category(char) == "Co" or char in "•◦▪▫►▸▶➤➢→":
      offset += 1
      saw_decoration = True
    else:
      break
  remainder = text[offset:]
  if saw_decoration and _keyword_header(remainder)[0]:
    return remainder, True
  return text, False


def _target_question_matches(
  lines: list[dict[str, Any]],
  markers: list[dict[str, Any]],
  question: dict[str, Any],
) -> list[dict[str, Any]]:
  """Exact number/page matching; no response evidence or fuzzy substitution."""
  identity = _question_identity(question)
  number = identity["observedQuestionNumber"]
  page = int(question["pageStart"])
  legacy = {(m["page"], m["top"], m["x0"], m["text"]): m
            for m in _unique_match(markers, number, page)}
  repeated = indexer._repeated_line_keys(as_question_marker_lines(lines))
  matches = []
  for line in lines:
    if int(line.get("page") or 0) != page:
      continue
    original = str(line.get("text") or "")
    text, decorated = _leading_keyword_decoration(original.strip())
    match, grammar = _keyword_header(text)
    family, kind = "keyword", "keyword"
    if not match:
      match = _ORDINAL_ITEM_RE.match(text)
      grammar = "ordinal_item"
    if not match:
      # Dash + isolated A-E is a parent-child header, not a new question.
      if indexer.PARENT_CHILD_RE.match(text) or indexer.ROMAN_RE.match(text):
        continue
      key = (page, float(line.get("top") or 0.0), float(line.get("x0") or 0.0), original.strip())
      existing = legacy.get(key)
      if existing and existing["family"] != "keyword":
        matches.append({**existing, **identity, "text": original,
                        "matchGrammar": "numeric_separator" if existing["family"] == "separator" else "legacy_bare_numeric",
                        "leadingDecorationNormalized": False})
        continue
      match = _TARGET_NUMERIC_RE.match(text)
      grammar, family, kind = "numeric_separator", "separator", "numeric"
      if match:
        rest = text[match.end(1):]
        if (rest.startswith(".") and rest[1:2].isdigit()) or indexer._line_key(text) in repeated:
          continue
    if not match or int(match.group(1)) != number:
      continue
    matches.append({"number": number, "page": page,
                    "top": float(line.get("top") or 0.0), "x0": float(line.get("x0") or 0.0),
                    "family": family, "kind": kind, "text": original,
                    **identity, "matchGrammar": grammar, "leadingDecorationNormalized": decorated})
  return matches


def as_question_marker_lines(lines: list[dict[str, Any]]) -> list[dict[str, Any]]:
  shaped: list[dict[str, Any]] = []
  for line in lines:
    shaped.append({
      "text": str(line.get("text") or ""),
      "page": int(line.get("page") or 0),
      "bbox": [line.get("x0") or 0.0, line.get("top") or 0.0,
               line.get("x1") or 0.0, line.get("bottom") or 0.0],
    })
  return shaped


def detect_question_markers(lines: list[dict[str, Any]]) -> list[dict[str, Any]]:
  keyword, separator, bare = indexer._extract_families(as_question_marker_lines(lines))
  markers: list[dict[str, Any]] = []
  for family, items in (("keyword", keyword), ("separator", separator), ("bare", bare)):
    for item in items:
      markers.append({
        "number": int(item["number"]),
        "page": int(item["page"]),
        "top": float(item["top"]),
        "x0": float(item["x0"]),
        "family": family,
        "kind": item["kind"],
        "text": item["text"],
      })
  markers.sort(key=lambda marker: (_FAMILY_ORDER.index(marker["family"]), marker["page"], marker["top"]))
  return markers


def index_document_by_id(index: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
  documents: dict[str, dict[str, Any]] = {}
  for document in (index or {}).get("documents", []):
    documents[document["documentId"]] = document
  return documents


def index_questions(document: dict[str, Any] | None) -> list[dict[str, Any]]:
  if not document:
    return []
  return list(document.get("questions") or [])


def find_question(questions: list[dict[str, Any]], question_id: str) -> dict[str, Any] | None:
  for question in questions:
    if question.get("questionId") == question_id:
      return question
  return None


def next_question_in_order(questions: list[dict[str, Any]], question_id: str) -> dict[str, Any] | None:
  for index, question in enumerate(questions):
    if question.get("questionId") == question_id:
      return questions[index + 1] if index + 1 < len(questions) else None
  return None


def expected_pages(question: dict[str, Any]) -> list[int]:
  start = int(question.get("pageStart") or 1)
  end = int(question.get("pageEnd") or start)
  if end < start:
    end = start
  return list(range(start, end + 1))


def _page_height(bundle: observations.ObservationBundle, page: int) -> float:
  # Observed bboxes live in the same coordinate system as the page they came
  # from. OCR bundles carry raster/pixel bboxes, so imageHeight must win over
  # pdfHeight (an OCR payload can carry both; mixing them would collapse the
  # boundary). Native bundles have imageHeight=None and fall back to pdfHeight.
  geometry = bundle.page_geometry.get(page) or {}
  for key in ("imageHeight", "pdfHeight"):
    value = geometry.get(key)
    if value:
      return float(value)
  heights = [line.bbox[3] for line in bundle.lines if line.page == page]
  return float(max(heights)) if heights else 0.0


def _page_width(
  bundle: observations.ObservationBundle,
  page: int,
) -> float:
  geometry = (
    bundle.page_geometry.get(
      page
    )
    or {}
  )

  for key in (
    "imageWidth",
    "pdfWidth",
  ):
    value = geometry.get(
      key
    )

    if value:
      return float(
        value
      )

  widths = [
    line.bbox[2]
    for line in bundle.lines
    if line.page == page
  ]

  return (
    float(
      max(
        widths
      )
    )
    if widths
    else 0.0
  )


def _unique_match(markers: list[dict[str, Any]], number: int, page: int) -> list[dict[str, Any]]:
  return [marker for marker in markers if marker["number"] == number and marker["page"] == page]


def _match_reason(matches: list[dict[str, Any]], label: str) -> str | None:
  if len(matches) == 1:
    return None
  if not matches:
    return f"{label}_marker_not_found"
  return f"{label}_marker_ambiguous"


def _word_rows(bundle: observations.ObservationBundle, page: int,
               words: list[observations.ObservedWord] | None = None) -> list[observations.ObservedLine]:
  """Local geometry view; never modifies observation adapter defaults or tokens."""
  local = [w for w in (bundle.words if words is None else words) if w.page == page]
  heights = [w.bbox[3] - w.bbox[1] for w in local if w.bbox[3] > w.bbox[1]]
  tolerance = max(3.0, statistics.median(heights) * 0.15) if heights else 3.0
  return observations.group_words_into_lines(local, _page_width(bundle, page), y_tolerance=tolerance)


def _internal_numbered_run(anchor: observations.ObservedWord, words: list[observations.ObservedWord]) -> bool:
  """A short, aligned run of 3+ numbered subitems is not header evidence."""
  height = anchor.bbox[3]-anchor.bbox[1]
  numbered = []
  for word in words:
    match = re.fullmatch(r"([0-9]{1,3})([.)])",word.text)
    if (match and abs(word.bbox[0]-anchor.bbox[0]) <= height
        and 0.5*height <= word.bbox[3]-word.bbox[1] <= 2.5*height):
      numbered.append((word,int(match.group(1)),match.group(2)))
  numbered.sort(key=lambda item:item[0].bbox[1])
  for i in range(len(numbered)-2):
    triple = numbered[i:i+3]
    if (any(w is anchor for w,_,_ in triple)
        and len({suffix for _,_,suffix in triple}) == 1
        and all(b[1] == a[1]+1 and 0 < b[0].bbox[1]-a[0].bbox[1] <= height*3.5
                for a,b in zip(triple,triple[1:]))):
      return True
  return False


def _word_question_matches(bundle: observations.ObservationBundle, question: dict[str, Any]) -> list[dict[str, Any]]:
  # Build a target-local baseline, not a global row whose tall noise can bridge
  # unrelated Y bands. Every token remains an observed word with its own index.
  page = int(question["pageStart"])
  number = _observed_question_number(question)
  page_words = [w for w in bundle.words if w.page == page and w.text.strip()]
  local_rows = []
  for anchor in page_words:
    keyword = re.fullmatch(r"(?:QUEST[ÃA]O|ITEM)[:\-–—]?",anchor.text,re.IGNORECASE)
    numeric = re.fullmatch(r"([0-9]{1,3})(?:[.)\-–—]|\.?[º°])",anchor.text)
    if not keyword and not (numeric and int(numeric.group(1)) == number):
      continue
    h = anchor.bbox[3]-anchor.bbox[1]
    if h <= 0:
      continue
    if numeric and _internal_numbered_run(anchor,page_words):
      continue
    band = [w for w in page_words if 0.5*h <= w.bbox[3]-w.bbox[1] <= 2*h
            and abs(_center_y(w.bbox)-_center_y(anchor.bbox)) <= h*0.45]
    # Do not promote an internal reference, decimal, or parent-child suffix.
    if any(w.bbox[0] < anchor.bbox[0] and 0 <= anchor.bbox[0]-w.bbox[2] <= h*2
           and any(c.isalnum() for c in w.text) for w in band):
      continue
    tokens = [anchor]
    for word in sorted((w for w in band if w.bbox[0] >= anchor.bbox[2]),key=lambda w:w.bbox[0]):
      if word.bbox[0]-tokens[-1].bbox[2] > h*2 or len(tokens)>=8:
        break
      tokens.append(word)
    local_rows.append(observations.ObservedLine(page," ".join(w.text for w in tokens),
      (anchor.bbox[0],anchor.bbox[1],max(w.bbox[2] for w in tokens),max(w.bbox[3] for w in tokens)),
      [w.word_index for w in tokens],source="word_geometry"))
  shaped = observations.ObservationBundle([], local_rows, [], {}, "word_geometry").lines_as_region_input()
  candidates = _target_question_matches(shaped, detect_question_markers(shaped), question)
  lookup = {(w.page, w.word_index): w for w in bundle.words}
  result = []
  for candidate in candidates:
    row = next(r for r in local_rows if r.bbox[0] == candidate["x0"] and r.bbox[1] == candidate["top"])
    tokens = [lookup[(row.page, i)] for i in row.word_indexes]
    # Bare numbers in prose/math are insufficient word evidence.
    if candidate["matchGrammar"] == "legacy_bare_numeric":
      continue
    text, _ = _leading_keyword_decoration(row.text.strip())
    match, _ = _keyword_header(text)
    match = match or _ORDINAL_ITEM_RE.match(text)
    if match:
      end = row.text.find(text) + match.end()
      offset, header = 0, []
      for token in tokens:
        if offset >= end:
          break
        header.append(token)
        offset += len(token.text) + 1
    else:
      if not re.fullmatch(r"[0-9]{1,3}[.)\-–—]", tokens[0].text):
        continue
      header = tokens[:1]
      height = _page_height(bundle, row.page)
      if not height * 0.05 <= header[0].bbox[1] < height * 0.93:
        continue
      if len(tokens) < 3 or not any(c.isalpha() for c in tokens[1].text):
        continue
    # Keyword/number must be adjacent observed tokens, close in X and Y.
    if any(b.bbox[0] - a.bbox[2] > max(4.0, 1.5 * max(a.bbox[3]-a.bbox[1], b.bbox[3]-b.bbox[1]))
           for a, b in zip(header, header[1:])):
      continue
    box = [min(w.bbox[0] for w in header), min(w.bbox[1] for w in header),
           max(w.bbox[2] for w in header), max(w.bbox[3] for w in header)]
    minimal = " ".join(w.text for w in header)
    result.append({**candidate, "top": box[1], "x0": box[0], "bbox": box,
                   "text": minimal, "reconstructedText": minimal,
                   "wordIndexes": [w.word_index for w in header],
                   "source": "word_geometry", "matchSource": "word_geometry",
                   "evidence": ["frozen_index_expected_identity", "observed_header_tokens",
                                "same_page_y_band", "ordered_adjacent_x"]})
  return result


def _resolve_question_starts(bundle: observations.ObservationBundle, lines: list[dict[str, Any]],
                             markers: list[dict[str, Any]], entries: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
  """Line-first for current, next and peers; ambiguities never trigger fallback."""
  resolved = {}
  raw = {}
  rows_by_page = {}
  for entry in entries:
    qid = entry["questionId"]
    matches = _target_question_matches(lines, markers, entry)
    if matches:
      resolved[qid] = [{**m, "matchSource": "line"} for m in matches]
      continue
    page = int(entry["pageStart"])
    if page not in rows_by_page:
      rows_by_page[page] = _word_rows(bundle, page)
    raw[qid] = _word_question_matches(bundle, entry)
  for entry in entries:
    qid = entry["questionId"]
    if qid not in raw:
      continue
    candidates = raw[qid]
    # Do not pick one plausible duplicate by how convenient its support is.
    if not candidates or all(c["kind"] == "keyword" for c in candidates):
      resolved[qid] = candidates
      continue
    resolved[qid] = []
    for candidate in candidates:
      supported = (candidate if candidate["kind"] == "keyword" else
                   _corroborate_word_numeric(bundle, entries, entry, candidate, raw, resolved, rows_by_page))
      if supported:
        resolved[qid].append(supported)
  return resolved


def _numeric_style(marker: dict[str, Any]) -> tuple[bool, str] | None:
  match = re.match(r"^([0-9]{1,3})([.)\-–—])", marker["text"])
  return (match.group(1).startswith("0"),match.group(2)) if match else None


def _corroborate_word_numeric(bundle: observations.ObservationBundle, entries: list[dict[str, Any]],
                             entry: dict[str, Any], candidate: dict[str, Any],
                             raw: dict[str, list[dict[str, Any]]], resolved: dict[str, list[dict[str, Any]]],
                             rows_by_page: dict[int, list[observations.ObservedLine]]) -> dict[str, Any] | None:
  qid = entry["questionId"]
  page = int(entry["pageStart"])
  corroboration = []
  for position, peer_entry in enumerate(entries):
    if peer_entry["questionId"] == qid or int(peer_entry["pageStart"]) != page:
      continue
    peers = raw.get(peer_entry["questionId"], resolved.get(peer_entry["questionId"], []))
    if peer_entry["questionId"] not in raw and len(peers) != 1:
      continue  # Existing line ambiguity is never word corroboration.
    peers = [p for p in peers if _numeric_style(candidate) == _numeric_style(p)]
    if len(peers) != 1:
      continue
    peer = peers[0]
    dx, dy = peer["x0"]-candidate["x0"], peer["top"]-candidate["top"]
    index_delta = position - entries.index(entry)
    aligned = abs(dx) <= max(12, _page_width(bundle,page)*0.025) and dy * index_delta > 0
    parallel = abs(dx) >= max(COLUMN_MIN_X_GAP_ABS, COLUMN_MIN_X_GAP_RATIO*_page_width(bundle,page)) and abs(dy) <= max(COLUMN_MAX_Y_GAP_ABS,COLUMN_MAX_Y_GAP_RATIO*_page_height(bundle,page))
    if (aligned or parallel) and _numeric_style(candidate) == _numeric_style(peer):
      corroboration.append("index_backed_spatial_neighbor")
  page_entries = [e for e in entries if int(e["pageStart"]) == page]
  rows = rows_by_page[page]
  # Single-question pages may have no peer. Require top-body header, a damaged
  # original observation and multiple aligned observed body rows, not a number alone.
  header_height = candidate["bbox"][3]-candidate["bbox"][1]
  collapsed = any(l.page == page and l.bbox[3]-l.bbox[1] > header_height*6
                  and l.bbox[2]-l.bbox[0] > _page_width(bundle,page)*0.6 for l in bundle.lines)
  body = [r for r in rows if candidate["top"] < r.bbox[1] < candidate["top"]+_page_height(bundle,page)*0.5
          and abs(r.bbox[0]-candidate["x0"]) < _page_width(bundle,page)*0.05 and len(r.text.split()) >= 2]
  if (len(page_entries)==1 and collapsed and len(body)>=2
      and candidate["top"] < _page_height(bundle,page)*0.25
      and _page_width(bundle,page)*0.04 < candidate["x0"] < _page_width(bundle,page)*0.25):
    corroboration.append("single_indexed_start_top_body_collapsed_observation")
  return {**candidate, "evidence": candidate["evidence"] + sorted(set(corroboration))} if corroboration else None


def _verified_question_starts(
  lines: list[dict[str, Any]],
  markers: list[dict[str, Any]],
  document_questions: list[dict[str, Any]] | None,
  page: int,
  resolved: dict[str, list[dict[str, Any]]] | None = None,
) -> list[dict[str, Any]]:
  starts = []
  for entry in document_questions or []:
    if int(entry.get("pageStart") or 0) != page:
      continue
    matches = resolved[entry["questionId"]] if resolved is not None else _target_question_matches(lines, markers, entry)
    status = "unique" if len(matches) == 1 else "ambiguous" if matches else "missing"
    starts.append({"questionId": entry.get("questionId"), **_question_identity(entry),
                   "matchCount": len(matches), "status": status,
                   "matchGrammar": matches[0]["matchGrammar"] if status == "unique" else None,
                   "matchSource": matches[0].get("matchSource") if status == "unique" else None,
                   "marker": matches[0] if status == "unique" else None})
  return starts


def _infer_parallel_column_limits(
  bundle: observations.ObservationBundle,
  markers: list[dict[str, Any]],
  current: dict[str, Any],
) -> dict[str, Any] | None:
  page = int(
    current[
      "page"
    ]
  )

  page_width = _page_width(
    bundle,
    page,
  )

  page_height = _page_height(
    bundle,
    page,
  )

  if (
    page_width <= 0
    or page_height <= 0
  ):
    return None

  min_x_gap = max(
    COLUMN_MIN_X_GAP_ABS,
    COLUMN_MIN_X_GAP_RATIO
    * page_width,
  )

  max_y_gap = max(
    COLUMN_MAX_Y_GAP_ABS,
    COLUMN_MAX_Y_GAP_RATIO
    * page_height,
  )

  peers = []
  seen = set()

  for marker in markers:
    if (
      int(
        marker.get(
          "page"
        )
        or 0
      )
      != page
    ):
      continue

    if (
      int(
        marker.get(
          "number"
        )
        or -1
      )
      == int(
        current.get(
          "number"
        )
        or -2
      )
      and abs(
        float(
          marker.get(
            "top"
          )
          or 0
        )
        - float(
          current.get(
            "top"
          )
          or 0
        )
      )
      < 0.01
      and abs(
        float(
          marker.get(
            "x0"
          )
          or 0
        )
        - float(
          current.get(
            "x0"
          )
          or 0
        )
      )
      < 0.01
    ):
      continue

    x_gap = abs(
      float(
        marker.get(
          "x0"
        )
        or 0
      )
      - float(
        current.get(
          "x0"
        )
        or 0
      )
    )

    y_gap = abs(
      float(
        marker.get(
          "top"
        )
        or 0
      )
      - float(
        current.get(
          "top"
        )
        or 0
      )
    )

    if (
      x_gap < min_x_gap
      or y_gap > max_y_gap
    ):
      continue

    key = (
      int(
        marker.get(
          "number"
        )
        or 0
      ),
      round(
        float(
          marker.get(
            "top"
          )
          or 0
        ),
        2,
      ),
      round(
        float(
          marker.get(
            "x0"
          )
          or 0
        ),
        2,
      ),
    )

    if key in seen:
      continue

    seen.add(
      key
    )

    peers.append(
      marker
    )

  if not peers:
    return None

  current_x = float(
    current[
      "x0"
    ]
  )

  left = [
    marker
    for marker in peers
    if float(
      marker[
        "x0"
      ]
    )
    < current_x
  ]

  right = [
    marker
    for marker in peers
    if float(
      marker[
        "x0"
      ]
    )
    > current_x
  ]

  # A marker with strong parallel peers on both sides looks like 3+ columns or
  # another layout we do not yet understand. Abstain instead of guessing.
  if (
    left
    and right
  ):
    return {
      "ambiguous":
        True,

      "reason":
        "parallel_columns_multiple_sides",
    }

  side = (
    left
    if left
    else right
  )

  peer = min(
    side,
    key=lambda marker: abs(
      float(
        marker[
          "x0"
        ]
      )
      - current_x
    ),
  )

  peer_x = float(
    peer[
      "x0"
    ]
  )

  split = (
    current_x
    + peer_x
  ) / 2.0

  min_side = (
    COLUMN_MIN_SIDE_RATIO
    * page_width
  )

  if (
    split < min_side
    or (
      page_width
      - split
    ) < min_side
  ):
    return None

  if current_x > peer_x:
    x0 = split
    x1 = page_width
    side_name = "right"
  else:
    x0 = 0.0
    x1 = split
    side_name = "left"

  return {
    "ambiguous":
      False,

    "x0":
      x0,

    "x1":
      x1,

    "split":
      split,

    "side":
      side_name,

    "peerMarker":
      peer,
  }


def _marker_inside_x_limits(
  marker: dict[str, Any],
  limits: dict[str, Any] | None,
) -> bool:
  if not limits:
    return True

  x = float(
    marker.get(
      "x0"
    )
    or 0
  )

  return (
    float(
      limits[
        "x0"
      ]
    )
    <= x
    < float(
      limits[
        "x1"
      ]
    )
  )


def compute_question_boundary(
  bundle: observations.ObservationBundle,
  question: dict[str, Any],
  next_question: dict[str, Any] | None,
  expected: list[int],
  document_questions: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
  """Return the neutral boundary metadata for one question.

  ``bundle`` may contain several pages and several questions. The returned
  metadata describes which vertical slice of each page belongs to ``question``.
  """
  marker_lines = bundle.lines_as_region_input()
  markers = detect_question_markers(marker_lines)
  pages = list(expected)

  result: dict[str, Any] = {
    "questionId": question.get("questionId"),
    "questionNumber": question.get("questionNumber"),
    **_question_identity(question),
    "reliable": True,
    "reason": "ok",
    "pages": pages,
    "expectedPages": pages,
    "currentMarker": None,
    "nextMarker": None,
    "boundaryMode": "vertical",
    "columnLimits": None,
    "columnEvidence": None,
    "verifiedQuestionStarts": [],
    "columnPeerContextAvailable": document_questions is not None,
    "pageLimits": {},
  }

  if int(question.get("pageStart") or 0) not in pages:
    result["reliable"] = False
    result["reason"] = "current_page_not_loaded"
    return result

  entries = list(document_questions or [])
  for entry in [question, next_question]:
    if entry and not any(e["questionId"] == entry["questionId"] for e in entries):
      entries.append(entry)
  resolved = _resolve_question_starts(bundle, marker_lines, markers, entries)
  verified_starts = _verified_question_starts(marker_lines, markers, document_questions, int(question["pageStart"]), resolved)
  result["verifiedQuestionStarts"] = verified_starts
  current_matches = resolved[question["questionId"]]
  current_reason = _match_reason(current_matches, "current")
  if current_reason:
    result["reliable"] = False
    result["reason"] = current_reason
    return result
  current = current_matches[0]
  result["currentMarker"] = current
  result["questionStartMatchSource"] = current["matchSource"]

  column_limits = None

  single_page_question = (
    int(
      question.get(
        "pageStart"
      )
      or 0
    )
    == int(
      question.get(
        "pageEnd"
      )
      or 0
    )
  )

  if single_page_question:
    # No global numeric marker is evidence of another question. Missing or
    # ambiguous index entries never supply a peer, even if one match is closer.
    peers = [{**start["marker"], "questionId": start["questionId"]}
             for start in verified_starts
             if start["status"] == "unique" and start["questionId"] != question.get("questionId")]
    inferred_columns = (
      _infer_parallel_column_limits(
        bundle,
        peers,
        current,
      )
    )

    if (
      inferred_columns
      and inferred_columns.get(
        "ambiguous"
      )
    ):
      result[
        "reliable"
      ] = False

      result[
        "reason"
      ] = str(
        inferred_columns.get(
          "reason"
        )
        or "column_boundary_ambiguous"
      )

      return result

    if inferred_columns:
      peer = inferred_columns["peerMarker"]
      result["columnEvidence"] = {
        "peerQuestionId": peer["questionId"],
        "peerCanonicalQuestionNumber": peer["canonicalQuestionNumber"],
        "peerObservedQuestionNumber": peer["observedQuestionNumber"],
        "peerNumberSource": peer["numberSource"],
        "peerMatchGrammar": peer["matchGrammar"],
        "peerMarker": peer,
        "evidence": ["frozen_index_same_page", "unique_target_match",
                     "parallel_x_separation", "parallel_y_alignment"],
      }
      column_limits = {
        "x0":
          float(
            inferred_columns[
              "x0"
            ]
          ),

        "x1":
          float(
            inferred_columns[
              "x1"
            ]
          ),
      }

      result[
        "boundaryMode"
      ] = "two_column"

      result[
        "columnLimits"
      ] = {
        **column_limits,

        "split":
          float(
            inferred_columns[
              "split"
            ]
          ),

        "side":
          inferred_columns[
            "side"
          ],

        "peerMarker":
          inferred_columns[
            "peerMarker"
          ],
      }

  next_marker: dict[str, Any] | None = None
  next_in_pages = bool(next_question) and int(next_question.get("pageStart") or 0) in pages
  if next_in_pages:
    next_matches = resolved[next_question["questionId"]]
    next_reason = _match_reason(next_matches, "next")
    if next_reason:
      result["reliable"] = False
      result["reason"] = next_reason
      return result
    next_marker = next_matches[0]
    result["nextMarker"] = next_marker

  if next_marker is not None:
    last_page = int(next_marker["page"])
  else:
    last_page = min(int(question.get("pageEnd") or pages[-1]), pages[-1])

  result["pages"] = [page for page in pages if int(question["pageStart"]) <= page <= last_page]

  page_limits: dict[int, dict[str, float]] = {}

  for page in result["pages"]:
    top = (
      float(
        current[
          "top"
        ]
      )
      if page
      == int(
        current[
          "page"
        ]
      )
      else 0.0
    )

    bottom = _page_height(
      bundle,
      page,
    )

    next_same_column = (
      next_marker is not None
      and (
        column_limits is None
        or _marker_inside_x_limits(
          next_marker,
          column_limits,
        )
      )
    )

    if (
      next_marker is not None
      and page
      == int(
        next_marker[
          "page"
        ]
      )
      and next_same_column
    ):
      bottom = float(
        next_marker[
          "top"
        ]
      )

    if bottom < top:
      bottom = top

    limits = {
      "top":
        top,

      "bottom":
        bottom,
    }

    if (
      column_limits is not None
      and page
      == int(
        current[
          "page"
        ]
      )
    ):
      limits[
        "x0"
      ] = float(
        column_limits[
          "x0"
        ]
      )

      limits[
        "x1"
      ] = float(
        column_limits[
          "x1"
        ]
      )

    page_limits[
      page
    ] = limits

  result[
    "pageLimits"
  ] = page_limits

  return result


def _center_x(bbox: Any) -> float:
  values = list(bbox or [])

  if len(values) < 4:
    return 0.0

  return (
    float(
      values[0]
    )
    + float(
      values[2]
    )
  ) / 2.0


def _center_y(bbox: Any) -> float:
  values = list(bbox or [])

  if len(values) < 4:
    return 0.0

  return (
    float(
      values[1]
    )
    + float(
      values[3]
    )
  ) / 2.0


def _within_boundary(
  boundary: dict[str, Any],
  page: int,
  center_x: float,
  center_y: float,
) -> bool:
  limits = (
    boundary.get(
      "pageLimits"
    )
    or {}
  ).get(
    page
  )

  if limits is None:
    return False

  if not (
    float(
      limits[
        "top"
      ]
    )
    <= center_y
    < float(
      limits[
        "bottom"
      ]
    )
  ):
    return False

  if (
    "x0"
    in limits
    and center_x
    < float(
      limits[
        "x0"
      ]
    )
  ):
    return False

  if (
    "x1"
    in limits
    and center_x
    >= float(
      limits[
        "x1"
      ]
    )
  ):
    return False

  return True


def _reconstruct_local_lines(bundle: observations.ObservationBundle, boundary: dict[str, Any],
                             words: list[observations.ObservedWord],
                             lines: list[observations.ObservedLine]) -> list[observations.ObservedLine]:
  """Only scoped words enter reconstruction; healthy pages keep original lines."""
  result, diagnostics = [], []
  for page in boundary.get("pages") or []:
    local_words = [w for w in words if w.page == page]
    local_lines = [l for l in lines if l.page == page]
    reason = None
    rebuilt = []
    if boundary.get("reliable") and local_words:
      rebuilt = _word_rows(bundle, page, local_words)
      limits = boundary["pageLimits"][page]
      originals = [l for l in bundle.lines if l.page == page
                   and l.bbox[3] > limits["top"] and l.bbox[1] < limits["bottom"]]
      heights = [w.bbox[3]-w.bbox[1] for w in local_words if w.bbox[3]>w.bbox[1]]
      median_height = statistics.median(heights) if heights else 0
      if not local_lines:
        reason = "no_filtered_lines"
      elif "x0" in limits and any(l.bbox[0] < limits["x0"] or l.bbox[2] > limits["x1"] for l in originals):
        reason = "original_lines_cross_column_boundary"
      elif any(l.order_ambiguous for l in local_lines):
        reason = "original_line_order_ambiguous"
      elif len(rebuilt)>=3 and any(l.bbox[3]-l.bbox[1] > median_height*4
                                  and l.bbox[2]-l.bbox[0] > _page_width(bundle,page)*0.6 for l in originals):
        reason = "collapsed_full_width_line"
      else:
        current = boundary.get("currentMarker") or {}
        if current.get("page") == page and current.get("matchSource") == "word_geometry":
          shape = observations.ObservationBundle([],local_lines,[],{},bundle.source).lines_as_region_input()
          identity = {"questionNumber": current["canonicalQuestionNumber"],
                      "printedQuestionNumber": current["observedQuestionNumber"], "pageStart": page}
          if not _target_question_matches(shape, detect_question_markers(shape), identity):
            reason = "word_start_not_preserved_in_local_lines"
    if reason:
      for line in rebuilt:
        line.source = "reconstructed_from_words"
      result.extend(rebuilt)
    else:
      result.extend(local_lines)
    diagnostics.append({"page": page, "used": reason is not None,
                        "reason": reason or ("healthy_lines_preserved" if boundary.get("reliable") else "boundary_unreliable"),
                        "inputWordCount": len(local_words), "outputLineCount": len(rebuilt) if reason else 0})
  used = [d for d in diagnostics if d["used"]]
  boundary["lineReconstruction"] = {"used": bool(used),
    "reason": ";".join(dict.fromkeys(d["reason"] for d in used)) if used else "not_required",
    "inputWordCount": len(words), "outputLineCount": sum(d["outputLineCount"] for d in used), "pages": diagnostics}
  if used:
    result.sort(key=lambda l: (l.page,l.bbox[1],l.bbox[0]))
    # Reindex copies only: untouched original ObservedLine objects stay immutable.
    result = [observations.ObservedLine(l.page,l.text,l.bbox,list(l.word_indexes),i,l.source,l.order_ambiguous)
              for i,l in enumerate(result)]
  return result


def filter_bundle(
  bundle: observations.ObservationBundle,
  boundary: dict[str, Any],
) -> observations.ObservationBundle:
  """Return a copy of ``bundle`` restricted to the question boundary.

  Boundaries are normally vertical. When conservative parallel-column evidence
  is available, pageLimits also carry x0/x1 and filtering becomes 2D.
  The original bundle is never mutated.
  """
  pages = set(
    boundary.get(
      "pages"
    )
    or []
  )

  words = [
    word
    for word in bundle.words
    if (
      word.page in pages
      and _within_boundary(
        boundary,
        word.page,
        _center_x(
          word.bbox
        ),
        _center_y(
          word.bbox
        ),
      )
    )
  ]

  lines = [
    line
    for line in bundle.lines
    if (
      line.page in pages
      and _within_boundary(
        boundary,
        line.page,
        _center_x(
          line.bbox
        ),
        _center_y(
          line.bbox
        ),
      )
    )
  ]

  components = [
    component
    for component
    in bundle.visual_components
    if (
      component.page in pages
      and _within_boundary(
        boundary,
        component.page,
        _center_x(
          component.bbox
        ),
        _center_y(
          component.bbox
        ),
      )
    )
  ]

  lines = _reconstruct_local_lines(bundle, boundary, words, lines)
  return observations.ObservationBundle(
    words=words,
    lines=lines,
    visual_components=components,
    page_geometry=dict(
      bundle.page_geometry
    ),
    source=bundle.source,
  )


def filter_visual_items(
  items: list[dict[str, Any]],
  boundary: dict[str, Any],
) -> list[dict[str, Any]]:
  """Filter visual evidence/components by the same 1D or 2D boundary."""
  kept: list[dict[str, Any]] = []

  pages = set(
    boundary.get(
      "pages"
    )
    or []
  )

  for item in items:
    page = int(
      item.get(
        "page"
      )
      or 0
    )

    if page not in pages:
      continue

    bbox = item.get(
      "bbox"
    )

    if _within_boundary(
      boundary,
      page,
      _center_x(
        bbox
      ),
      _center_y(
        bbox
      ),
    ):
      kept.append(
        item
      )

  return kept
