from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pdfplumber
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "outputs" / "audit" / "ocr"
DEFAULT_TESSERACT = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")
DEFAULT_TESSDATA = ROOT / "tmp" / "tessdata"


@dataclass
class OcrPage:
  page: int
  width: int
  height: int
  words: list[dict[str, Any]]
  lines: list[dict[str, Any]]
  confidence: float | None
  chars: int


def slugify(value: str) -> str:
  value = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-").lower()
  return value[:120] or "pdf"


def render_pages(pdf_path: Path, output_dir: Path, dpi: int, first_page: int | None, last_page: int | None) -> list[Path]:
  output_dir.mkdir(parents=True, exist_ok=True)
  prefix = output_dir / "page"
  cmd = ["pdftoppm", "-r", str(dpi), "-png"]
  if first_page:
    cmd += ["-f", str(first_page)]
  if last_page:
    cmd += ["-l", str(last_page)]
  cmd += [str(pdf_path), str(prefix)]
  subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
  return sorted(output_dir.glob("page-*.png"))


def file_fingerprint(path: Path) -> dict[str, Any]:
  stat = path.stat()
  digest = hashlib.sha256()
  with path.open("rb") as handle:
    for chunk in iter(lambda: handle.read(1024 * 1024), b""):
      digest.update(chunk)
  return {
    "sha256": digest.hexdigest(),
    "sizeBytes": stat.st_size,
    "mtimeNs": stat.st_mtime_ns,
  }


def tesseract_version(tesseract: Path) -> str | None:
  try:
    proc = subprocess.run(
      [str(tesseract), "--version"],
      check=True,
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE,
      text=True,
      encoding="utf-8",
      errors="replace",
    )
  except Exception:
    return None
  first_line = proc.stdout.splitlines()[0].strip() if proc.stdout.splitlines() else ""
  return first_line or None


def pdf_page_sizes(pdf_path: Path) -> dict[int, dict[str, float]]:
  with pdfplumber.open(str(pdf_path)) as pdf:
    return {
      index + 1: {"width": float(page.width), "height": float(page.height)}
      for index, page in enumerate(pdf.pages)
    }


def group_words_into_lines(words: list[dict[str, Any]]) -> list[dict[str, Any]]:
  groups: list[dict[str, Any]] = []
  for word in sorted(words, key=lambda item: (item["bbox"][1], item["bbox"][0])):
    x0, y0, x1, y1 = word["bbox"]
    matched = None
    for group in groups:
      gy0, gy1 = group["_y0"], group["_y1"]
      if abs(((gy0 + gy1) / 2) - ((y0 + y1) / 2)) <= max(8, (gy1 - gy0) * 0.8):
        matched = group
        break
    if matched is None:
      matched = {"words": [], "_y0": y0, "_y1": y1}
      groups.append(matched)
    matched["words"].append(word)
    matched["_y0"] = min(matched["_y0"], y0)
    matched["_y1"] = max(matched["_y1"], y1)
  lines = []
  for index, group in enumerate(sorted(groups, key=lambda item: item["_y0"]), start=1):
    group_words = sorted(group["words"], key=lambda item: item["bbox"][0])
    text = " ".join(word["text"] for word in group_words).strip()
    if not text:
      continue
    xs0 = [word["bbox"][0] for word in group_words]
    ys0 = [word["bbox"][1] for word in group_words]
    xs1 = [word["bbox"][2] for word in group_words]
    ys1 = [word["bbox"][3] for word in group_words]
    confidences = [word["confidence"] for word in group_words if word.get("confidence") is not None and word["confidence"] >= 0]
    lines.append({
      "line": index,
      "text": text,
      "bbox": [min(xs0), min(ys0), max(xs1), max(ys1)],
      "confidence": round(sum(confidences) / len(confidences), 4) if confidences else None,
      "wordIndexes": [word["index"] for word in group_words],
    })
  return lines


def tesseract_page(image_path: Path, page_number: int, tesseract: Path, tessdata: Path, lang: str, psm: int) -> OcrPage:
  with Image.open(image_path) as image:
    width, height = image.size
  cmd = [
    str(tesseract),
    str(image_path),
    "stdout",
    "--tessdata-dir",
    str(tessdata),
    "-l",
    lang,
    "--psm",
    str(psm),
    "-c",
    "tessedit_create_tsv=1",
  ]
  proc = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
  words: list[dict[str, Any]] = []
  rows = proc.stdout.splitlines()
  if rows:
    headers = rows[0].split("\t")
    for row in rows[1:]:
      values = row.split("\t")
      if len(values) != len(headers):
        continue
      item = dict(zip(headers, values))
      text = item.get("text", "").strip()
      if not text:
        continue
      try:
        conf = float(item.get("conf", "-1"))
        left = int(float(item.get("left", "0")))
        top = int(float(item.get("top", "0")))
        w = int(float(item.get("width", "0")))
        h = int(float(item.get("height", "0")))
      except ValueError:
        continue
      words.append({
        "index": len(words),
        "text": text,
        "bbox": [left, top, left + w, top + h],
        "confidence": round(conf / 100, 4) if conf >= 0 else None,
        "source": "tesseract",
      })
  lines = group_words_into_lines(words)
  confidences = [word["confidence"] for word in words if word.get("confidence") is not None]
  return OcrPage(
    page=page_number,
    width=width,
    height=height,
    words=words,
    lines=lines,
    confidence=round(sum(confidences) / len(confidences), 4) if confidences else None,
    chars=sum(len(word["text"]) for word in words),
  )


