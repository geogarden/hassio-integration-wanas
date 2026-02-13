"""Sensor platform for Wanas integration."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SENSOR_DESCRIPTIONS, WanasSensorDescription
from .coordinator import WanasCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Wanas sensor entities."""
    coordinator: WanasCoordinator = entry.runtime_data
    async_add_entities(
        WanasSensor(coordinator, entry, desc) for desc in SENSOR_DESCRIPTIONS
    )


class WanasSensor(CoordinatorEntity[WanasCoordinator], SensorEntity):
    """Representation of a Wanas sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: WanasCoordinator,
        entry: ConfigEntry,
        description: WanasSensorDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_translation_key = description.key
        self._attr_name = coordinator.registers.get(
            f"{description.key}_name", description.name
        )
        self._attr_native_unit_of_measurement = description.unit
        self._attr_device_class = description.device_class
        self._attr_state_class = description.state_class
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Wanas Rekuperator",
            manufacturer="Wanas",
        )

    @property
    def native_value(self) -> float | int | None:
        """Return the sensor value."""
        if self.coordinator.data is None:
            return None
        address = self.coordinator.registers.get(
            f"{self._description.key}_address", self._description.address
        )
        return WanasCoordinator.get_sensor_value(
            self.coordinator.data,
            address,
            self._description.data_type,
            self._description.scale,
        )
