"""Tests for config-flow outcomes using synthetic input."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.atag_zone_cloud.api import AtagZoneAuthenticationError
from custom_components.atag_zone_cloud.config_flow import AtagZoneCloudConfigFlow

INPUT = {"username": "user@example.com", "password": "example_password", "system_id": "YOUR_SYSTEM_ID"}


def _flow():
    flow = AtagZoneCloudConfigFlow()
    flow.hass = MagicMock()
    flow.async_set_unique_id = AsyncMock()
    flow._abort_if_unique_id_configured = MagicMock()
    return flow


@pytest.mark.asyncio
async def test_config_flow_success():
    flow = _flow()
    with (
        patch("custom_components.atag_zone_cloud.config_flow.async_get_clientsession"),
        patch(
            "custom_components.atag_zone_cloud.config_flow.AtagZoneApiClient.async_get_menu_items",
            new=AsyncMock(return_value={1: {"id": 1, "value": 8.5}}),
        ),
    ):
        result = await flow.async_step_user(INPUT)
    assert result["type"] == "create_entry"
    assert result["data"] == INPUT


@pytest.mark.asyncio
async def test_config_flow_authentication_failure():
    flow = _flow()
    with (
        patch("custom_components.atag_zone_cloud.config_flow.async_get_clientsession"),
        patch(
            "custom_components.atag_zone_cloud.config_flow.AtagZoneApiClient.async_get_menu_items",
            new=AsyncMock(side_effect=AtagZoneAuthenticationError()),
        ),
    ):
        result = await flow.async_step_user(INPUT)
    assert result["type"] == "form"
    assert result["errors"] == {"base": "invalid_auth"}


@pytest.mark.asyncio
async def test_duplicate_configuration_prevention():
    flow = _flow()
    flow._abort_if_unique_id_configured.side_effect = RuntimeError("duplicate prevented")
    with pytest.raises(RuntimeError, match="duplicate prevented"):
        await flow.async_step_user(INPUT)
