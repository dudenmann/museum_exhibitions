"""JSON-хранилище с проверкой данных и атомарной заменой файла."""

import json
import os
import tempfile
from dataclasses import asdict
from datetime import date
from pathlib import Path

from models import Curator, Exhibition, Hall
from services import Museum


ROOT = Path(__file__).resolve().parent
DEFAULT_PATH = ROOT / "data" / "local.json"
DEMO_PATH = ROOT / "data" / "demo.json"


def load_museum(path=DEFAULT_PATH):
    path = Path(path)
    # Только первое открытие рабочего файла использует демонстрационные данные.
    source = DEMO_PATH if path == DEFAULT_PATH and not path.exists() else path
    try:
        data = json.loads(source.read_text(encoding="utf-8"))
        exhibitions = [
            Exhibition(
                **{
                    **item,
                    "start_date": date.fromisoformat(item["start_date"]),
                    "end_date": date.fromisoformat(item["end_date"]),
                }
            )
            for item in data["exhibitions"]
        ]
        return Museum(
            [Hall(**item) for item in data["halls"]],
            [Curator(**item) for item in data["curators"]],
            exhibitions,
        )
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError(f"Некорректные данные в {source}: {error}") from error


def save_museum(museum, path=DEFAULT_PATH):
    museum.validate()
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "halls": [asdict(item) for item in museum.halls],
        "curators": [asdict(item) for item in museum.curators],
        "exhibitions": [asdict(item) for item in museum.exhibitions],
    }
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, delete=False,
        ) as stream:
            temporary = Path(stream.name)
            json.dump(data, stream, ensure_ascii=False, indent=2, default=str)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
