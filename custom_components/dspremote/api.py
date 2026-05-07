"""Async client for the dspremote HTTP/WebSocket API."""

from __future__ import annotations

import math
from collections.abc import AsyncIterator
from contextlib import suppress
from typing import Any

from aiohttp import ClientError, ClientSession, WSMsgType
try:
    from homeassistant.helpers.aiohttp_client import async_get_clientsession
except Exception:  # pragma: no cover - headless test fallback without HA install
    async_get_clientsession = None  # type: ignore[assignment]

try:
    from homeassistant.core import HomeAssistant
except Exception:  # pragma: no cover - lets tests run without HA installed
    HomeAssistant = Any  # type: ignore[misc,assignment]


def _seq_for_ws_pong(seq: object) -> int | float | None:
    """Return seq for a JSON pong reply, or None if invalid (matches web UI / desktop WS contract)."""
    if isinstance(seq, bool):
        return None
    if isinstance(seq, int):
        return seq
    if isinstance(seq, float) and math.isfinite(seq):
        return seq
    return None


class DspremoteApiClient:
    """Small client for dspremote endpoints."""

    def __init__(
        self,
        base_url: str,
        hass: HomeAssistant | None = None,
        session: ClientSession | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._owns_session = False
        if session is not None:
            self._session = session
        elif hass is not None:
            if async_get_clientsession is None:
                raise RuntimeError("Home Assistant aiohttp client helper is unavailable")
            self._session = async_get_clientsession(hass)
            self._owns_session = False
        else:
            self._session = ClientSession()
            self._owns_session = True

    async def async_close(self) -> None:
        """Close owned sessions used by headless tests/CLIs."""
        if self._owns_session and not self._session.closed:
            with suppress(Exception):
                await self._session.close()

    async def discovery(self) -> dict[str, Any]:
        return await self._get_json("/v1/discovery")

    async def fields(self) -> dict[str, Any]:
        return await self._get_json("/v1/fields")

    async def read_prefix(self, prefix: str) -> dict[str, Any]:
        payload = await self._post_json("/v1/read-prefixes", {"prefix": prefix})
        return payload.get("values", {})

    async def write_value(self, path: str, value: Any) -> dict[str, Any]:
        return await self._post_json("/v1/write", {"path": path, "value": value})

    async def run_action(self, path: str, args: dict[str, Any] | None = None) -> dict[str, Any]:
        return await self._post_json("/v1/action", {"path": path, "args": args or {}})

    async def subscribe_root(self) -> AsyncIterator[dict[str, Any]]:
        ws_url = self._base_url.replace("http://", "ws://").replace("https://", "wss://")
        async with self._session.ws_connect(f"{ws_url}/v1/stream", heartbeat=30) as ws:
            await ws.receive_json()  # hello
            await ws.send_json({"op": "subscribe", "path": "/"})
            await ws.receive_json()  # subAck
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    payload = msg.json()
                    if payload.get("type") == "ping":
                        pong_seq = _seq_for_ws_pong(payload.get("seq"))
                        if pong_seq is not None:
                            await ws.send_json({"type": "pong", "seq": pong_seq})
                        continue
                    yield payload
                elif msg.type in (WSMsgType.ERROR, WSMsgType.CLOSE, WSMsgType.CLOSED):
                    break

    async def _get_json(self, path: str) -> dict[str, Any]:
        try:
            response = await self._session.get(f"{self._base_url}{path}")
            response.raise_for_status()
            return await response.json()
        except ClientError as err:
            raise RuntimeError(str(err)) from err

    async def _post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            response = await self._session.post(f"{self._base_url}{path}", json=payload)
            response.raise_for_status()
            return await response.json()
        except ClientError as err:
            raise RuntimeError(str(err)) from err

