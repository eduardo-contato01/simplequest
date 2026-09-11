from __future__ import annotations

import argparse
import io
import json
import posixpath
import re
import unicodedata
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from xml.etree import ElementTree as ET

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "work" / "source_files"
CATALOG = ROOT / "public" / "data" / "questions.json"
MEDIA_DIR = ROOT / "public" / "question-media"
REPORT = ROOT / "work" / "analysis_output" / "media-extraction.json"

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
RP = "http://schemas.openxmlformats.org/package/2006/relationships"
V = "urn:schemas-microsoft-com:vml"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
NS = {"w": W, "a": A, "r": RP, "v": V, "m": M}
W_NAME = f"{{{W}}}name"
W_VAL = f"{{{W}}}val"
R_ID = f"{{{R}}}id"
R_EMBED = f"{{{R}}}embed"
M_VAL = f"{{{M}}}val"


def relationship_map(zf: zipfile.ZipFile) -> dict[str, str]:
    root = ET.fromstring(zf.read("word/_rels/document.xml.rels"))
    return {node.attrib["Id"]: node.attrib.get("Target", "") for node in root.findall("r:Relationship", NS)}


def question_segments(zf: zipfile.ZipFile) -> dict[str, list[ET.Element]]:
    root = ET.fromstring(zf.read("word/document.xml"))
    body = root.find("w:body", NS)
    if body is None:
        return {}
    children = list(body)
    boundaries: list[tuple[int, str, bool]] = []
    for index, child in enumerate(children):
        for bookmark in child.findall(".//w:bookmarkStart", NS):
            name = bookmark.attrib.get(W_NAME, "")
            is_question = bool(re.match(r"^[A-Za-z]+_\d{4}_\d+$", name))
            if is_question or name.startswith("_Toc") or name.startswith("Prova_"):
                boundaries.append((index, name, is_question))
    boundaries.sort(key=lambda item: item[0])
    segments: dict[str, list[ET.Element]] = {}
    for position, (start, name, is_question) in enumerate(boundaries):
        if not is_question:
            continue
        end = next((index for index, _, _ in boundaries[position + 1 :] if index > start), len(children))
        segments[name] = children[start:end]
    return segments


def image_relationship_ids(nodes: list[ET.Element]) -> list[str]:
    ids: list[str] = []
    for node in nodes:
        ids.extend(blip.attrib[R_EMBED] for blip in node.findall(".//a:blip", NS) if blip.attrib.get(R_EMBED))
        ids.extend(image.attrib[R_ID] for image in node.findall(".//v:imagedata", NS) if image.attrib.get(R_ID))
    return list(dict.fromkeys(ids))


def table_text(nodes: list[ET.Element]) -> str:
    tables: list[str] = []
    for node in nodes:
        table_nodes = [node] if node.tag == f"{{{W}}}tbl" else node.findall(".//w:tbl", NS)
        for table in table_nodes:
            rows = []
            for row in table.findall("w:tr", NS):
                cells = []
                for cell in row.findall("w:tc", NS):
                    value = " ".join("".join(text.text or "" for text in paragraph.findall(".//w:t", NS)).strip() for paragraph in cell.findall(".//w:p", NS)).strip()
                    cells.append(value.replace("|", "/"))
                if any(cells):
                    rows.append(" | ".join(cells))
            if rows:
                tables.append("\n".join(rows))
    return "\n\n".join(tables)


def math_children(node: ET.Element) -> list[ET.Element]:
    return [child for child in list(node) if not child.tag.endswith("Pr") and child.tag != f"{{{M}}}ctrlPr"]


