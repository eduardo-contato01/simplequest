from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import audit_response_structure as response_structure

_PRIVATE_USE_RE = re.compile(r"[\ue000-\uf8ff]")
REFERENCE_COMMAND_RE = re.compile(r"\b(item|itens|quest[ãa]o|quest[õo]es)\b", re.IGNORECASE)
LABEL_TOKEN_RE = re.compile(r"^\(?\s*([A-Ea-e])\s*\)?$")
CELL_LABEL_RE = re.compile(r"^\(\s*([A-Ea-e])\s*\)$|^([A-Ea-e])\s*[\)\.]$")


@dataclass
class ObservedWord:
  page: int
  text: str
  bbox: tuple[float, float, float, float]
  word_index: int = 0
  source: str = "unknown"

  def to_dict(self) -> dict[str, Any]:
    return {"page": self.page, "text": self.text, "bbox": list(self.bbox), "wordIndex": self.word_index, "source": self.source}


@dataclass
class ObservedLine:
  page: int
  text: str
  bbox: tuple[float, float, float, float]
  word_indexes: list[int] = field(default_factory=list)
  line_index: int = 0
  source: str = "unknown"
  order_ambiguous: bool = False

  def to_dict(self) -> dict[str, Any]:
    return {
      "page": self.page, "text": self.text, "bbox": list(self.bbox),
      "wordIndexes": self.word_indexes, "lineIndex": self.line_index,
      "source": self.source, "orderAmbiguous": self.order_ambiguous,
    }


@dataclass
class ObservedVisualComponent:
  page: int
  bbox: tuple[float, float, float, float]
  area: float
  width: float
  height: float
  fill: float
  source: str = "raster"

  def to_dict(self) -> dict[str, Any]:
    return {
      "page": self.page, "bbox": list(self.bbox), "area": self.area,
      "width": self.width, "height": self.height, "fill": self.fill, "source": self.source,
    }


@dataclass
class ObservationBundle:
  words: list[ObservedWord]
  lines: list[ObservedLine]
  visual_components: list[ObservedVisualComponent]
  page_geometry: dict[int, dict[str, Any]]
  source: str

  def lines_as_region_input(self) -> list[dict[str, Any]]:
    return [
      {
        "text": line.text, "page": line.page,
        "x0": line.bbox[0], "top": line.bbox[1], "x1": line.bbox[2], "bottom": line.bbox[3],
        "lineIndex": line.line_index, "role": "stem", "source": line.source,
      }
      for line in self.lines
    ]

  def words_as_region_input(self) -> list[dict[str, Any]]:
    return [
      {"page": word.page, "bbox": list(word.bbox), "wordIndex": word.word_index, "text": word.text}
      for word in self.words
    ]

  def visual_as_region_input(self) -> list[dict[str, Any]]:
    return [
      {"page": component.page, "bbox": list(component.bbox), "area": component.area,
       "width": component.width, "height": component.height, "fill": component.fill}
      for component in self.visual_components
    ]


def extract_text_markers(lines: list[dict[str, Any]]) -> list[dict[str, Any]]:
  # Only leading markers: generic native text can put an option letter inside a
  # word (e.g. "estrofe)"); intra-line scanning would fabricate markers.
  markers: list[dict[str, Any]] = []
  for line in lines:
    text = _PRIVATE_USE_RE.sub(" ", str(line.get("text") or ""))
    parsed = response_structure.parse_marker(text)
    if not parsed:
      continue
    markers.append({
      "label": parsed.get("label"),
      "markerKind": parsed.get("markerKind"),
      "subitemLabel": parsed.get("subitemLabel"),
      "parentQuestion": parsed.get("parentQuestion"),
      "labelCase": parsed.get("labelCase"),
      "markerShape": parsed.get("markerShape"),
      "separator": parsed.get("separator"),
      "responseField": parsed.get("responseField"),
      "text": parsed.get("text"),
      "page": int(line.get("page") or 0),
      "bbox": [line.get("x0"), line.get("top"), line.get("x1"), line.get("bottom")],
      "lineIndex": line.get("lineIndex"),
    })
  return markers


