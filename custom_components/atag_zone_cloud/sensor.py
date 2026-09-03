"""Sensor entities for ATAG Zone Cloud."""

from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity

from . import AtagZoneConfigEntry
from .const import CONF_SYSTEM_ID, MENU_ITEMS, ItemKind, MenuItemDescription
from .entity import AtagZoneEntity


def _api_enum_options(item: dict[str, Any]) -> dict[int, str]:
    """Extract enum choices while tolerating known API response shapes."""
    raw_options = item.get("options") or item.get("enumValues") or item.get("enum")
    parsed: dict[int, str] = {}
    if isinstance(raw_options, dict):
        for key, value in raw_options.items():
            try:
                parsed[int(key)] = str(value)
            except (TypeError, ValueError):
                continue
    elif isinstance(raw_options, list):
        for option in raw_options:
            if not isinstance(option, dict):
                continue
            key = option.get("value", option.get("id"))
            label = option.get("text", option.get("name"))
            try:
                if label is not None:
                    parsed[int(key)] = str(label)
            except (TypeError, ValueError):
                continue
    return parsed


async def async_setup_entry(hass, entry: AtagZoneConfigEntry, async_add_entities) -> None:
    """Add only sensors returned by this installation."""
    coordinator = entry.runtime_data
    async_add_entities(
        AtagZoneSensor(coordinator, description, entry.data[CONF_SYSTEM_ID])
        for description in MENU_ITEMS
        if description.kind is ItemKind.SENSOR and description.item_id in coordinator.data
    )


class AtagZoneSensor(AtagZoneEntity, SensorEntity):
    """Representation of an ATAG menu item."""

    def __init__(self, coordinator, description: MenuItemDescription, system_id: str) -> None:
        super().__init__(coordinator, description, system_id)
        api_options = _api_enum_options(self._item)
        self._attr_device_class = (
            SensorDeviceClass.ENUM
            if description.enum_options or api_options
            else description.device_class
        )
        self._attr_state_class = description.state_class
        self._attr_native_unit_of_measurement = description.unit
        self._attr_entity_category = description.entity_category

    @property
    def options(self) -> list[str] | None:
        mapping = self.item_description.enum_options or _api_enum_options(self._item)
        return list(dict.fromkeys(mapping.values())) or None

    @property
    def native_value(self) -> Any:
        value = self._item.get("value")
        mapping = self.item_description.enum_options or _api_enum_options(self._item)
        if mapping:
            try:
                return mapping.get(int(value), f"unknown_{value}")
            except (TypeError, ValueError):
                return str(value) if value is not None else None
        return value
