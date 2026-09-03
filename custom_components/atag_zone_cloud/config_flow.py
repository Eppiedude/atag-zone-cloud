"""Config flow for ATAG Zone Cloud."""

from __future__ import annotations

import hashlib

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import AtagZoneApiClient, AtagZoneApiError, AtagZoneAuthenticationError
from .const import CONF_SYSTEM_ID, DOMAIN, MENU_ITEM_IDS


class AtagZoneCloudConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle an ATAG Zone Cloud config flow."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        """Collect and validate account details."""
        errors: dict[str, str] = {}
        if user_input is not None:
            system_id = user_input[CONF_SYSTEM_ID].strip()
            unique_id = hashlib.sha256(system_id.encode()).hexdigest()
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()
            client = AtagZoneApiClient(
                async_get_clientsession(self.hass),
                user_input[CONF_USERNAME].strip(),
                user_input[CONF_PASSWORD],
                system_id,
            )
            try:
                await client.async_get_menu_items(MENU_ITEM_IDS)
            except AtagZoneAuthenticationError:
                errors["base"] = "invalid_auth"
            except AtagZoneApiError:
                errors["base"] = "cannot_connect"
            else:
                data = {**user_input, CONF_USERNAME: user_input[CONF_USERNAME].strip(), CONF_SYSTEM_ID: system_id}
                return self.async_create_entry(title="ATAG Zone Cloud", data=data)

        schema = vol.Schema(
            {
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
                vol.Required(CONF_SYSTEM_ID): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
