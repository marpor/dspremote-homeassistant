"""Sensor entities for dspremote read-only fields."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import DspremoteCoordinator
from .entity import DspremoteFieldEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: DspremoteCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        DspremoteSensorEntity(coordinator, descriptor)
        for descriptor in coordinator.fields
        if descriptor.read_only
        and coordinator.is_field_selected(descriptor.path)
    ]
    async_add_entities(entities)


class DspremoteSensorEntity(DspremoteFieldEntity, SensorEntity):
    """Read-only field entity."""

    @property
    def native_unit_of_measurement(self):
        if self.descriptor.unit == "dB":
            return "dB"
        return self.descriptor.unit

