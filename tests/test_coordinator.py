"""Tests for coordinator error conversion."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.atag_zone_cloud.api import AtagZoneAuthenticationError, AtagZoneCommunicationError
from custom_components.atag_zone_cloud.coordinator import AtagZoneCoordinator


@pytest.mark.asyncio
@pytest.mark.parametrize("error", [AtagZoneAuthenticationError(), AtagZoneCommunicationError()])
async def test_coordinator_update_failure_handling(error):
    hass = MagicMock()
    hass.loop = None
    client = MagicMock()
    client.async_get_menu_items = AsyncMock(side_effect=error)
    coordinator = AtagZoneCoordinator(hass, client, MagicMock())
    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()
