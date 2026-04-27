"""Config flow for dspremote."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SSL
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_BASE_URL,
    CONF_PREFIX,
    CONF_SELECTED_PATHS,
    CONF_USE_WEBSOCKET,
    DEFAULT_PREFIX,
    DOMAIN,
)


def _parse_selected_paths(raw: str) -> list[str]:
    parts = raw.replace(",", "\n").splitlines()
    return [part.strip() for part in parts if part.strip()]


class DspremoteConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for dspremote."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            scheme = "https" if user_input[CONF_SSL] else "http"
            base_url = f"{scheme}://{user_input[CONF_HOST]}:{user_input[CONF_PORT]}"
            await self.async_set_unique_id(base_url.lower())
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=f"dspremote ({user_input[CONF_HOST]})",
                data={
                    CONF_BASE_URL: base_url,
                    CONF_USE_WEBSOCKET: user_input[CONF_USE_WEBSOCKET],
                    CONF_PREFIX: user_input[CONF_PREFIX].strip() or DEFAULT_PREFIX,
                    CONF_SELECTED_PATHS: _parse_selected_paths(
                        user_input.get(CONF_SELECTED_PATHS, "")
                    ),
                },
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_PORT, default=8787): int,
                vol.Required(CONF_SSL, default=False): bool,
                vol.Required(CONF_USE_WEBSOCKET, default=True): bool,
                vol.Required(CONF_PREFIX, default=DEFAULT_PREFIX): str,
                vol.Optional(CONF_SELECTED_PATHS, default=""): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Options flow; core binds `config_entry` on the instance (HA 2024.12+)."""
        return DspremoteOptionsFlow()


class DspremoteOptionsFlow(config_entries.OptionsFlow):
    """Handle options for dspremote."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(
                title="",
                data={
                    CONF_SELECTED_PATHS: _parse_selected_paths(
                        user_input.get(CONF_SELECTED_PATHS, "")
                    )
                },
            )

        selected_paths = self.config_entry.options.get(
            CONF_SELECTED_PATHS, self.config_entry.data.get(CONF_SELECTED_PATHS, [])
        )
        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_SELECTED_PATHS,
                    default="\n".join(selected_paths),
                ): str
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)

