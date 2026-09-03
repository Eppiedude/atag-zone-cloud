"""Binary sensor entities for ATAG Zone Cloud."""

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity

from . import AtagZoneConfigEntry
from .const import CONF_SYSTEM_ID, MENU_ITEMS, ItemKind, MenuItemDescription
from .entity import AtagZoneEntity


async def async_setup_entry(hass, entry: AtagZoneConfigEntry, async_add_entities) -> None:
    """Add only binary sensors returned by this installation."""
    coordinator = entry.runtime_data
    async_add_entities(
        AtagZoneBinarySensor(coordinator, description, entry.data[CONF_SYSTEM_ID])
        for description in MENU_ITEMS
        if description.kind is ItemKind.BINARY_SENSOR and description.item_id in coordinator.data
    )


class AtagZoneBinarySensor(AtagZoneEntity, BinarySensorEntity):
    """Representation of a binary ATAG menu item."""

    def __init__(self, coordinator, description: MenuItemDescription, system_id: str) -> None:
        super().__init__(coordinator, description, system_id)
        self._attr_device_class = BinarySensorDeviceClass.HEAT

    @property
    def is_on(self) -> bool | None:
        value = self._item.get("value")
        if value is None:
            return None
        try:
            return int(value) == 1
        except (TypeError, ValueError):
            return None