def _parent_child_markers(lines: list[dict[str, Any]]) -> list[dict[str, Any]]:
  markers: list[dict[str, Any]] = []
  for line in lines:
    parsed = response_structure.parse_marker(str(line.get("text") or ""))
    if not parsed or parsed.get("markerKind") != "parent_child":
      continue
    text_start = parsed.get("textStart") or 0
    markers.append({
      "label": None, "markerKind": "parent_child", "subitemLabel": parsed.get("subitemLabel"),
      "parentQuestion": parsed.get("parentQuestion"), "labelCase": parsed.get("labelCase"),
      "markerShape": "none", "separator": "dash", "responseField": "absent",
      "text": str(line.get("text") or "")[text_start:].strip(),
      "page": int(line.get("page") or 0), "bbox": [line.get("x0"), line.get("top"), line.get("x1"), line.get("bottom")],
      "lineIndex": line.get("lineIndex"),
    })
  return markers


def extract_instruction_context(lines: list[dict[str, Any]], question_label: int | str) -> list[dict[str, Any]]:
  # Generic: a command line that explicitly references the question label
  # ("item 75", "questão 90", "itens 73 e 74 e ... item 75").
  label = str(question_label)
  context: list[dict[str, Any]] = []
  for line in lines:
    text = str(line.get("text") or "")
    if not REFERENCE_COMMAND_RE.search(text):
      continue
    numbers = set(re.findall(r"\b\d{1,3}\b", text))
    if label in numbers:
      context.append(line)
  return context


def render_pdf_page(pdf_path: str | Path, page: int, dpi: float = 160.0, cache_dir: str | Path | None = None) -> dict[str, Any]:
  import pdfplumber

  path = Path(pdf_path)
  stat = path.stat()
  fingerprint = hashlib.sha256(
    f"{path.resolve()}|{stat.st_size}|{int(stat.st_mtime)}|{page}|{dpi}".encode("utf-8")
  ).hexdigest()[:16]
  cache_root = Path(cache_dir) if cache_dir else Path("outputs/audit/native-render")
  output = cache_root / fingerprint / f"page-{page:02d}-dpi{int(dpi)}.png"
  if not output.exists():
    output.parent.mkdir(parents=True, exist_ok=True)
    with pdfplumber.open(str(path)) as pdf:
      rendered = pdf.pages[page - 1].to_image(resolution=dpi)
      rendered.original.save(output)
  return {"path": str(output), "page": page, "dpi": dpi, "scale": dpi / 72.0}


def _word_bbox(word: Any) -> list[float]:
  bbox = word.get("bbox") if isinstance(word, dict) else getattr(word, "bbox", None)
  return [float(value) for value in bbox]


def resegment_words_into_cells(
  words: list[Any],
  region: dict[str, Any] | None = None,
  x_tolerance: float = 40.0,
  y_tolerance: float = 40.0,
) -> list[dict[str, Any]]:
  anchors: list[dict[str, Any]] = []
  for index, word in enumerate(words):
    text = str(word.get("text") if isinstance(word, dict) else getattr(word, "text", "")).strip()
    bbox = _word_bbox(word)
    if region is not None:
      if int((word.get("page") if isinstance(word, dict) else getattr(word, "page", 0)) or 0) != int(region.get("page") or 0):
        continue
      if bbox[1] < float(region.get("top", 0)) - 2 or bbox[3] > float(region.get("bottom", 10 ** 9)) + 2:
        continue
      if "x0" in region and bbox[0] < float(region["x0"]) - 2:
        continue
      if "x1" in region and bbox[0] > float(region["x1"]):
        continue
    match = CELL_LABEL_RE.match(text)
    if match:
      label = match.group(1) or match.group(2)
      anchors.append({"label": label.upper(), "bbox": bbox, "wordIndex": index})
  if len(anchors) < 3:
    return []

  def cluster(values: list[float], tolerance: float) -> list[float]:
    ordered = sorted(values)
    centers: list[float] = []
    for value in ordered:
      if centers and value - centers[-1] <= tolerance:
        centers[-1] = (centers[-1] + value) / 2.0
      else:
        centers.append(value)
    return centers

  def band(value: float, centers: list[float]) -> int:
    best = 0
    best_distance = None
    for index, center in enumerate(centers):
      distance = abs(value - center)
      if best_distance is None or distance < best_distance:
        best_distance = distance
        best = index
    return best

  column_centers = cluster([anchor["bbox"][0] for anchor in anchors], x_tolerance)
  row_centers = cluster([anchor["bbox"][1] for anchor in anchors], y_tolerance)
  cells: list[dict[str, Any]] = []
  for anchor in anchors:
    column = band(anchor["bbox"][0], column_centers)
    row = band(anchor["bbox"][1], row_centers)
    cells.append({
      "label": anchor["label"],
      "bbox": anchor["bbox"],
      "wordIndex": anchor["wordIndex"],
      "row": row,
      "column": column,
    })
  cells.sort(key=lambda cell: (cell["row"], cell["column"]))
  return cells


