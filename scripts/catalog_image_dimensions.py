"""Registra no catálogo as dimensões naturais das imagens já extraídas."""

import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "public" / "data" / "questions.json"
PUBLIC = ROOT / "public"


def add_dimensions(block: dict) -> int:
    if block.get("type") != "image":
        return 0
    dimensions = []
    for url in block.get("urls", []):
        path = PUBLIC / str(url).lstrip("/")
        if not path.exists():
            dimensions.append({"width": 0, "height": 0})
            continue
        with Image.open(path) as image:
            dimensions.append({"width": image.width, "height": image.height})
    block["dimensions"] = dimensions
    return len(dimensions)


def main() -> None:
    questions = json.loads(CATALOG.read_text(encoding="utf-8"))
    image_count = 0
    for question in questions:
        for block in question.get("contentBlocks") or []:
            image_count += add_dimensions(block)
        for alternative in question.get("alternativeBlocks") or []:
            for block in alternative:
                image_count += add_dimensions(block)
    CATALOG.write_text(json.dumps(questions, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"Dimensões registradas para {image_count} referências de imagem.")


if __name__ == "__main__":
    main()