def rapidocr_page(image_path: Path, page_number: int) -> OcrPage:
  from rapidocr_onnxruntime import RapidOCR

  engine = rapidocr_page.engine
  if engine is None:
    engine = RapidOCR()
    rapidocr_page.engine = engine
  with Image.open(image_path) as image:
    width, height = image.size
  result, _ = engine(str(image_path))
  words: list[dict[str, Any]] = []
  for item in result or []:
    box, text, score = item
    xs = [int(point[0]) for point in box]
    ys = [int(point[1]) for point in box]
    if not str(text).strip():
      continue
    words.append({
      "index": len(words),
      "text": str(text).strip(),
      "bbox": [min(xs), min(ys), max(xs), max(ys)],
      "confidence": round(float(score), 4),
      "source": "rapidocr",
    })
  lines = group_words_into_lines(words)
  confidences = [word["confidence"] for word in words if word.get("confidence") is not None]
  return OcrPage(
    page=page_number,
    width=width,
    height=height,
    words=words,
    lines=lines,
    confidence=round(sum(confidences) / len(confidences), 4) if confidences else None,
    chars=sum(len(word["text"]) for word in words),
  )


rapidocr_page.engine = None


def marker_count(pages: list[OcrPage]) -> dict[str, int]:
  counts = {"questao": 0, "numeric": 0}
  for page in pages:
    for line in page.lines:
      text = line["text"]
      normalized = re.sub(r"\s+", " ", text.upper())
      compact = re.sub(r"[^A-Z0-9]+", "", normalized)
      if re.search(r"QUEST[ÃA]O\s*\d{1,3}", normalized) or re.search(r"QUESTAO\d{1,3}", compact) or re.search(r"Q\s*UEST[ÃA]O\s*\d{1,3}", normalized):
        counts["questao"] += 1
      elif re.match(r"^\s*0*\d{1,3}\s*[.)-]\s+\S+", text):
        counts["numeric"] += 1
  return counts


def run_ocr(args: argparse.Namespace) -> dict[str, Any]:
  pdf_path = Path(args.pdf)
  out_root = Path(args.output_dir) / slugify(pdf_path.stem) / args.engine
  render_dir = out_root / "rendered"
  if args.clean and out_root.exists():
    shutil.rmtree(out_root)
  out_root.mkdir(parents=True, exist_ok=True)
  start = time.perf_counter()
  images = render_pages(pdf_path, render_dir, args.dpi, args.first_page, args.last_page)
  source_page_sizes = pdf_page_sizes(pdf_path)
  pages: list[OcrPage] = []
  first_page = args.first_page or 1
  for offset, image in enumerate(images):
    page_number = first_page + offset
    if args.engine == "tesseract":
      pages.append(tesseract_page(image, page_number, Path(args.tesseract), Path(args.tessdata), args.lang, args.psm))
    elif args.engine == "rapidocr":
      pages.append(rapidocr_page(image, page_number))
    else:
      raise ValueError(f"Unsupported engine: {args.engine}")
  elapsed = time.perf_counter() - start
  payload = {
    "pdf": str(pdf_path),
    "pdfFingerprint": file_fingerprint(pdf_path),
    "engine": args.engine,
    "engineVersion": tesseract_version(Path(args.tesseract)) if args.engine == "tesseract" else None,
    "dpi": args.dpi,
    "psm": args.psm if args.engine == "tesseract" else None,
    "lang": args.lang if args.engine == "tesseract" else None,
    "firstPage": args.first_page,
    "lastPage": args.last_page,
    "elapsedSeconds": round(elapsed, 3),
    "pagesProcessed": len(pages),
    "averageConfidence": round(sum(page.confidence or 0 for page in pages) / len(pages), 4) if pages else None,
    "totalChars": sum(page.chars for page in pages),
    "markerCounts": marker_count(pages),
    "pages": [
      {
        "page": page.page,
        "width": page.width,
        "height": page.height,
        "pdfWidth": source_page_sizes.get(page.page, {}).get("width"),
        "pdfHeight": source_page_sizes.get(page.page, {}).get("height"),
        "confidence": page.confidence,
        "chars": page.chars,
        "words": page.words,
        "lines": page.lines,
      }
      for page in pages
    ],
  }
  json_path = out_root / "ocr.json"
  json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
  return {"json": str(json_path), **{key: payload[key] for key in ["engine", "elapsedSeconds", "pagesProcessed", "averageConfidence", "totalChars", "markerCounts"]}}


def main() -> None:
  parser = argparse.ArgumentParser(description="Camada OCR experimental para PDFs rasterizados do SimpleQuest.")
  parser.add_argument("--pdf", required=True)
  parser.add_argument("--engine", choices=["tesseract", "rapidocr"], required=True)
  parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
  parser.add_argument("--dpi", type=int, default=220)
  parser.add_argument("--first-page", type=int)
  parser.add_argument("--last-page", type=int)
  parser.add_argument("--tesseract", default=str(DEFAULT_TESSERACT))
  parser.add_argument("--tessdata", default=str(DEFAULT_TESSDATA))
  parser.add_argument("--lang", default="por+eng")
  parser.add_argument("--psm", type=int, default=6)
  parser.add_argument("--clean", action="store_true")
  args = parser.parse_args()
  print(json.dumps(run_ocr(args), ensure_ascii=False, indent=2))


if __name__ == "__main__":
  main()
