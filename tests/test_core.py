import json
from pathlib import Path

import pytest

from editor import core as core_mod
from editor import telemetry as telemetry_mod


def use_tmp_dirs(tmp_path, monkeypatch):
    """
    Redirect editor.core DATA_DIR/BUILD_DIR and telemetry.LOG into tmp_path.
    """
    data_dir = tmp_path / "data"
    build_dir = tmp_path / "build"
    data_dir.mkdir(parents=True, exist_ok=True)
    build_dir.mkdir(parents=True, exist_ok=True)

    # Point core to temp dirs
    monkeypatch.setattr(core_mod, "DATA_DIR", data_dir, raising=False)
    monkeypatch.setattr(core_mod, "BUILD_DIR", build_dir, raising=False)

    # Point telemetry to a temp CSV
    monkeypatch.setattr(telemetry_mod, "LOG", build_dir / "telemetry.csv", raising=False)

    return data_dir, build_dir


def test_flow(tmp_path, monkeypatch):
    use_tmp_dirs(tmp_path, monkeypatch)
    lp = core_mod.new_level("ci_demo", 10, 10)
    core_mod.add_object(lp, "coin", 2, 2)
    s = core_mod.stats(lp)
    assert s["objects"] == 1
    assert s["by_type"] == {"coin": 1}


def test_export_and_telemetry(tmp_path, monkeypatch):
    _, build_dir = use_tmp_dirs(tmp_path, monkeypatch)

    # Create level and add a couple objects
    lp = core_mod.new_level("demo", 8, 6)
    core_mod.add_object(lp, "coin", 1, 1)
    core_mod.add_object(lp, "enemy", 2, 3)

    # Export
    out = build_dir / "out.json"
    p = core_mod.export(lp, out)
    assert p == out and p.exists()

    # Exported JSON is valid and matches Level schema fields
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["name"] == "demo"
    assert data["width"] == 8 and data["height"] == 6
    assert len(data["objects"]) == 2

    # Telemetry file should exist and contain at least new_level/add_object/export events
    tel = build_dir / "telemetry.csv"
    assert tel.exists()
    txt = tel.read_text(encoding="utf-8")
    assert "new_level" in txt
    assert txt.count("add_object") >= 2
    assert "export" in txt


@pytest.mark.parametrize("mode", ["index", "match_first", "match_all"])
def test_remove_object(tmp_path, monkeypatch, mode):
    """
    Covers `remove_object` if present. If the project doesn't include it yet,
    the test is skipped gracefully.
    """
    if not hasattr(core_mod, "remove_object"):
        pytest.skip("remove_object not implemented in editor.core")

    use_tmp_dirs(tmp_path, monkeypatch)

    lp = core_mod.new_level("r", 5, 5)
    core_mod.add_object(lp, "coin", 1, 1)
    core_mod.add_object(lp, "coin", 1, 1)
    core_mod.add_object(lp, "enemy", 2, 2)

    if mode == "index":
        removed = core_mod.remove_object(lp, index=1)
        assert removed == 1
    elif mode == "match_first":
        removed = core_mod.remove_object(lp, type="coin", x=1, y=1)
        assert removed == 1
    else:  # "match_all"
        removed = core_mod.remove_object(lp, type="coin", x=1, y=1, remove_all=True)
        assert removed == 2

    # Verify persisted file reflects removals
    data = json.loads(Path(lp).read_text(encoding="utf-8"))
    if mode == "index":
        assert len(data["objects"]) == 2
    elif mode == "match_first":
        # one coin removed; two objects remain
        assert len(data["objects"]) == 2
    else:
        # both coins removed; only enemy left
        assert len(data["objects"]) == 1
        assert data["objects"][0]["type"] == "enemy"
