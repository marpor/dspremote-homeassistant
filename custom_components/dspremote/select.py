"""Select entities for dspremote enum fields."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
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
        DspremoteSelectEntity(coordinator, descriptor)
        for descriptor in coordinator.fields
        if descriptor.value_type == "enum"
        and not descriptor.read_only
        and descriptor.enum_values
        and coordinator.is_field_selected(descriptor.path)
    ]
    async_add_entities(entities)


class DspremoteSelectEntity(DspremoteFieldEntity, SelectEntity):
    """Writable enum field."""

    @property
    def options(self) -> list[str]:
        return self.descriptor.enum_values

    @property
    def current_option(self) -> str | None:
        value = self.native_value
        return value if isinstance(value, str) else None

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.api.write_value(self.descriptor.path, {"enum": option})
        await self.coordinator.async_request_refresh()

