"""Constants and the curated ATAG Zone menu-item registry."""

from dataclasses import dataclass
from enum import StrEnum

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import PERCENTAGE, UnitOfTemperature
from homeassistant.helpers.entity import EntityCategory

DOMAIN = "atag_zone_cloud"
NAME = "ATAG Zone Cloud"
CONF_SYSTEM_ID = "system_id"
DEFAULT_SCAN_INTERVAL = 60
LOGIN_URL = "https://www.atagzone.remotethermo.com/api/v2/accounts/login"
MENU_ITEMS_URL = "https://www.atagzone.remotethermo.com/api/v2/menuItems/{system_id}"
REQUEST_HEADERS = {"User-Agent": "Home Assistant ATAG Zone Cloud/0.1"}


class ItemKind(StrEnum):
    """Supported entity kinds."""

    SENSOR = "sensor"
    BINARY_SENSOR = "binary_sensor"


@dataclass(frozen=True, slots=True)
class MenuItemDescription:
    """Description of a known menu item."""

    item_id: int
    translation_key: str
    kind: ItemKind = ItemKind.SENSOR
    device_class: SensorDeviceClass | str | None = None
    state_class: SensorStateClass | None = None
    unit: str | None = None
    entity_category: EntityCategory | None = None
    enum_options: dict[int, str] | None = None


TEMPERATURE = {
    "device_class": SensorDeviceClass.TEMPERATURE,
    "state_class": SensorStateClass.MEASUREMENT,
    "unit": UnitOfTemperature.CELSIUS,
}

HEAT_PUMP_MODES = {
    0: "off",
    1: "standby",
    2: "cooling",
    3: "heating",
    4: "booster_heating",
    5: "booster_cooling",
    6: "rating_heating_mode",
    7: "rating_cooling_mode",
    8: "freeze_protection",
    9: "defrost",
    10: "high_temperature_protection",
    11: "timeguard",
    12: "system_fail",
    13: "hard_system_fail",
    14: "pump_down",
    15: "soft_fail_mode",
    16: "rating_only_fan",
    17: "defrost",
    18: "cascade_heating",
    19: "cascade_cooling",
}

MENU_ITEMS: tuple[MenuItemDescription, ...] = (
    MenuItemDescription(1, "outdoor_temperature", **TEMPERATURE),
    MenuItemDescription(2, "room_temperature_zone_1", **TEMPERATURE),
    MenuItemDescription(3, "room_temperature_zone_2", **TEMPERATURE),
    MenuItemDescription(8, "heat_request_zone_1", ItemKind.BINARY_SENSOR, "heat"),
    MenuItemDescription(9, "heat_request_zone_2", ItemKind.BINARY_SENSOR, "heat"),
    MenuItemDescription(10, "heat_request_zone_3", ItemKind.BINARY_SENSOR, "heat"),
    MenuItemDescription(24, "dhw_setpoint", **TEMPERATURE),
    MenuItemDescription(
        119,
        "signal_level",
        state_class=SensorStateClass.MEASUREMENT,
        unit=PERCENTAGE,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    MenuItemDescription(
        146,
        "relative_humidity_zone_1",
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        unit=PERCENTAGE,
    ),
    MenuItemDescription(305, "dhw_temperature", **TEMPERATURE),
    MenuItemDescription(340, "heat_pump_mode", device_class=SensorDeviceClass.ENUM, enum_options=HEAT_PUMP_MODES),
    MenuItemDescription(341, "heat_pump_outside_air_temperature", **TEMPERATURE),
    MenuItemDescription(348, "heat_pump_water_flow_temperature", **TEMPERATURE),
    MenuItemDescription(349, "ch_flow_temperature", **TEMPERATURE),
    MenuItemDescription(391, "ch_flow_set_temperature", **TEMPERATURE),
    MenuItemDescription(302, "hydraulic_scheme", entity_category=EntityCategory.DIAGNOSTIC),
    MenuItemDescription(339, "heat_pump_quiet_mode", entity_category=EntityCategory.DIAGNOSTIC),
    MenuItemDescription(409, "buffer_activation", entity_category=EntityCategory.DIAGNOSTIC),
)

MENU_ITEM_IDS = tuple(item.item_id for item in MENU_ITEMS)
PLATFORMS = ("sensor", "binary_sensor")
