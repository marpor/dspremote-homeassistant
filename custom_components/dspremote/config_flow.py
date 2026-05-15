"""Config flow for dspremote."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SSL
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .api import DspremoteApiClient
from .const import (
    CONF_ADDITIONAL_PATH_PATTERNS,
    CONF_BASE_URL,
    CONF_PREFIX,
    CONF_SELECTED_PATHS,
    CONF_USE_WEBSOCKET,
    DEFAULT_PREFIX,
    DOMAIN,
)
from .coordinator import list_field_paths_from_discovery


def _parse_selected_paths(raw: str) -> list[str]:
    parts = raw.replace(",", "\n").splitlines()
    return [part.strip() for part in parts if part.strip()]


def _merge_selected_paths(multi: Any, extra_raw: str) -> list[str]:
    """Combine multi-select list with optional extra patterns (one list per entry)."""
    paths: list[str] = []
    if isinstance(multi, list):
        paths.extend(str(p) for p in multi if isinstance(p, str) and p.strip())
    elif isinstance(multi, str) and multi.strip():
        paths.append(multi.strip())
    paths.extend(_parse_selected_paths(extra_raw))
    seen: set[str] = set()
    out: list[str] = []
    for p in paths:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


def _paths_form_schema(
    available: list[str],
    default_multi: list[str],
    default_extra: str,
) -> vol.Schema:
    fields: dict[vol.Marker, Any] = {}

    if available:
        fields[vol.Optional(CONF_SELECTED_PATHS, default=default_multi)] = (
            selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[{"value": p, "label": p} for p in available],
                    multiple=True,
                    mode=selector.SelectSelectorMode.LIST,
                )
            )
        )
    fields[vol.Optional(CONF_ADDITIONAL_PATH_PATTERNS, default=default_extra)] = (
        selector.TextSelector(selector.TextSelectorConfig(multiline=True))
    )
    return vol.Schema(fields)


class DspremoteConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for dspremote."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Connection parameters."""
        errors: dict[str, str] = {}
        if user_input is not None:
            scheme = "https" if user_input[CONF_SSL] else "http"
            base_url = f"{scheme}://{user_input[CONF_HOST]}:{user_input[CONF_PORT]}"
            await self.async_set_unique_id(base_url.lower())
            self._abort_if_unique_id_configured()
            try:
                client = DspremoteApiClient(base_url, self.hass)
                discovery = await client.discovery()
                self._available_paths = list_field_paths_from_discovery(discovery)
            except Exception:
                errors["base"] = "cannot_connect"
            else:
                self._pending_user = user_input
                return await self.async_step_paths()

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_PORT, default=8787): int,
                vol.Required(CONF_SSL, default=False): bool,
                vol.Required(CONF_USE_WEBSOCKET, default=True): bool,
                vol.Required(CONF_PREFIX, default=DEFAULT_PREFIX): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_paths(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Pick fields from discovery (and optional wildcard patterns)."""
        pending = getattr(self, "_pending_user", None)
        if pending is None:
            return await self.async_step_user()

        if user_input is not None:
            scheme = "https" if pending[CONF_SSL] else "http"
            base_url = f"{scheme}://{pending[CONF_HOST]}:{pending[CONF_PORT]}"
            merged = _merge_selected_paths(
                user_input.get(CONF_SELECTED_PATHS),
                user_input.get(CONF_ADDITIONAL_PATH_PATTERNS, ""),
            )
            return self.async_create_entry(
                title=f"dspremote ({pending[CONF_HOST]})",
                data={
                    CONF_BASE_URL: base_url,
                    CONF_USE_WEBSOCKET: pending[CONF_USE_WEBSOCKET],
                    CONF_PREFIX: pending[CONF_PREFIX].strip() or DEFAULT_PREFIX,
                    CONF_SELECTED_PATHS: merged,
                },
            )

        available = getattr(self, "_available_paths", [])
        schema = _paths_form_schema(available, [], "")
        return self.async_show_form(step_id="paths", data_schema=schema)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Options flow; core binds `config_entry` on the instance (HA 2024.12+)."""
        return DspremoteOptionsFlow()


class DspremoteOptionsFlow(config_entries.OptionsFlowWithReload):
    """Handle options for dspremote.

    Uses OptionsFlowWithReload so the config entry reloads when options change
    (entity set must be rebuilt). Do not combine with entry.add_update_listener
    for the same reload — core schedules reload when options actually change.
    """

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}
        entry = self.config_entry

        if getattr(self, "_available_paths", None) is None:
            base_url = entry.data[CONF_BASE_URL]
            try:
                client = DspremoteApiClient(base_url, self.hass)
                discovery = await client.discovery()
                self._available_paths = list_field_paths_from_discovery(discovery)
            except Exception:
                errors["base"] = "cannot_connect"
                self._available_paths = []

        available = self._available_paths or []
        prev = entry.options.get(
            CONF_SELECTED_PATHS, entry.data.get(CONF_SELECTED_PATHS, [])
        )
        if not isinstance(prev, list):
            prev = []
        available_set = set(available)
        default_multi = [p for p in prev if p in available_set]
        default_extra = "\n".join(p for p in prev if p not in available_set)

        if user_input is not None:
            merged = _merge_selected_paths(
                user_input.get(CONF_SELECTED_PATHS),
                user_input.get(CONF_ADDITIONAL_PATH_PATTERNS, ""),
            )
            return self.async_create_entry(
                title="",
                data={CONF_SELECTED_PATHS: merged},
            )

        schema = _paths_form_schema(available, default_multi, default_extra)
        return self.async_show_form(step_id="init", data_schema=schema, errors=errors)
