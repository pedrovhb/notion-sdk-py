import abc
from functools import cached_property
from typing import Any, Dict, Final, Optional, Sequence, Union

import httpx

# @dataclass
# class ClientOptions:
#     auth: str = None
#     timeout_ms: int = 60_000
#     base_url: str = "https://api.notion.com"
#     log_level: int = logging.WARNING
#     logger: logging.Logger = None
#     notion_version: str = "2021-05-13"


DEFAULT_BASE_URL: Final[str] = "https://api.notion.com/v1/"
DEFAULT_NOTION_VERSION: Final[str] = "2021-05-13"
# todo - change default UA before PR
DEFAULT_USER_AGENT: Final[str] = "pedrovhb/notion-sdk-py@0.3.0"
DEFAULT_PAGE_SIZE: Final[int] = 100

"""
Test snippet - 


import os
from notion_client import Client

token = "my_token"

notion = Client(auth_token=token)
dbs = notion.list_databases()
print("dbs:", dbs)
first_db = notion.get_database(dbs["results"][0]["id"])
print("first_db:", first_db)
"""


class BaseClient(abc.ABC):
    def __init__(
        self,
        auth_token: str,
        user_agent: str = DEFAULT_USER_AGENT,
        base_url: str = DEFAULT_BASE_URL,
        notion_version: str = DEFAULT_NOTION_VERSION,
        page_size: int = DEFAULT_PAGE_SIZE,
        **additional_http_kwargs: Any,
    ) -> None:
        self._auth_token = auth_token
        self._user_agent = user_agent
        self._base_url = base_url
        self._notion_version = notion_version
        self._additional_http_kwargs = additional_http_kwargs
        self.page_size = page_size

    @abc.abstractmethod
    @cached_property
    def _http_client(self) -> Union[httpx.Client, httpx.AsyncClient]:
        raise NotImplementedError

    def _get_http_client_kwargs(self) -> Dict[str, Any]:
        headers: Dict[str, str] = {
            "Notion-Version": self._notion_version,
            "User-Agent": self._user_agent,
            "Authorization": f"Bearer {self._auth_token}",
        }

        if self._additional_http_kwargs.get("headers"):
            additional_headers = self._additional_http_kwargs.pop("headers")
            headers.update(additional_headers)

        return {
            "base_url": self._base_url,
            "headers": headers,
            **self._additional_http_kwargs,
        }

    def _build_request_databases_list(
        self,
        start_cursor: Optional[int] = None,
    ) -> httpx.Request:
        params = {"page_size": self.page_size}
        if start_cursor:
            params["start_cursor"] = start_cursor
        return self._http_client.build_request(
            method="GET",
            url="databases",
            params=params,
        )

    def _build_request_databases_query(
        self,
        database_id: str,
        sorts: Optional[dict] = None,
        filter: Optional[Sequence] = None,
        start_cursor: Optional[int] = None,
    ) -> httpx.Request:
        return self._http_client.build_request(
            method="POST",
            url=f"databases/{database_id}/query",
            json={
                "start_cursor": start_cursor,
                "page_size": self.page_size,
                "sorts": sorts,
                "filter": filter,
            },
        )

    def _build_request_databases_retrieve(
        self,
        database_id: str,
    ) -> httpx.Request:
        return self._http_client.build_request(
            method="GET",
            url=f"databases/{database_id}",
        )

    @abc.abstractmethod
    def list_databases(self, start_cursor: Optional[str] = None) -> dict:
        raise NotImplementedError

    @abc.abstractmethod
    def get_database(self, database_id: str) -> dict:
        raise NotImplementedError


class Client(BaseClient):
    @cached_property
    def _http_client(self) -> httpx.Client:
        client_kwargs = self._get_http_client_kwargs()
        return httpx.Client(**client_kwargs)

    def _send_request(self, request: httpx.Request) -> dict:
        response = self._http_client.send(request)
        data = response.json()
        assert isinstance(data, dict)
        return data

    def list_databases(self, start_cursor: Optional[int] = None) -> dict:
        # todo - think of returning manager object with
        #  auto pagination instead of dict
        request = self._build_request_databases_list(start_cursor=start_cursor)
        return self._send_request(request)

    def get_database(self, database_id: str) -> dict:
        request = self._build_request_databases_retrieve(database_id=database_id)
        return self._send_request(request)


# class Client:
#     def __init__(
#         self,
#         options: Union[Dict, ClientOptions] = None,
#         client: httpx.Client = None,
#         **kwargs,
#     ):
#         if options is None:
#             options = ClientOptions(**kwargs)
#         elif isinstance(options, dict):
#             options = ClientOptions(**options)
#
#         self.logger = options.logger or make_console_logger()
#         self.logger.setLevel(options.log_level)
#
#         if client is None:
#             client = httpx.Client()
#         self.client = client
#         self.client.base_url = options.base_url + "/v1/"
#         self.client.timeout = options.timeout_ms / 1_000
#         self.client.headers = {
#             "Notion-Version": options.notion_version,
#             "User-Agent": "ramnes/notion-sdk-py@0.3.0",
#         }
#         if options.auth:
#             self.client.headers["Authorization"] = f"Bearer {options.auth}"
#
#         self.blocks = BlocksEndpoint(self)
#         self.databases = DatabasesEndpoint(self)
#         self.users = UsersEndpoint(self)
#         self.pages = PagesEndpoint(self)
#
#     # def _build_request(self, method, path, body):
#     #     self.logger.info(f"{method} {self.client.base_url}{path}")
#     #     return self.client.build_request(method, path, json=body)
#
#     def list_databases(
#         self,
#         start_cursor: Optional[str] = None,
#         page_size: Optional[int] = None,
#     ) -> dict:
#         request = self.l
#
#     def request(self, path, method, query=None, body=None, auth=None):
#         request = self._build_request(method, path, body)
#         return self.client.send(request)
#
#     def search(self, **kwargs):
#         return self.request(
#             path="search",
#             method="POST",
#             body=pick(
#                 kwargs, "query", "sort", "filter", "start_cursor", "page_size"
#             ),
#         )
#
#
# class AsyncClient(Client):
#     def __init__(
#         self,
#         options: Union[Dict, ClientOptions] = None,
#         client: httpx.AsyncClient = None,
#         **kwargs,
#     ):
#         if client is None:
#             client = httpx.AsyncClient()
#         super().__init__(options, client, **kwargs)
#
#     async def request(self, path, method, query=None, body=None, auth=None):
#         request = self._build_request(method, path, body)
#         async with self.client as client:
#             response = await client.send(request)
#         return response
