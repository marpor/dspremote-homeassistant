"""Shared entity base classes."""

from __future__ import annotations

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import DspremoteCoordinator, FieldDescriptor


def _slug(path: str) -> str:
    return (
        path.strip("/")
        .replace("/", "_")
        .replace("{", "")
        .replace("}", "")
        .replace("-", "_")
    )


class DspremoteFieldEntity(CoordinatorEntity[DspremoteCoordinator]):
    """Common behavior for field entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: DspremoteCoordinator, descriptor: FieldDescriptor) -> None:
        super().__init__(coordinator)
        self.descriptor = descriptor
        self._attr_unique_id = f"dspremote_{_slug(descriptor.path)}"
        self._attr_name = descriptor.path

    @property
    def native_value(self):
        return (self.coordinator.data or {}).get(self.descriptor.path)

