"""Data coordinator for ATAG Zone Cloud."""

import logging
from datetime import timedelta
from typing import Any

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import AtagZoneApiClient, AtagZoneApiError, AtagZoneAuthenticationError
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN, MENU_ITEM_IDS

_LOGGER = logging.getLogger(__name__)


class AtagZoneCoordinator(DataUpdateCoordinator[dict[int, dict[str, Any]]]):
    """Coordinate cloud updates."""

    def __init__(self, hass, client: AtagZoneApiClient, config_entry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.client = client

    async def _async_update_data(self) -> dict[int, dict[str, Any]]:
        try:
            return await self.client.async_get_menu_items(MENU_ITEM_IDS)
        except AtagZoneAuthenticationError as err:
            raise UpdateFailed("ATAG Zone authentication failed") from err
        except AtagZoneApiError as err:
            raise UpdateFailed("Unable to update ATAG Zone data") from err
