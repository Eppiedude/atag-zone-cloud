"""Data coordinator for ATAG Zone Cloud."""

import logging
from datetime import timedelta
from typing import Any

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import AtagZoneApiClient, AtagZoneApiError, AtagZoneAuthenticationError
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN, MENU_ITEM_IDS

_LOGGER = logging.getLogger(__name__)
FAILURE_THRESHOLD = 3


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
        self.failure_count = 0

    async def _async_update_data(self) -> dict[int, dict[str, Any]]:
        try:
            update = await self.client.async_get_menu_items(MENU_ITEM_IDS)
        except AtagZoneAuthenticationError as err:
            return self._handle_failure("authentication", err)
        except AtagZoneApiError as err:
            return self._handle_failure("communication", err)

        self.failure_count = 0
        return {**(self.data or {}), **update}

    def _handle_failure(self, kind: str, err: AtagZoneApiError) -> dict[int, dict[str, Any]]:
        """Retain valid data until the failure threshold is reached."""
        self.failure_count += 1
        if self.failure_count < FAILURE_THRESHOLD and self.data:
            if self.failure_count == 1:
                _LOGGER.warning("Temporary ATAG Zone %s failure; retaining last valid data", kind)
            return self.data
        message = "ATAG Zone authentication failed" if kind == "authentication" else "Unable to update ATAG Zone data"
        raise UpdateFailed(message) from err
