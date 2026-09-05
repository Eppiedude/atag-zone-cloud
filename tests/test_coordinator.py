"""Tests for coordinator error conversion."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.atag_zone_cloud.api import AtagZoneAuthenticationError, AtagZoneCommunicationError
from custom_components.atag_zone_cloud.coordinator import AtagZoneCoordinator


@pytest.mark.asyncio
@pytest.mark.parametrize("error", [AtagZoneAuthenticationError(), AtagZoneCommunicationError()])
async def test_coordinator_retains_data_until_third_failure_and_recovers(error):
    hass = MagicMock()
    hass.loop = None
    client = MagicMock()
    client.async_get_menu_items = AsyncMock(side_effect=[error, error, error, {1: {"id": 1, "value": 9.0}}])
    coordinator = AtagZoneCoordinator(hass, client, MagicMock())
    coordinator.data = {1: {"id": 1, "value": 8.5}}
    assert await coordinator._async_update_data() == coordinator.data
    assert await coordinator._async_update_data() == coordinator.data
    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()
    assert await coordinator._async_update_data() == {1: {"id": 1, "value": 9.0}}
    assert coordinator.failure_count == 0


@pytest.mark.asyncio
async def test_coordinator_merges_partial_update_with_last_valid_data():
    hass = MagicMock()
    hass.loop = None
    client = MagicMock()
    client.async_get_menu_items = AsyncMock(return_value={1: {"id": 1, "value": 9.0}})
    coordinator = AtagZoneCoordinator(hass, client, MagicMock())
    coordinator.data = {1: {"id": 1, "value": 8.5}, 2: {"id": 2, "value": 20.0}}
    assert await coordinator._async_update_data() == {
        1: {"id": 1, "value": 9.0},
        2: {"id": 2, "value": 20.0},
    }
