import inspect
import os
import re
import time
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

import httpx
from criteo_api import api, rest
from criteo_api.api_client import ApiClient
from criteo_api.configuration import Configuration
from mcp.server.fastmcp import FastMCP


class ClientCredentialsApiClient(ApiClient):
    def __init__(
        self,
        configuration=None,
        header_name=None,
        header_value=None,
        cookie=None,
        *,
        client_id: str,
        client_secret: str,
    ):
        super().__init__(configuration, header_name, header_value, cookie)
        self.client_id = client_id
        self.client_secret = client_secret
        self._token_data: dict[str, Any] | None = None
        self._valid_until: float = 0

    @property
    def token_data(self) -> dict[str, Any] | None:
        return self._token_data if time.time() < self._valid_until else None

    @token_data.setter
    def token_data(self, value: dict[str, Any]) -> None:
        self._token_data = value
        self._valid_until = time.time() + value["expires_in"]

    async def fetch_token(self) -> dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.configuration.host}/oauth2/token",
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "grant_type": "client_credentials",
                },
            )
            response.raise_for_status()
            token_data = response.json()
            return token_data

    async def call_api(
        self,
        method,
        url,
        header_params=None,
        body=None,
        post_params=None,
        _request_timeout=None,
    ) -> rest.RESTResponse:
        if not self.token_data:
            self.token_data = await self.fetch_token()
        if header_params is None:
            header_params = {}
        header_params.setdefault(
            "Authorization", f"Bearer {self.token_data['access_token']}"
        )
        return await super().call_api(
            method,
            url,
            header_params,
            body,
            post_params,
            _request_timeout,
        )


BASE_URL = os.environ.get("CRITEO_MCP_BASE_URL", "https://api.criteo.com")
CLIENT_ID = os.environ.get("CRITEO_MCP_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("CRITEO_MCP_CLIENT_SECRET", "")

clean_re = re.compile(
    r"_[a-z]*\d+|_external|_api|retail_media_|marketing_solutions_|preview_|call_\d+_"
)


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[None]:
    async with ClientCredentialsApiClient(
        configuration=Configuration(host=BASE_URL),
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
    ) as client:
        for cls_name, cls in inspect.getmembers(api, inspect.isclass):
            for name, member in inspect.getmembers(cls(client), inspect.ismethod):
                if (
                    name.startswith("_")
                    or name.endswith("_with_http_info")
                    or name.endswith("_without_preload_content")
                ):
                    continue
                assert member.__doc__
                server.add_tool(
                    member,
                    name=f"{cls_name}-{clean_re.sub('', name)}"[:64],
                    description=member.__doc__.splitlines()[2],
                    skip_names=[
                        name
                        for name in inspect.signature(member).parameters
                        if name.startswith("_")
                    ],
                )
        yield


mcp = FastMCP("Criteo API", lifespan=app_lifespan)