def group_words_into_lines(
  words: list[ObservedWord],
  page_width: float,
  y_tolerance: float = 3.0,
  column_gap_ratio: float = 0.35,
) -> list[ObservedLine]:
  by_page: dict[int, list[ObservedWord]] = {}
  for word in words:
    by_page.setdefault(word.page, []).append(word)
  lines: list[ObservedLine] = []
  for page in sorted(by_page):
    page_words = sorted(by_page[page], key=lambda w: (w.bbox[1], w.bbox[0]))
    rows: list[list[ObservedWord]] = []
    for word in page_words:
      placed = False
      for row in rows:
        row_top = min(w.bbox[1] for w in row)
        row_bottom = max(w.bbox[3] for w in row)
        overlap = min(row_bottom, word.bbox[3]) - max(row_top, word.bbox[1])
        if overlap >= (word.bbox[3] - word.bbox[1]) * 0.5 or abs(word.bbox[1] - row_top) <= y_tolerance:
          if _same_column(row, word, page_width, column_gap_ratio):
            row.append(word)
            placed = True
            break
      if not placed:
        rows.append([word])
    for row in rows:
      ordered = sorted(row, key=lambda w: w.bbox[0])
      x0 = min(w.bbox[0] for w in ordered)
      top = min(w.bbox[1] for w in ordered)
      x1 = max(w.bbox[2] for w in ordered)
      bottom = max(w.bbox[3] for w in ordered)
      text = " ".join(w.text for w in ordered if w.text.strip())
      ambiguous = (x1 - x0) > page_width * 0.6 and len(ordered) > 3
      lines.append(ObservedLine(
        page=page, text=text, bbox=(x0, top, x1, bottom),
        word_indexes=[w.word_index for w in ordered], source=ordered[0].source,
        order_ambiguous=ambiguous,
      ))
  lines.sort(key=lambda line: (line.page, line.bbox[1], line.bbox[0]))
  for index, line in enumerate(lines):
    line.line_index = index
  return lines


def _same_column(row: list[ObservedWord], word: ObservedWord, page_width: float, column_gap_ratio: float) -> bool:
  row_min = min(w.bbox[0] for w in row)
  row_max = max(w.bbox[2] for w in row)
  gap = max(0.0, max(row_min, word.bbox[0]) - min(row_max, word.bbox[2]))
  return gap <= max(40.0, page_width * column_gap_ratio * 0.25)


