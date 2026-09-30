from __future__ import annotations

from typing import Any

import audit_holdout_question_index as indexer
import audit_observations as observations

"""Neutral intra-page question boundary.

This module separates the region of a single selected question from the other
questions that share the same page(s). It uses only neutral information:

- the frozen question index (document order, questionId, questionNumber,
  pageStart, pageEnd, sequenceRun);
- the page numbers of the question;
- the text and vertical position of observed question-start markers.

It never uses option labels, option count, response mode, layout or Ground
Truth content to locate the boundary. When the current or the next question
marker cannot be located unambiguously the boundary is declared
``reliable=False`` so downstream fusion withholds unsafe emissions.

The marker grammar is the same neutral grammar used to build the question
index (QUESTAO_RE / ITEM_RE / NUMERIC_RE / BARE_NUMERIC_RE).
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
) -> dict[str, Any]:
  """Return the neutral boundary metadata for one question.

  ``bundle`` may contain several pages and several questions. The returned
  metadata describes which vertical slice of each page belongs to ``question``.
  """
  markers = detect_question_markers(bundle.lines_as_region_input())
  pages = list(expected)

  result: dict[str, Any] = {
    "questionId": question.get("questionId"),
    "questionNumber": question.get("questionNumber"),
    "reliable": True,
    "reason": "ok",
    "pages": pages,
    "expectedPages": pages,
    "currentMarker": None,
    "nextMarker": None,
    "boundaryMode": "vertical",
    "columnLimits": None,
    "pageLimits": {},
  }

  if int(question.get("pageStart") or 0) not in pages:
    result["reliable"] = False
    result["reason"] = "current_page_not_loaded"
    return result

  current_matches = _unique_match(markers, int(question["questionNumber"]), int(question["pageStart"]))
  current_reason = _match_reason(current_matches, "current")
  if current_reason:
    result["reliable"] = False
    result["reason"] = current_reason
    return result
  current = current_matches[0]
  result["currentMarker"] = current

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
    inferred_columns = (
      _infer_parallel_column_limits(
        bundle,
        markers,
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
    next_matches = _unique_match(markers, int(next_question["questionNumber"]), int(next_question["pageStart"]))
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
