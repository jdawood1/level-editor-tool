from pydantic import BaseModel, Field, field_validator
from typing import List, Literal

ObjectType = Literal["wall", "spawn", "enemy", "coin", "door"]


class LevelObject(BaseModel):
    type: ObjectType
    x: int = Field(ge=0)
    y: int = Field(ge=0)
    meta: dict = {}


class Level(BaseModel):
    name: str
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    # Use default_factory to avoid a shared mutable default list
    objects: List[LevelObject] = Field(default_factory=list)

    @field_validator("objects")
    @classmethod
    def within_bounds(cls, objs, info):
        """
        Pydantic v2: sibling fields are in info.data (ValidationInfo), not a dict.
        """
        w = int(info.data.get("width", 0) or 0)
        h = int(info.data.get("height", 0) or 0)
        for o in objs:
            if o.x >= w or o.y >= h:
                raise ValueError(f"Object out of bounds: ({o.x},{o.y}) >= ({w},{h})")
        return objs
