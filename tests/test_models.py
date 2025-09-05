import pytest
from editor.models import Level, LevelObject


def test_object_bounds():
    lvl = Level(name="t", width=5, height=5, objects=[])
    lvl.objects.append(LevelObject(type="wall", x=1, y=1))
    # Round-trip through validation should not raise
    Level(**lvl.model_dump())

    # Out-of-bounds should fail via the objects validator
    lvl.objects.append(LevelObject(type="wall", x=10, y=1))
    with pytest.raises(Exception):
        Level(**lvl.model_dump())


def test_negative_coordinates_disallowed():
    # LevelObject has ge=0 constraints on x,y
    with pytest.raises(Exception):
        LevelObject(type="coin", x=-1, y=0)
    with pytest.raises(Exception):
        LevelObject(type="coin", x=0, y=-1)


def test_width_height_positive():
    # width/height must be > 0
    with pytest.raises(Exception):
        Level(name="badw", width=0, height=5, objects=[])
    with pytest.raises(Exception):
        Level(name="badh", width=5, height=0, objects=[])


def test_roundtrip_dump_load():
    # Ensure model_dump is fully reconstructible
    lvl = Level(name="z", width=3, height=2, objects=[LevelObject(type="door", x=0, y=1)])
    dumped = lvl.model_dump()
    lvl2 = Level(**dumped)
    assert lvl2.name == "z"
    assert lvl2.width == 3 and lvl2.height == 2
    assert len(lvl2.objects) == 1 and lvl2.objects[0].type == "door"
