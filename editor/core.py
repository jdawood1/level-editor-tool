import json
import time
from pathlib import Path
from .models import Level, LevelObject
from .telemetry import log_event

from typing import Optional
from .models import ObjectType

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

def remove_object(
        level_path: Path,
        *,
        index: Optional[int] = None,
        type: Optional[ObjectType] = None,
        x: Optional[int] = None,
        y: Optional[int] = None,
        remove_all: bool = False,
) -> int:
    """
    Remove by either:
      A) list index (exactly one object), OR
      B) match (type, x, y); removes first match by default, or all with remove_all=True.
    Returns the number of removed objects.
    """
    t0 = time.time()
    data = json.loads(Path(level_path).read_text())
    level = Level(**data)

    if index is not None:
        if index < 0 or index >= len(level.objects):
            raise IndexError(f"index {index} out of range (0..{len(level.objects)-1})")
        del level.objects[index]
        # validate + persist
        Path(level_path).write_text(Level(**level.model_dump()).model_dump_json(indent=2))
        log_event("remove_object", time.time() - t0, {"level": Path(level_path).name, "index": index})
        return 1

    # Must have full key for match-based removal
    if type is None or x is None or y is None:
        raise ValueError("Provide either --index OR the trio --type/--x/--y")

    removed = 0
    kept = []
    for obj in level.objects:
        is_match = (obj.type == type and obj.x == x and obj.y == y)
        if is_match and (remove_all or removed == 0):
            removed += 1
            if not remove_all:
                # keep the remaining tail and break
                kept.extend(level.objects[level.objects.index(obj) + 1 :])
                break
        else:
            kept.append(obj)

    if removed:
        level.objects = kept
        # validate + persist
        Path(level_path).write_text(Level(**level.model_dump()).model_dump_json(indent=2))

    log_event(
        "remove_object",
        time.time() - t0,
        {
            "level": Path(level_path).name,
            "mode": "index" if index is not None else "match",
            "type": type,
            "x": x,
            "y": y,
            "all": remove_all,
            "removed": removed,
        },
        )
    return removed