def omml_to_latex(node: ET.Element) -> str:
    local = node.tag.rsplit("}", 1)[-1]
    if local == "t":
        value = node.text or ""
        replacements = {
            "−": "-", "×": r"\times ", "÷": r"\div ", "∈": r"\in ", "∉": r"\notin ",
            "≤": r"\leq ", "≥": r"\geq ", "≠": r"\neq ", "≈": r"\approx ", "±": r"\pm ",
            "∞": r"\infty ", "∅": r"\varnothing ", "∩": r"\cap ", "∪": r"\cup ",
            "∎": r"\blacksquare ", "⊄": r"\not\subset ", "☼": r"\circledast ", "♥": r"\heartsuit ",
            "□": r"\square ", "●": r"\bullet ",
            "%": r"\%", "#": r"\#", "&": r"\&", "_": r"\_",
            "{": r"\{", "}": r"\}",
        }
        for source, target in replacements.items():
            value = value.replace(source, target)
        return value
    if local == "f":
        numerator = node.find("m:num", NS)
        denominator = node.find("m:den", NS)
        return rf"\frac{{{omml_to_latex(numerator) if numerator is not None else ''}}}{{{omml_to_latex(denominator) if denominator is not None else ''}}}"
    if local in {"sSup", "sSub", "sSubSup"}:
        base = node.find("m:e", NS)
        subscript = node.find("m:sub", NS)
        superscript = node.find("m:sup", NS)
        result = "{" + (omml_to_latex(base) if base is not None else "") + "}"
        if subscript is not None:
            result += "_{" + omml_to_latex(subscript) + "}"
        if superscript is not None:
            result += "^{" + omml_to_latex(superscript) + "}"
        return result
    if local == "rad":
        degree = node.find("m:deg", NS)
        expression = node.find("m:e", NS)
        degree_text = omml_to_latex(degree) if degree is not None else ""
        expression_text = omml_to_latex(expression) if expression is not None else ""
        return rf"\sqrt[{degree_text}]{{{expression_text}}}" if degree_text else rf"\sqrt{{{expression_text}}}"
    if local == "d":
        properties = node.find("m:dPr", NS)
        begin = "("
        end = ")"
        if properties is not None:
            begin_node = properties.find("m:begChr", NS)
            end_node = properties.find("m:endChr", NS)
            if begin_node is not None:
                begin = begin_node.attrib.get(M_VAL, begin)
            if end_node is not None:
                end = end_node.attrib.get(M_VAL, end)
        begin = {"{": r"\{", "}": r"\}", "": "."}.get(begin, begin)
        end = {"{": r"\{", "}": r"\}", "": "."}.get(end, end)
        expression = node.find("m:e", NS)
        return rf"\left{begin}{omml_to_latex(expression) if expression is not None else ''}\right{end}"
    if local == "acc":
        properties = node.find("m:accPr", NS)
        symbol = "^"
        if properties is not None:
            character = properties.find("m:chr", NS)
            if character is not None:
                symbol = character.attrib.get(M_VAL, symbol)
        expression = node.find("m:e", NS)
        command = {"^": "hat", "¯": "bar", "→": "vec", "˜": "tilde"}.get(symbol, "hat")
        return rf"\{command}{{{omml_to_latex(expression) if expression is not None else ''}}}"
    return "".join(omml_to_latex(child) for child in math_children(node))


def formulas_latex(nodes: list[ET.Element]) -> tuple[str, int]:
    formulas: list[str] = []
    total = 0
    for node in nodes:
        math_nodes = node.findall(".//m:oMath", NS)
        total += len(math_nodes)
        for math_node in math_nodes:
            latex = omml_to_latex(math_node).strip()
            if latex:
                formulas.append(latex)
    formulas = list(dict.fromkeys(formulas))
    if not formulas:
        return "", total
    if len(formulas) == 1:
        return formulas[0], total
    return r"\begin{gathered}" + r"\\[0.55em]".join(formulas) + r"\end{gathered}", total


def package_path(target: str) -> str:
    return posixpath.normpath(posixpath.join("word", target)).lstrip("/")


def optimize_image(data: bytes, extension: str) -> tuple[bytes | None, str | None, int, int]:
    extension = extension.lower()
    if extension not in {".png", ".jpg", ".jpeg", ".gif"}:
        return None, None, 0, 0
    with Image.open(io.BytesIO(data)) as source:
        image = ImageOps.exif_transpose(source)
        image.thumbnail((1800, 1800), Image.Resampling.LANCZOS)
        output = io.BytesIO()
        has_alpha = image.mode in {"RGBA", "LA"} or (image.mode == "P" and "transparency" in image.info)
        if has_alpha:
            image.save(output, "WEBP", lossless=True, method=6)
        else:
            if image.mode != "RGB":
                image = image.convert("RGB")
            image.save(output, "WEBP", quality=86, method=6)
        return output.getvalue(), ".webp", image.width, image.height


