"""The Wanas integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .const import (
    BINARY_SENSOR_DESCRIPTIONS,
    DOMAIN,
    NUMBER_DESCRIPTIONS,
    SWITCH_DESCRIPTIONS,
)
from .coordinator import WanasCoordinator

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.NUMBER,
    Platform.SENSOR,
    Platform.SWITCH,
]

type WanasConfigEntry = ConfigEntry[WanasCoordinator]


def _purge_absent_modules(hass: HomeAssistant, entry: WanasConfigEntry) -> None:
    """Drop registry entries for modules the unit does not have.

    Without this, answering "no" to a module the user first said yes to would leave
    its entities behind as permanently unavailable.
    """
    coordinator: WanasCoordinator = entry.runtime_data
    absent = {
        f"{entry.entry_id}_{desc.key}"
        for desc in (*BINARY_SENSOR_DESCRIPTIONS, *SWITCH_DESCRIPTIONS, *NUMBER_DESCRIPTIONS)
        if not coordinator.has_feature(desc.feature)
    }
    if not absent:
        return

    registry = er.async_get(hass)
    for reg_entry in er.async_entries_for_config_entry(registry, entry.entry_id):
        if reg_entry.unique_id in absent:
            registry.async_remove(reg_entry.entity_id)


async def _async_update_listener(hass: HomeAssistant, entry: WanasConfigEntry) -> None:
    """Reload when the fitted modules change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_setup_entry(hass: HomeAssistant, entry: WanasConfigEntry) -> bool:
    """Set up Wanas from a config entry."""
    coordinator = WanasCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator
    _purge_absent_modules(hass, entry)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: WanasConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        coordinator: WanasCoordinator = entry.runtime_data
        await coordinator.async_close()

    return unload_ok
