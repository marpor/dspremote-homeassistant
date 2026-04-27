"""Number entities for dspremote numeric writable fields."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfDecibel
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
        DspremoteNumberEntity(coordinator, descriptor)
        for descriptor in coordinator.fields
        if descriptor.value_type in {"number", "integer"}
        and descriptor.access == "readWrite"
        and coordinator.is_field_selected(descriptor.path)
    ]
    async_add_entities(entities)


class DspremoteNumberEntity(DspremoteFieldEntity, NumberEntity):
    """Writable numeric dspremote field."""

    _attr_mode = NumberMode.SLIDER

    @property
    def native_unit_of_measurement(self):
        if self.descriptor.unit == "dB":
            return UnitOfDecibel.DECIBEL
        return self.descriptor.unit

    @property
    def native_min_value(self):
        if self.descriptor.range_spec and "min" in self.descriptor.range_spec:
            return float(self.descriptor.range_spec["min"])
        return None

    @property
    def native_max_value(self):
        if self.descriptor.range_spec and "max" in self.descriptor.range_spec:
            return float(self.descriptor.range_spec["max"])
        return None

    @property
    def native_step(self):
        if self.descriptor.range_spec and "step" in self.descriptor.range_spec:
            return float(self.descriptor.range_spec["step"])
        return None

    async def async_set_native_value(self, value: float) -> None:
        payload = (
            {"integer": int(value)}
            if self.descriptor.value_type == "integer"
            else {"number": float(value)}
        )
        await self.coordinator.api.write_value(self.descriptor.path, payload)
        await self.coordinator.async_request_refresh()

