"""Tests for diagnostics redaction."""

from types import SimpleNamespace

import pytest

from custom_components.atag_zone_cloud.diagnostics import async_get_config_entry_diagnostics


@pytest.mark.asyncio
async def test_diagnostics_redact_private_configuration():
    coordinator = SimpleNamespace(data={1: {"id": 1, "value": 8.5}}, last_update_success=True)
    entry = SimpleNamespace(
        data={"username": "user@example.com", "password": "example_password", "system_id": "YOUR_SYSTEM_ID"},
        runtime_data=coordinator,
    )
    diagnostics = await async_get_config_entry_diagnostics(None, entry)
    serialized = str(diagnostics)
    assert "user@example.com" not in serialized
    assert "example_password" not in serialized
    assert "YOUR_SYSTEM_ID" not in serialized
    assert diagnostics["available_menu_item_ids"] == [1]
