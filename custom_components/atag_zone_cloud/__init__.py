"""ATAG Zone Cloud integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import AtagZoneApiClient
from .const import CONF_SYSTEM_ID, PLATFORMS
from .coordinator import AtagZoneCoordinator

type AtagZoneConfigEntry = ConfigEntry[AtagZoneCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: AtagZoneConfigEntry) -> bool:
    """Set up from a config entry."""
    client = AtagZoneApiClient(
        async_get_clientsession(hass), entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD], entry.data[CONF_SYSTEM_ID]
    )
    coordinator = AtagZoneCoordinator(hass, client, entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: AtagZoneConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
