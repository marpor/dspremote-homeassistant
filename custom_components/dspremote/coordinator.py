"""Coordinator for dspremote state and entity metadata."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
import fnmatch
from itertools import product
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import DspremoteApiClient
from .const import (
    CONF_PREFIX,
    CONF_SELECTED_PATHS,
    CONF_USE_WEBSOCKET,
    DEFAULT_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class FieldDescriptor:
    path: str
    template_path: str
    value_type: str
    read_only: bool
    unit: str | None
    range_spec: dict[str, Any] | None
    enum_values: list[str]


@dataclass(frozen=True, slots=True)
class ActionDescriptor:
    path: str
    has_args: bool
    preset_slots: list[int]


class DspremoteCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Manage dspremote reads, writes, and push updates."""

    def __init__(self, hass, api: DspremoteApiClient, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="dspremote",
            update_interval=DEFAULT_SCAN_INTERVAL,
            config_entry=entry,
        )
        self.api = api
        self.entry = entry
        self.fields: list[FieldDescriptor] = []
        self.actions: list[ActionDescriptor] = []
        self._ws_task = None

    async def _async_update_data(self) -> dict[str, Any]:
        """Poll values from the API."""
        prefix = self.entry.data.get(CONF_PREFIX, "/")
        try:
            if not self.fields:
                await self._bootstrap_metadata()
            values = await self.api.read_prefix(prefix)
            if self._ws_task is None and self.entry.data.get(CONF_USE_WEBSOCKET, True):
                self._ws_task = self.hass.async_create_task(self._ws_loop())
            return values
        except Exception as err:
            raise UpdateFailed(str(err)) from err

    async def async_shutdown(self) -> None:
        """Clean up background tasks."""
        if self._ws_task:
            self._ws_task.cancel()
            self._ws_task = None

    def selected_patterns(self) -> list[str]:
        """Return configured field path patterns."""
        patterns = self.entry.options.get(
            CONF_SELECTED_PATHS, self.entry.data.get(CONF_SELECTED_PATHS, [])
        )
        return [pattern for pattern in patterns if pattern]

    def is_field_selected(self, path: str) -> bool:
        """Check if a field path is enabled by user selection."""
        patterns = self.selected_patterns()
        if not patterns:
            return False
        return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)

    async def _bootstrap_metadata(self) -> None:
        discovery = await self.api.discovery()
        action_templates: dict[str, dict[str, Any]] = {}
        _collect_actions_from_nodes(discovery, action_templates)
        self.fields = _collect_fields(discovery)
        self.actions = _collect_actions(action_templates)

    async def _ws_loop(self) -> None:
        """Subscribe to root deltas and merge into coordinator data."""
        while True:
            try:
                async for message in self.api.subscribe_root():
                    if message.get("type") != "deltas":
                        continue
                    values = message.get("values")
                    if not isinstance(values, dict):
                        continue
                    merged = dict(self.data or {})
                    merged.update(values)
                    self.async_set_updated_data(merged)
            except Exception as err:  # pragma: no cover - network reconnect path
                _LOGGER.warning("websocket reconnect after error: %s", err)
                await asyncio.sleep(5)


def list_field_paths_from_discovery(discovery: dict[str, Any]) -> list[str]:
    """Concrete field paths from discovery (for config/options UI)."""
    return [d.path for d in _collect_fields(discovery)]


def _collect_actions_from_nodes(
    node: dict[str, Any],
    action_templates: dict[str, dict[str, Any]],
) -> None:
    path = node.get("path")
    node_kind = node.get("nodeKind")
    if isinstance(path, str) and node_kind == "Action":
        action_templates[path] = node
    for child in node.get("children", []):
        if isinstance(child, dict):
            _collect_actions_from_nodes(child, action_templates)


def _collect_fields(discovery: dict[str, Any]) -> list[FieldDescriptor]:
    out: list[FieldDescriptor] = []

    def walk(node: dict[str, Any], indices: list[dict[str, Any]]) -> None:
        path = node.get("path")
        next_indices = indices
        index = node.get("index")
        if isinstance(index, dict):
            next_indices = [*indices, index]
        if isinstance(path, str) and node.get("nodeKind") == "Field":
            for combo in _index_combinations(next_indices):
                concrete = path
                for key, value in combo.items():
                    concrete = concrete.replace(f"{{{key}}}", str(value))
                out.append(_descriptor_from_template(concrete, path, node))
        for child in node.get("children", []):
            if isinstance(child, dict):
                walk(child, next_indices)

    walk(discovery, [])
    out.sort(key=lambda item: item.path)
    return out


def _collect_actions(action_templates: dict[str, dict[str, Any]]) -> list[ActionDescriptor]:
    out: list[ActionDescriptor] = []
    for path, node in action_templates.items():
        args = node.get("args", {})
        preset_slots: list[int] = []
        if isinstance(args, dict):
            preset_schema = args.get("preset")
            if isinstance(preset_schema, dict):
                range_spec = preset_schema.get("range")
                if isinstance(range_spec, dict) and "min" in range_spec and "max" in range_spec:
                    min_slot = int(range_spec["min"])
                    max_slot = int(range_spec["max"])
                    if min_slot <= max_slot:
                        preset_slots = list(range(min_slot, max_slot + 1))
        out.append(ActionDescriptor(path=path, has_args=bool(args), preset_slots=preset_slots))
    out.sort(key=lambda item: item.path)
    return out


def _descriptor_from_template(
    concrete_path: str, template_path: str, node: dict[str, Any]
) -> FieldDescriptor:
    values = node.get("values")
    enum_values: list[str] = []
    range_spec = None
    if isinstance(values, list):
        enum_values = [row["id"] for row in values if isinstance(row, dict) and "id" in row]
    elif isinstance(values, dict):
        range_spec = values
    return FieldDescriptor(
        path=concrete_path,
        template_path=template_path,
        value_type=node.get("type", ""),
        read_only=bool(node.get("readOnly", False)),
        unit=node.get("unit"),
        range_spec=range_spec,
        enum_values=enum_values,
    )


def _index_combinations(indices: list[dict[str, Any]]) -> list[dict[str, int]]:
    if not indices:
        return [{}]
    names = [idx["name"] for idx in indices]
    value_ranges = [range(int(idx["min"]), int(idx["max"]) + 1) for idx in indices]
    return [dict(zip(names, values, strict=True)) for values in product(*value_ranges)]

