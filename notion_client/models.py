from __future__ import annotations

from time import time
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, root_validator, validator

CACHE_TTL = 60


# class CacheableMixin:
#     def __init__(self):
#         self.cache_updated_at = time()
#         self.cache_dirty = False
#
#     @property
#     def cache_stale(self) -> bool:
#         return self.cache_dirty
#
#     def __getattribute__(self, name):
#         if name in ("id", "id_"):
#             return object.__getattribute__(self, name)
#         if self.cache_stale:
#             print(
#                 "woops, this cache seems stale. "
#                 "i should probably do something about it."
#             )
#         return object.__getattribute__(self, name)


class Item(BaseModel):
    id_: str = Field(..., alias="id")
    object_: Literal["database", "page"] = Field(..., alias="object")  #
    created_time: str
    last_edited_time: str
    properties: Dict[str, "Property"]
    title: str = ""
    title_rich: Optional[List["RichText"]] = []
    name: str = ""
    name_rich: Optional[List["RichText"]] = []
    parent: Optional["Item"] = None
    parent_id: Optional[str] = None
    archived: Optional[bool] = None

    def __init__(self, **data: Any):
        print("a")
        self._set_parent(data)
        self._set_title(data)
        self._set_name(data)
        super().__init__(**data)

    def _set_parent(self, data):
        parent = data.get("parent", {})
        parent_id = parent.get("database_id") or parent.get("page_id")
        data["parent_id"] = parent_id
        data["parent"] = None

    def _set_title(self, data):
        rich_title = data.get("title", [])
        title = "".join(t["plain_text"] for t in rich_title)
        data["title_rich"] = rich_title
        data["title"] = title

    def _set_name(self, data):
        rich_name = data.get("properties", {}).get("Name", {}).get("title", [])
        name = "".join(t["plain_text"] for t in rich_name)
        data["name_rich"] = rich_name or []
        data["name"] = name


class Property(BaseModel):
    id_: str = Field(..., alias="id")
    type_: str = Field(..., alias="type")
    # todo - add specific fields of properties (richtext is one i think)


class RichText(BaseModel):
    type_: str = Field(..., alias="type")  # Literal["text"]
    text: "Text"
    annotations: "Annotation"
    plain_text: str
    href: Optional[str] = None


class Text(BaseModel):
    content: str
    link: str = None

    @validator("link", pre=True)
    def clean_link(cls, value):
        """Return the URL for the link property, as it's otherwise nested."""
        if value:
            return value["url"]


class Annotation(BaseModel):
    bold: bool
    italic: bool
    strikethrough: bool
    underline: bool
    code: bool
    color: str  # Literal["default"]


for model in [
    Item,
    Property,
    RichText,
    Text,
    Annotation,
]:
    model.update_forward_refs()
