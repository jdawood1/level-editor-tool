import json
import time
from pathlib import Path
from .models import Level, LevelObject
from .telemetry import log_event

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
BUILD_DIR = Path(__file__).resolve().parent.parent / "build"
DATA_DIR.mkdir(exist_ok=True)
BUILD_DIR.mkdir(exist_ok=True)


def new_level(name: str, width: int, height: int) -> Path:
    t0 = time.time()
    level = Level(name=name, width=width, height=height, objects=[])
    out = DATA_DIR / f"{name}.json"
    out.write_text(level.model_dump_json(indent=2))
    log_event("new_level", time.time() - t0, {"name": name, "w": width, "h": height})
    return out


def add_object(level_path: Path, type: str, x: int, y: int) -> None:
    t0 = time.time()
    data = json.loads(Path(level_path).read_text())
    level = Level(**data)
    level.objects.append(LevelObject(type=type, x=x, y=y))
    # validate on dump
    Level(**level.model_dump())
    Path(level_path).write_text(Level(**level.model_dump()).model_dump_json(indent=2))
    log_event(
        "add_object",
        time.time() - t0,
        {"level": Path(level_path).name, "type": type, "x": x, "y": y},
    )


def export(level_path: Path, out_path: Path) -> Path:
    t0 = time.time()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    data = json.loads(Path(level_path).read_text())
    level = Level(**data)
    out_path.write_text(level.model_dump_json(indent=2))
    log_event(
        "export",
        time.time() - t0,
        {"level": Path(level_path).name, "out": str(out_path)},
    )
    return out_path


def stats(level_path: Path) -> dict:
    data = json.loads(Path(level_path).read_text())
    level = Level(**data)
    count_by_type = {}
    for o in level.objects:
        count_by_type[o.type] = count_by_type.get(o.type, 0) + 1
    return {
        "name": level.name,
        "width": level.width,
        "height": level.height,
        "objects": len(level.objects),
        "by_type": count_by_type,
    }
