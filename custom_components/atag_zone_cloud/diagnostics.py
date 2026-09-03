"""Privacy-safe diagnostics for ATAG Zone Cloud."""

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME

from .const import CONF_SYSTEM_ID

TO_REDACT = {CONF_USERNAME, CONF_PASSWORD, CONF_SYSTEM_ID, "token", "ar.authToken"}


async def async_get_config_entry_diagnostics(hass, entry) -> dict:
    """Return only redacted configuration and non-identifying item metadata."""
    coordinator = entry.runtime_data
    return {
        "config_entry": async_redact_data(dict(entry.data), TO_REDACT),
        "available_menu_item_ids": sorted(coordinator.data),
        "last_update_success": coordinator.last_update_success,
    }
