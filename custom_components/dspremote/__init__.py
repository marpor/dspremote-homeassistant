"""Home Assistant integration for dspremote."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .api import DspremoteApiClient
from .const import CONF_BASE_URL, DOMAIN, PLATFORMS
from .coordinator import DspremoteCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up dspremote from a config entry."""
    api = DspremoteApiClient(entry.data[CONF_BASE_URL], hass)
    coordinator = DspremoteCoordinator(hass, api, entry)
    await coordinator.async_config_entry_first_refresh()
    coordinator._unsub_update_listener = entry.add_update_listener(  # type: ignore[attr-defined]
        _async_options_updated
    )

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(
        entry, [Platform(p) for p in PLATFORMS]
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, [Platform(p) for p in PLATFORMS]
    )
    if unload_ok:
        coordinator: DspremoteCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        unsub = getattr(coordinator, "_unsub_update_listener", None)
        if unsub:
            unsub()
        await coordinator.async_shutdown()
        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN)
    return unload_ok


async def _async_options_updated(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload when options are updated."""
    await hass.config_entries.async_reload(entry.entry_id)