def from_ocr_payload(payload: dict[str, Any], pages: list[int] | None = None) -> ObservationBundle:
  words: list[ObservedWord] = []
  lines: list[ObservedLine] = []
  geometry: dict[int, dict[str, Any]] = {}
  word_index = 0
  for page in payload.get("pages") or []:
    page_number = int(page.get("page") or 0)
    if pages and page_number not in pages:
      continue
    width = float(page.get("width") or 0)
    height = float(page.get("height") or 0)
    pdf_width = page.get("pdfWidth")
    pdf_height = page.get("pdfHeight")
    geometry[page_number] = {
      "imageWidth": width, "imageHeight": height,
      "pdfWidth": pdf_width, "pdfHeight": pdf_height,
      "scaleX": (width / pdf_width) if pdf_width else 1.0,
      "scaleY": (height / pdf_height) if pdf_height else 1.0,
    }
    page_word_start = word_index
    for word in page.get("words") or []:
      wb = [float(v) for v in word.get("bbox") or (0, 0, 0, 0)]
      words.append(ObservedWord(page=page_number, text=str(word.get("text") or ""), bbox=(wb[0], wb[1], wb[2], wb[3]), word_index=word_index, source="ocr_cache"))
      word_index += 1
    for line in page.get("lines") or []:
      bbox = [float(v) for v in line.get("bbox") or (0, 0, 0, 0)]
      indexes: list[int] = []
      if line.get("wordIndexes") is not None:
        indexes = [page_word_start + int(index) for index in line.get("wordIndexes") or []]
      else:
        for word in line.get("words") or []:
          wb = [float(v) for v in word.get("bbox") or (0, 0, 0, 0)]
          words.append(ObservedWord(page=page_number, text=str(word.get("text") or ""), bbox=(wb[0], wb[1], wb[2], wb[3]), word_index=word_index, source="ocr_cache"))
          indexes.append(word_index)
          word_index += 1
      lines.append(ObservedLine(
        page=page_number, text=str(line.get("text") or ""), bbox=(bbox[0], bbox[1], bbox[2], bbox[3]),
        word_indexes=indexes, source="ocr_cache",
      ))
  lines.sort(key=lambda line: (line.page, line.bbox[1], line.bbox[0]))
  for index, line in enumerate(lines):
    line.line_index = index
  return ObservationBundle(words=words, lines=lines, visual_components=[], page_geometry=geometry, source="ocr_cache")


def from_native_pdf(pdf_path: str | Path, pages: list[int], boundary: dict[str, Any] | None = None) -> ObservationBundle:
  import pdfplumber

  words: list[ObservedWord] = []
  visual: list[ObservedVisualComponent] = []
  geometry: dict[int, dict[str, Any]] = {}
  word_index = 0
  with pdfplumber.open(str(pdf_path)) as pdf:
    for page_number in pages:
      if page_number < 1 or page_number > len(pdf.pages):
        continue
      page = pdf.pages[page_number - 1]
      geometry[page_number] = {
        "imageWidth": None, "imageHeight": None,
        "pdfWidth": float(page.width), "pdfHeight": float(page.height),
        "scaleX": 1.0, "scaleY": 1.0,
      }
      for word in page.extract_words(keep_blank_chars=False):
        words.append(ObservedWord(
          page=page_number, text=str(word.get("text") or ""),
          bbox=(float(word["x0"]), float(word["top"]), float(word["x1"]), float(word["bottom"])),
          word_index=word_index, source="native_pdf",
        ))
        word_index += 1
      for image in page.images:
        bbox = (float(image["x0"]), float(image["top"]), float(image["x1"]), float(image["bottom"]))
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        visual.append(ObservedVisualComponent(page=page_number, bbox=bbox, area=width * height, width=width, height=height, fill=1.0, source="native_image"))
      for rect in page.rects:
        bbox = (float(rect["x0"]), float(rect["top"]), float(rect["x1"]), float(rect["bottom"]))
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        if width < 25 or height < 25 or width > page.width * 0.9 or height > page.height * 0.9:
          continue
        visual.append(ObservedVisualComponent(page=page_number, bbox=bbox, area=width * height, width=width, height=height, fill=0.3, source="native_rect"))
  lines = group_words_into_lines(words, page_width=max((g["pdfWidth"] or 0) for g in geometry.values()) if geometry else 600.0)
  return ObservationBundle(words=words, lines=lines, visual_components=visual, page_geometry=geometry, source="native_pdf")
