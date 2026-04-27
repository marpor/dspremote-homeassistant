"""Button entities for dspremote action endpoints."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import slugify

from .const import DOMAIN
from .coordinator import ActionDescriptor, DspremoteCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: DspremoteCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for action in coordinator.actions:
        if not action.has_args:
            entities.append(DspremoteActionButtonEntity(coordinator, action, args={}))
            continue
        for preset_slot in action.preset_slots:
            entities.append(
                DspremoteActionButtonEntity(
                    coordinator,
                    action,
                    args={"preset": preset_slot},
                    label_suffix=f" slot {preset_slot}",
                )
            )
    async_add_entities(entities)


class DspremoteActionButtonEntity(ButtonEntity):
    """Action endpoint exposed as a button."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: DspremoteCoordinator,
        action: ActionDescriptor,
        args: dict,
        label_suffix: str = "",
    ) -> None:
        self.coordinator = coordinator
        self.action = action
        self.args = args
        self._attr_name = f"{action.path}{label_suffix}"
        self._attr_unique_id = (
            f"dspremote_action_{slugify(action.path)}_{slugify(str(sorted(args.items())))}"
        )

    async def async_press(self) -> None:
        await self.coordinator.api.run_action(self.action.path, self.args)

