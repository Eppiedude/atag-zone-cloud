"""Tests for the ATAG Zone API client."""

import pytest

from custom_components.atag_zone_cloud.api import (
    AtagZoneApiClient,
    AtagZoneAuthenticationError,
    AtagZoneCommunicationError,
)
from custom_components.atag_zone_cloud.const import LOGIN_URL
from tests.conftest import FakeResponse, FakeSession


@pytest.mark.asyncio
async def test_successful_login_and_token_extraction(credentials):
    session = FakeSession(FakeResponse(200, {"token": "example_token"}))
    client = AtagZoneApiClient(session, *credentials)
    await client.async_login()
    assert client._token == "example_token"
    assert session.calls[0][0] == LOGIN_URL
    assert session.calls[0][1]["headers"]["User-Agent"].startswith("Home Assistant")


@pytest.mark.asyncio
async def test_login_uses_get_params_for_url_encoding(credentials):
    session = FakeSession(FakeResponse(200, {"token": "example_token"}))
    client = AtagZoneApiClient(session, *credentials)
    await client.async_login()
    assert session.calls[0][1]["params"] == {"userName": "user@example.com", "password": "p@ss word&more"}


@pytest.mark.asyncio
async def test_invalid_authentication(credentials):
    client = AtagZoneApiClient(FakeSession(FakeResponse(403, {"message": "denied"})), *credentials)
    with pytest.raises(AtagZoneAuthenticationError):
        await client.async_login()


@pytest.mark.asyncio
async def test_missing_token_is_authentication_error(credentials):
    client = AtagZoneApiClient(FakeSession(FakeResponse(200, {})), *credentials)
    with pytest.raises(AtagZoneAuthenticationError):
        await client.async_login()


@pytest.mark.asyncio
async def test_menu_items_parsing_skips_absent_and_error_items(credentials):
    session = FakeSession(
        FakeResponse(200, {"token": "example_token"}),
        FakeResponse(200, [{"id": 1, "value": 8.5}, {"id": 340, "error": True}]),
    )
    data = await AtagZoneApiClient(session, *credentials).async_get_menu_items((1, 2, 340))
    assert data == {1: {"id": 1, "value": 8.5}}
    assert 2 not in data


@pytest.mark.asyncio
async def test_only_curated_requested_ids_are_accepted(credentials):
    session = FakeSession(
        FakeResponse(200, {"token": "example_token"}),
        FakeResponse(200, [{"id": 1, "value": 8.5}, {"id": 999, "value": "private"}]),
    )
    data = await AtagZoneApiClient(session, *credentials).async_get_menu_items((1,))
    assert list(data) == [1]


@pytest.mark.asyncio
async def test_token_refresh_and_reauthentication(credentials):
    session = FakeSession(
        FakeResponse(200, {"token": "first_token"}),
        FakeResponse(401, {}),
        FakeResponse(200, {"token": "second_token"}),
        FakeResponse(200, [{"id": 1, "value": 9.0}]),
    )
    client = AtagZoneApiClient(session, *credentials)
    assert await client.async_get_menu_items((1,)) == {1: {"id": 1, "value": 9.0}}
    assert session.calls[-1][1]["headers"]["ar.authToken"] == "second_token"


@pytest.mark.asyncio
async def test_server_error_is_update_error(credentials):
    session = FakeSession(FakeResponse(200, {"token": "example_token"}), FakeResponse(500, {"Message": "error"}))
    with pytest.raises(AtagZoneCommunicationError):
        await AtagZoneApiClient(session, *credentials).async_get_menu_items((1,))


@pytest.mark.asyncio
async def test_server_error_for_one_item_does_not_destroy_other_data(credentials):
    session = FakeSession(
        FakeResponse(200, {"token": "example_token"}),
        FakeResponse(500, {"Message": "error"}),
        FakeResponse(200, [{"id": 1, "value": 8.5}]),
        FakeResponse(500, {"Message": "error"}),
    )
    data = await AtagZoneApiClient(session, *credentials).async_get_menu_items((1, 302))
    assert data == {1: {"id": 1, "value": 8.5}}
