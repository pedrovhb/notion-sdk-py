from typing import TYPE_CHECKING, Optional, Sequence

import httpx

from .helpers import pick

if TYPE_CHECKING:
    from .client import Client


class Endpoint:
    def __init__(self, parent: Client):
        self.parent = parent


class BlocksChildrenEndpoint(Endpoint):
    def append(self, block_id, **kwargs):
        return self.parent.request(
            path=f"blocks/{block_id}/children",
            method="PATCH",
            body=pick(kwargs, "children"),
        )

    def list(self, block_id, **kwargs):
        return self.parent.request(
            path=f"blocks/{block_id}/children",
            method="GET",
            query=pick(kwargs, "start_cursor", "page_size"),
        )


class BlocksEndpoint(Endpoint):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.children = BlocksChildrenEndpoint(*args, **kwargs)


class DatabasesEndpoint(Endpoint):
    def list(
        self,
        start_cursor: Optional[str] = None,
        page_size: Optional[int] = None,
    ) -> httpx.Request:
        return self.parent.client.build_request(
            method="GET",
            url="databases",
            params={"start_cursor": start_cursor, "page_size": page_size},
        )

    def query(
        self,
        database_id: str,
        sorts: Optional[dict] = None,
        filter: Optional[Sequence] = None,
        start_cursor: Optional[str] = None,
        page_size: Optional[int] = None,
    ) -> httpx.Request:
        return self.parent.client.build_request(
            method="POST",
            url=f"databases/{database_id}/query",
            json={
                "start_cursor": start_cursor,
                "page_size": page_size,
                "sorts": sorts,
                "filter": filter,
            },
        )

    def retrieve(self, database_id: str):
        return self.parent.client.build_request(
            method="GET",
            url=f"databases/{database_id}",
        )


class PagesEndpoint(Endpoint):
    def create(self, **kwargs):
        return self.parent.request(
            path="pages",
            method="POST",
            body=pick(kwargs, "parent", "properties", "children"),
        )

    def retrieve(self, page_id, **kwargs):
        return self.parent.request(
            path=f"pages/{page_id}",
            method="GET",
        )

    def update(self, page_id, **kwargs):
        return self.parent.request(
            path=f"pages/{page_id}",
            method="PATCH",
            body=pick(kwargs, "properties"),
        )


class UsersEndpoint(Endpoint):
    def list(self, **kwargs):
        return self.parent.request(
            path="users",
            method="GET",
            query=pick(kwargs, "start_cursor", "page_size"),
            auth=kwargs.get("auth"),
        )

    def retrieve(self, user_id, **kwargs):
        return self.parent.request(
            path=f"users/{user_id}",
            method="GET",
        )
