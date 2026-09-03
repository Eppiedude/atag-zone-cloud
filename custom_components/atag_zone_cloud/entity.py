"""Base entity for ATAG Zone Cloud."""

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, NAME, MenuItemDescription
from .coordinator import AtagZoneCoordinator


class AtagZoneEntity(CoordinatorEntity[AtagZoneCoordinator]):
    """Base coordinator entity."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: AtagZoneCoordinator, description: MenuItemDescription, system_id: str) -> None:
        super().__init__(coordinator)
        self.item_description = description
        self._attr_unique_id = f"{system_id}_{description.item_id}"
        self._attr_translation_key = description.translation_key
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, system_id)},
            name=NAME,
            manufacturer="ATAG",
            model="ATAG Zone system",
        )

    @property
    def _item(self) -> dict:
        return self.coordinator.data[self.item_description.item_id]
