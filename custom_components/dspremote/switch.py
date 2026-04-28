"""Switch entities for dspremote boolean fields."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
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
        DspremoteSwitchEntity(coordinator, descriptor)
        for descriptor in coordinator.fields
        if descriptor.value_type == "boolean"
        and not descriptor.read_only
        and coordinator.is_field_selected(descriptor.path)
    ]
    async_add_entities(entities)


class DspremoteSwitchEntity(DspremoteFieldEntity, SwitchEntity):
    """Writable boolean field."""

    @property
    def is_on(self) -> bool | None:
        value = self.native_value
        return value if isinstance(value, bool) else None

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.api.write_value(self.descriptor.path, {"boolean": True})
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.api.write_value(self.descriptor.path, {"boolean": False})
        await self.coordinator.async_request_refresh()