def media_slug(question: dict) -> str:
    school = unicodedata.normalize("NFKD", str(question["school"])).encode("ascii", "ignore").decode("ascii").lower()
    school = re.sub(r"[^a-z0-9]+", "-", school).strip("-")
    return f"{school}-{question['year']}-{question['number']}"


def save_media(data: bytes, extension: str, filename: str) -> tuple[str | None, int, int, int]:
    optimized, output_extension, width, height = optimize_image(data, extension)
    if optimized is None or output_extension is None:
        return None, 0, 0, 0
    destination = MEDIA_DIR / f"{filename}{output_extension}"
    if not destination.exists():
        destination.write_bytes(optimized)
    return f"/question-media/{destination.name}", len(optimized), width, height


def plain_text(node: ET.Element) -> str:
    return "".join(item.text or "" for item in node.findall(".//w:t", NS)).strip()


def split_content_nodes(nodes: list[ET.Element], option_count: int) -> tuple[list[ET.Element], list[list[ET.Element]]]:
    candidates = [(index, plain_text(node)) for index, node in enumerate(nodes) if plain_text(node)]
    if len(candidates) <= option_count:
        return nodes, []
    alternatives = candidates[-option_count:]
    starts = [index for index, _ in alternatives]
    groups = [nodes[start : starts[position + 1] if position + 1 < len(starts) else len(nodes)] for position, start in enumerate(starts)]
    return nodes[: starts[0]], groups


def ordered_raw_blocks(nodes: list[ET.Element]) -> list[dict]:
    blocks: list[dict] = []

    def append_text(value: str, join_previous: bool = False) -> None:
        value = value.strip()
        if not value:
            return
        if join_previous and blocks and blocks[-1]["type"] == "text":
            blocks[-1]["text"] += "\n" + value
        else:
            blocks.append({"type": "text", "text": value})

    def parse_paragraph(paragraph: ET.Element) -> list[dict]:
        result: list[dict] = []
        buffer: list[str] = []

        def flush() -> None:
            raw_value = "".join(buffer)
            buffer.clear()
            value = raw_value.strip()
            if value:
                if raw_value[:1].isspace():
                    value = " " + value
                if raw_value[-1:].isspace():
                    value += " "
                result.append({"type": "text", "text": value})

        def walk(element: ET.Element) -> None:
            if element.tag in {f"{{{M}}}oMath", f"{{{M}}}oMathPara"}:
                flush()
                latex = omml_to_latex(element).strip()
                if latex:
                    result.append({"type": "formula", "latex": latex})
                return
            if element.tag in {f"{{{W}}}drawing", f"{{{W}}}pict"}:
                flush()
                relationship_ids = image_relationship_ids([element])
                if relationship_ids:
                    result.append({"type": "image-reference", "relationshipIds": relationship_ids})
                return
            if element.tag == f"{{{W}}}r":
                vertical_align = element.find("w:rPr/w:vertAlign", NS)
                script_type = vertical_align.attrib.get(W_VAL, "") if vertical_align is not None else ""
                if script_type in {"superscript", "subscript"}:
                    script_text = "".join(item.text or "" for item in element.findall(".//w:t", NS)).strip()
                    if script_text:
                        current_text = "".join(buffer)
                        base_match = re.search(r"([\w]+)$", current_text, re.UNICODE)
                        base = base_match.group(1) if base_match else ""
                        if base:
                            del buffer[:]
                            buffer.append(current_text[: -len(base)])
                        flush()
                        result.append({"type": "script", "base": base, "value": script_text, "position": script_type})
                        return
            if element.tag == f"{{{W}}}t":
                buffer.append(element.text or "")
                return
            if element.tag == f"{{{W}}}tab":
                buffer.append("\t")
                return
            if element.tag == f"{{{W}}}br":
                buffer.append("\n")
                return
            for child in list(element):
                walk(child)

        walk(paragraph)
        flush()
        has_text = any(block["type"] == "text" and block["text"].strip() for block in result)
        for block in result:
            if block["type"] == "formula":
                block["display"] = "inline" if has_text else "block"
        return result

    for node in nodes:
        if node.tag == f"{{{W}}}tbl":
            value = table_text([node])
            if value:
                blocks.append({"type": "table", "data": value})
            continue
        if node.tag != f"{{{W}}}p":
            continue
        paragraph = parse_paragraph(node)
        if len(paragraph) == 1 and paragraph[0]["type"] == "text":
            append_text(paragraph[0]["text"], join_previous=True)
        else:
            blocks.extend(paragraph)
    return blocks


