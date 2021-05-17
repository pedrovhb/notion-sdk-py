import abc
from collections import UserDict, UserList
from typing import Any, Dict, Iterator, List, Optional, Union

from notion_client import HttpClient
from notion_client.defaults import (
    DEFAULT_BASE_URL,
    DEFAULT_NOTION_VERSION,
    DEFAULT_PAGE_SIZE,
    DEFAULT_USER_AGENT,
)
from notion_client.models import Item


class _BaseNotionClient(abc.ABC):

    pass


class Page:
    pass


class PagesManager:
    def __init__(self):
        self._pages = None
        self._has_next = None
        self._cursor = None

    def __index__(self):
        pass

    def __iter__(self) -> Iterator[Page]:
        if self._pages is None:
            print(":o")
            yield self._pages
        pass

    @property
    def count(self) -> int:
        return 42


class Database:
    def __init__(self):
        self._name = "Larissa"
        self._pages_manager = PagesManager()

    @property
    def name(self) -> str:
        return self._name

    @property
    def pages(self) -> PagesManager:
        return self._pages_manager


class _Paginator:
    def __init__(self):
        self.next_cursor: Optional[str] = None
        self.has_more: Optional[bool] = None

    def update_from(self, results: dict) -> None:
        self.next_cursor = results["next_cursor"]
        self.has_more = results["has_more"]


class _ItemCacheManager:
    pass


class Items(UserDict):
    def __init__(self, items_dict: Optional[Dict[str, Item]] = None):
        super().__init__(items_dict)

        if self.data:
            self._update_items_parents()  # todo - consider adding callback to item which points to getting this function's parent from id

    def __getitem__(self, item: str) -> Item:
        return self.data[item]

    def __iter__(self) -> Iterator[Item]:
        for item in self.data.values():
            yield item

    def update(self, __m: Dict[str, Item], **kwargs: Any) -> None:
        super().update(__m, **kwargs)
        self._update_items_parents()

    def _update_items_parents(self):
        for item in self.data.values():
            if item.parent is None and item.parent_id in self.data:
                item.parent = self.data[item.parent_id]

    def update_from_search_results(self, search_results: dict):
        items_list = (Item(**i) for i in search_results["results"])
        items_dict = {item.id_: item for item in items_list}
        self.update(items_dict)


class NotionClient(_BaseNotionClient):
    def __init__(
        self,
        auth_token: str,
        user_agent: str = DEFAULT_USER_AGENT,
        base_url: str = DEFAULT_BASE_URL,
        notion_version: str = DEFAULT_NOTION_VERSION,
        page_size: int = DEFAULT_PAGE_SIZE,
    ):
        self.http_client = HttpClient(
            auth_token,
            user_agent,
            base_url,
            notion_version,
            page_size,
        )
        self._search_paginator = _Paginator()
        self._items: Optional[Items] = None

    @property
    def items(self):
        # todo - iterating could be lazy
        if self._items is None:
            self._items = Items()
            search_results = self.http_client.search()
            self._search_paginator.update_from(search_results)
            self._items.update_from_search_results(search_results)
            # todo - give the option to not download everything at once
            while self._search_paginator.has_more:
                search_results = self.http_client.search(
                    start_cursor=self._search_paginator.next_cursor
                )
                self._search_paginator.update_from(search_results)
                self._items.update_from_search_results(search_results)
        return self._items
