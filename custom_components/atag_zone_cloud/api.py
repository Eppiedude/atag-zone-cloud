"""Async client for the read-only ATAG Zone cloud API."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from aiohttp import ClientError, ClientResponse, ClientSession

from .const import LOGIN_URL, MENU_ITEMS_URL, REQUEST_HEADERS


class AtagZoneApiError(Exception):
    """Base API exception."""


class AtagZoneAuthenticationError(AtagZoneApiError):
    """Authentication was rejected."""


class AtagZoneCommunicationError(AtagZoneApiError):
    """Communication with the API failed."""


class AtagZoneApiClient:
    """Small read-only API client."""

    def __init__(self, session: ClientSession, username: str, password: str, system_id: str) -> None:
        self._session = session
        self._username = username
        self._password = password
        self._system_id = system_id
        self._token: str | None = None

    async def _json(self, response: ClientResponse) -> Any:
        try:
            return await response.json(content_type=None)
        except (ValueError, ClientError) as err:
            raise AtagZoneCommunicationError("ATAG Zone returned an invalid response") from err

    async def async_login(self) -> None:
        """Authenticate using the API's verified GET query semantics."""
        try:
            response = await self._session.get(
                LOGIN_URL,
                params={"userName": self._username, "password": self._password},
                headers=REQUEST_HEADERS,
            )
            payload = await self._json(response)
        except ClientError as err:
            raise AtagZoneCommunicationError("Unable to reach ATAG Zone") from err
        token = payload.get("token") if isinstance(payload, dict) else None
        if response.status != 200 or not isinstance(token, str) or not token:
            raise AtagZoneAuthenticationError("ATAG Zone authentication failed")
        self._token = token

    async def _request_items(self, item_ids: Iterable[int]) -> tuple[int, Any]:
        try:
            response = await self._session.get(
                MENU_ITEMS_URL.format(system_id=self._system_id),
                params={"menuItems": ",".join(str(item_id) for item_id in item_ids)},
                headers={**REQUEST_HEADERS, "ar.authToken": self._token or ""},
            )
            return response.status, await self._json(response)
        except ClientError as err:
            raise AtagZoneCommunicationError("Unable to reach ATAG Zone") from err

    async def async_get_menu_items(self, item_ids: Iterable[int]) -> dict[int, dict[str, Any]]:
        """Fetch curated items, re-authenticating once when necessary."""
        ids = tuple(item_ids)
        if self._token is None:
            await self.async_login()
        status, payload = await self._request_items(ids)
        if status in (401, 403):
            await self.async_login()
            status, payload = await self._request_items(ids)
        if status in (401, 403):
            raise AtagZoneAuthenticationError("ATAG Zone authentication failed")
        if status >= 500 and len(ids) > 1:
            recovered: dict[int, dict[str, Any]] = {}
            successful_request = False
            for item_id in ids:
                item_status, item_payload = await self._request_items((item_id,))
                if item_status == 200 and isinstance(item_payload, list):
                    successful_request = True
                    recovered.update(self._parse_items(item_payload, (item_id,)))
            if successful_request:
                return recovered
        if status != 200 or not isinstance(payload, list):
            raise AtagZoneCommunicationError(f"ATAG Zone data request failed with HTTP {status}")

        return self._parse_items(payload, ids)

    @staticmethod
    def _parse_items(payload: list[Any], ids: tuple[int, ...]) -> dict[int, dict[str, Any]]:
        """Parse supported items and silently discard item-level errors."""
        result: dict[int, dict[str, Any]] = {}
        for raw_item in payload:
            if not isinstance(raw_item, dict) or raw_item.get("error"):
                continue
            item_id = raw_item.get("id")
            if isinstance(item_id, (int, float)) and int(item_id) in ids:
                result[int(item_id)] = raw_item
        return result