def formatted_script_runs(nodes: list[ET.Element]) -> list[dict[str, str]]:
    scripts: list[dict[str, str]] = []
    for node in nodes:
        for run in node.findall(".//w:r", NS):
            vertical_align = run.find("w:rPr/w:vertAlign", NS)
            script_type = vertical_align.attrib.get(W_VAL, "") if vertical_align is not None else ""
            if script_type in {"superscript", "subscript"}:
                value = "".join(item.text or "" for item in run.findall(".//w:t", NS)).strip()
                if value:
                    scripts.append({"type": script_type, "value": value})
    return scripts


SUPERSCRIPT_CHARS = str.maketrans("0123456789+-=()", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾")
SUBSCRIPT_CHARS = str.maketrans("0123456789+-=()", "₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎")


def blocks_plain_text(blocks: list[dict]) -> str:
    pieces: list[str] = []
    for block in blocks:
        if block["type"] == "text":
            pieces.append(block["text"])
        elif block["type"] == "script":
            value = block["value"]
            if block["position"] == "superscript":
                if value == "o":
                    value = "º"
                elif value == "a":
                    value = "ª"
                elif value == "os":
                    value = "ºs"
                elif value == "as":
                    value = "ªs"
                else:
                    value = value.translate(SUPERSCRIPT_CHARS)
            else:
                value = value.translate(SUBSCRIPT_CHARS)
            pieces.append(block["base"] + value)
    return "".join(pieces).strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Mapeia imagens e tabelas dos DOCX para as questões do SimpleQuest.")
    parser.add_argument("--extract", action="store_true", help="Extrai arquivos e atualiza o catálogo. Sem esta opção, executa apenas a auditoria.")
    parser.add_argument("--formulas-only", action="store_true", help="Atualiza somente as fórmulas, preservando mídias e tabelas já extraídas.")
    args = parser.parse_args()

    questions = json.loads(CATALOG.read_text(encoding="utf-8"))
    by_document: dict[str, list[dict]] = defaultdict(list)
    for question in questions:
        if question.get("sourceDocument") and question.get("sourceBookmark"):
            by_document[question["sourceDocument"]].append(question)

    if args.extract:
        MEDIA_DIR.mkdir(parents=True, exist_ok=True)

    report = {
        "documents": {},
        "questions_with_mapped_images": 0,
        "mapped_image_references": 0,
        "questions_with_tables": 0,
        "questions_with_formulas": 0,
        "formula_nodes": 0,
        "formula_nodes_without_output": 0,
        "unsupported_references": 0,
        "unsupported_extensions": Counter(),
        "unsupported_items": [],
        "formatted_scripts": [],
        "output_bytes": 0,
    }

    for document_name, document_questions in sorted(by_document.items()):
        path = SOURCE / document_name
        if not path.exists():
            report["documents"][document_name] = {"error": "arquivo não encontrado"}
            continue
        document_stats = Counter()
        with zipfile.ZipFile(path) as zf:
            relations = relationship_map(zf)
            segments = question_segments(zf)
            for question in document_questions:
                nodes = segments.get(question["sourceBookmark"])
                if not nodes:
                    document_stats["missing_segments"] += 1
                    continue
                option_count = 2 if question.get("answerType") == "CE" else 4 if question.get("answerType") == "ABCD" else 5
                scripts = formatted_script_runs(nodes)
                if scripts:
                    report["formatted_scripts"].append({"questionId": question["id"], "document": document_name, "bookmark": question["sourceBookmark"], "runs": scripts})
                    if args.extract:
                        question["hasMath"] = True
                        question["status"] = "review"
                content_nodes, alternative_node_groups = split_content_nodes(nodes, option_count)
                urls: list[str] = []
                supported_media_paths: list[str] = []
                for relationship_id in image_relationship_ids(nodes):
                    target = relations.get(relationship_id, "")
                    media_path = package_path(target)
                    if target and media_path in zf.namelist() and Path(media_path).suffix.lower() in {".png", ".jpg", ".jpeg", ".gif"}:
                        supported_media_paths.append(media_path)
                supported_media_paths = list(dict.fromkeys(supported_media_paths))
                base_media_name = media_slug(question)
                media_filenames = {
                    media_path: base_media_name if len(supported_media_paths) == 1 else f"{base_media_name}_{index}"
                    for index, media_path in enumerate(supported_media_paths, start=1)
                }

                def convert_blocks(raw_blocks: list[dict], prefix: str) -> list[dict]:
                    converted: list[dict] = []
                    for raw_block in raw_blocks:
                        if raw_block["type"] != "image-reference":
                            converted.append(raw_block)
                            continue
                        block_media: dict[str, dict[str, int]] = {}
                        relationship_ids = [] if args.formulas_only else raw_block["relationshipIds"]
                        for relationship_id in relationship_ids:
                            target = relations.get(relationship_id, "")
                            media_path = package_path(target)
                            if not target or media_path not in zf.namelist():
                                document_stats["missing_media"] += 1
                                continue
                            extension = Path(media_path).suffix.lower()
                            document_stats[f"reference{extension}"] += 1
                            if extension not in {".png", ".jpg", ".jpeg", ".gif"}:
                                report["unsupported_references"] += 1
                                report["unsupported_extensions"][extension or "sem extensão"] += 1
                                item = {
                                    "questionId": question["id"], "document": document_name,
                                    "bookmark": question["sourceBookmark"], "format": extension or "desconhecido",
                                    "source": media_path, "position": prefix,
                                }
                                report["unsupported_items"].append(item)
                                converted.append({"type": "pending-media", "label": "Imagem pendente de conversão", "format": item["format"]})
                                continue
                            if args.extract:
                                url, output_size, width, height = save_media(zf.read(media_path), extension, media_filenames[media_path])
                                if url:
                                    block_media[url] = {"width": width, "height": height}
                                    urls.append(url)
                                    report["output_bytes"] += output_size
                            else:
                                block_media[media_path] = {"width": 0, "height": 0}
                                urls.append(media_path)
                        if block_media:
                            converted.append({"type": "image", "urls": list(block_media), "dimensions": list(block_media.values())})
                    for index, block in enumerate(converted):
                        block["id"] = f"{prefix}{index + 1}"
                    return converted

                content_blocks = convert_blocks(ordered_raw_blocks(content_nodes), "b")
                alternative_blocks = [convert_blocks(ordered_raw_blocks(group), f"a{index + 1}-") for index, group in enumerate(alternative_node_groups)]
                table = table_text(nodes)
                formula, formula_nodes = formulas_latex(nodes)
                report["formula_nodes"] += formula_nodes
                if urls:
                    report["questions_with_mapped_images"] += 1
                    report["mapped_image_references"] += len(urls)
                    document_stats["questions_with_images"] += 1
                    if args.extract:
                        question["imageUrls"] = list(dict.fromkeys(urls))
                        question["hasMedia"] = True
                        question["status"] = "review"
                if any(block["type"] == "pending-media" for block in content_blocks + [item for group in alternative_blocks for item in group]):
                    question["hasMedia"] = True
                    question["status"] = "review"
                if table and not args.formulas_only:
                    report["questions_with_tables"] += 1
                    document_stats["questions_with_tables"] += 1
                    if args.extract:
                        question["tableData"] = table
                        question["hasTable"] = True
                        question["status"] = "review"
                if formula:
                    report["questions_with_formulas"] += 1
                    document_stats["questions_with_formulas"] += 1
                    if args.extract:
                        question["formula"] = formula
                        question["hasMath"] = True
                        question["status"] = "review"
                elif formula_nodes:
                    report["formula_nodes_without_output"] += formula_nodes
                if args.extract and not args.formulas_only:
                    question["contentBlocks"] = content_blocks
                    question["alternativeBlocks"] = alternative_blocks
                    question["stem"] = blocks_plain_text(content_blocks)
                    if alternative_blocks:
                        question["alternatives"] = [blocks_plain_text(group) for group in alternative_blocks]
        report["documents"][document_name] = dict(document_stats)

    report["unsupported_extensions"] = dict(report["unsupported_extensions"])
    report["output_megabytes"] = round(report.pop("output_bytes") / 1024 / 1024, 2)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.extract:
        CATALOG.write_text(json.dumps(questions, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
