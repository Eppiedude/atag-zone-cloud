"""Tests for dynamic sensor and binary-sensor behavior."""

from unittest.mock import MagicMock

from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.sensor import SensorDeviceClass

from custom_components.atag_zone_cloud.binary_sensor import AtagZoneBinarySensor
from custom_components.atag_zone_cloud.const import MENU_ITEMS
from custom_components.atag_zone_cloud.sensor import AtagZoneSensor, _api_enum_options


def _description(item_id):
    return next(item for item in MENU_ITEMS if item.item_id == item_id)


def _coordinator(data):
    coordinator = MagicMock()
    coordinator.data = data
    coordinator.async_add_listener.return_value = MagicMock()
    return coordinator


def test_temperature_sensor_creation():
    entity = AtagZoneSensor(_coordinator({1: {"id": 1, "value": 7.5}}), _description(1), "YOUR_SYSTEM_ID")
    assert entity.device_class is SensorDeviceClass.TEMPERATURE
    assert entity.native_value == 7.5


def test_humidity_sensor_creation():
    entity = AtagZoneSensor(_coordinator({146: {"id": 146, "value": 48}}), _description(146), "YOUR_SYSTEM_ID")
    assert entity.device_class is SensorDeviceClass.HUMIDITY
    assert entity.native_value == 48


def test_heat_request_binary_sensor_creation():
    entity = AtagZoneBinarySensor(_coordinator({8: {"id": 8, "value": 1}}), _description(8), "YOUR_SYSTEM_ID")
    assert entity.device_class is BinarySensorDeviceClass.HEAT
    assert entity.is_on is True


def test_heat_request_inactive():
    entity = AtagZoneBinarySensor(_coordinator({8: {"id": 8, "value": 0}}), _description(8), "YOUR_SYSTEM_ID")
    assert entity.is_on is False


def test_heat_pump_mode_enum():
    entity = AtagZoneSensor(_coordinator({340: {"id": 340, "value": 3}}), _description(340), "YOUR_SYSTEM_ID")
    assert entity.device_class is SensorDeviceClass.ENUM
    assert entity.native_value == "heating"
    assert "defrost" in entity.options


def test_api_enum_parsing_preserves_full_options():
    assert _api_enum_options(
        {"options": [{"value": 8, "text": "Example scheme"}, {"value": 9, "text": "Another scheme"}]}
    ) == {8: "Example scheme", 9: "Another scheme"}


def test_api_enum_sensor_gets_enum_device_class():
    item = {
        "id": 302,
        "value": 8,
        "options": [{"value": 8, "text": "Example scheme"}],
    }
    entity = AtagZoneSensor(
        _coordinator({302: item}), _description(302), "YOUR_SYSTEM_ID"
    )
    assert entity.device_class is SensorDeviceClass.ENUM
    assert entity.native_value == "Example scheme"
