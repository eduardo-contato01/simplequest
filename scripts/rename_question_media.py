from __future__ import annotations

import json
import re
import shutil
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "public" / "data" / "questions.json"
MEDIA_DIR = ROOT / "public" / "question-media"
ORPHAN_DIR = ROOT / "work" / "orphaned-question-media"


def slug(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")


def image_blocks(question: dict) -> list[dict]:
    blocks = list(question.get("contentBlocks") or [])
    blocks.extend(block for group in question.get("alternativeBlocks") or [] for block in group)
    return [block for block in blocks if block.get("type") == "image"]


def main() -> None:
    questions = json.loads(CATALOG.read_text(encoding="utf-8"))
    plan: list[tuple[Path, Path]] = []
    referenced_before: set[str] = set()
    referenced_after: set[str] = set()

    for question in questions:
        blocks = image_blocks(question)
        if not blocks:
            continue
        base = f"{slug(str(question['school']))}-{question['year']}-{question['number']}"

        groups: list[tuple[list[dict], str]] = []
        main_blocks = [block for block in question.get("contentBlocks") or [] if block.get("type") == "image"]
        groups.append((main_blocks, "main"))
        for alternative_index, alternative in enumerate(question.get("alternativeBlocks") or []):
            alternative_blocks = [block for block in alternative if block.get("type") == "image"]
            groups.append((alternative_blocks, chr(ord("a") + alternative_index)))

        for grouped_blocks, location in groups:
            ordered_urls = list(dict.fromkeys(url for block in grouped_blocks for url in block.get("urls", [])))
            replacements: dict[str, str] = {}
            for index, old_url in enumerate(ordered_urls, start=1):
                if location == "main":
                    suffix = "" if len(ordered_urls) == 1 else f"_{index}"
                else:
                    suffix = f"_{location}" if len(ordered_urls) == 1 else f"_{location}_{index}"
                new_url = f"/question-media/{base}{suffix}.webp"
                old_path = ROOT / "public" / old_url.lstrip("/")
                new_path = ROOT / "public" / new_url.lstrip("/")
                if not old_path.exists():
                    raise FileNotFoundError(f"Imagem referenciada não encontrada: {old_path}")
                if new_path.exists() and new_path.resolve() != old_path.resolve():
                    raise FileExistsError(f"Destino já existe: {new_path}")
                replacements[old_url] = new_url
                referenced_before.add(old_url)
                referenced_after.add(new_url)
                if old_path.resolve() != new_path.resolve():
                    plan.append((old_path, new_path))
            for block in grouped_blocks:
                block["urls"] = [replacements[url] for url in block.get("urls", [])]

        question["imageUrls"] = list(dict.fromkeys(url for block in blocks for url in block.get("urls", [])))

    destinations = [destination for _, destination in plan]
    if len(destinations) != len(set(destinations)):
        raise RuntimeError("A migração produziu nomes de destino duplicados.")

    for source, destination in plan:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    missing = [path for path in destinations if not path.exists()]
    if missing:
        raise RuntimeError(f"Falha ao criar {len(missing)} imagens renomeadas.")

    CATALOG.write_text(json.dumps(questions, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    for old_url in referenced_before:
        old_path = ROOT / "public" / old_url.lstrip("/")
        if old_url not in referenced_after and old_path.exists():
            old_path.unlink()

    current_references = {url for question in questions for block in image_blocks(question) for url in block.get("urls", [])}
    orphans = [path for path in MEDIA_DIR.glob("*.webp") if f"/question-media/{path.name}" not in current_references]
    if orphans:
        ORPHAN_DIR.mkdir(parents=True, exist_ok=True)
        for orphan in orphans:
            destination = ORPHAN_DIR / orphan.name
            if destination.exists():
                raise FileExistsError(f"Órfão já arquivado: {destination}")
            orphan.replace(destination)

    print(json.dumps({
        "questions": len(questions),
        "references": sum(len(block.get("urls", [])) for question in questions for block in image_blocks(question)),
        "public_files": len(list(MEDIA_DIR.glob("*.webp"))),
        "archived_orphans": len(orphans),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
