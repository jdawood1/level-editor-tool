from editor.models import Level, LevelObject
import pytest


def test_object_bounds():
    lvl = Level(name="t", width=5, height=5, objects=[])
    lvl.objects.append(LevelObject(type="wall", x=1, y=1))
    Level(**lvl.model_dump())  # should not raise
    lvl.objects.append(LevelObject(type="wall", x=10, y=1))
    with pytest.raises(Exception):
        Level(**lvl.model_dump())
