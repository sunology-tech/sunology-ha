"""Sunology cloud REST API client.

The local WebSocket on port 20199 only accepts a tiny set of write commands
(openNetwork, flowConfig). All STOREY-level configuration (minSoc,
inhibitionTimeout, workingMode) must go through the cloud backend at
backend-mobile.stream.sunology.eu, which then relays to the gateway.

The cloud session cookie issued by /api/login-post has a Max-Age of ~400 days,
so we authenticate once at setup and reuse the session indefinitely. On a 401
we re-authenticate transparently.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import PACKAGE_NAME

_LOGGER = logging.getLogger(f"{PACKAGE_NAME}-cloud")

CLOUD_BASE_URL = "https://backend-mobile.stream.sunology.eu"

# Past timestamp used to clear inhibitionTimeout (the API uses "any past date" = no pause)
_INHIBITION_CLEAR_ISO = "2020-01-01T00:00:00.000Z"


class SunologyCloudError(Exception):
    """Base exception for Sunology cloud errors."""


class SunologyAuthError(SunologyCloudError):
    """Authentication failure (wrong credentials, or session permanently invalid)."""


class SunologyCloud:
    """Async client for the Sunology cloud REST API."""

    def __init__(self, hass: HomeAssistant, username: str, password: str) -> None:
        self._hass = hass
        self._username = username
        self._password = password
        self._session = async_get_clientsession(hass)
        self._cookies: dict[str, str] | None = None

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "User-Agent": "SunoStream/2.0",
            "App-Version": "3.1.3",
            "Origin": "http://localhost",
            "Referer": "http://localhost/",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
        }

    async def login(self) -> None:
        """POST credentials, capture the SESSION cookie."""
        url = f"{CLOUD_BASE_URL}/api/login-post"
        async with self._session.post(
            url,
            json={"username": self._username, "password": self._password},
            headers=self._headers,
        ) as resp:
            if resp.status != 204:
                text = await resp.text()
                raise SunologyAuthError(
                    f"Login failed: HTTP {resp.status} — {text[:200]}"
                )
            self._cookies = {k: v.value for k, v in resp.cookies.items()}
            if "SESSION" not in self._cookies:
                raise SunologyAuthError(
                    "Login succeeded but no SESSION cookie was returned"
                )
            _LOGGER.info("Authenticated to Sunology cloud as %s", self._username)

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict | None = None,
        _retry: bool = True,
    ) -> Any:
        """Authenticated request, auto-relogin once on 401."""
        if self._cookies is None:
            await self.login()
        url = f"{CLOUD_BASE_URL}{path}"
        async with self._session.request(
            method,
            url,
            json=json,
            headers=self._headers,
            cookies=self._cookies,
        ) as resp:
            if resp.status == 401 and _retry:
                _LOGGER.info("Cloud session rejected (401), re-authenticating")
                self._cookies = None
                await self.login()
                return await self._request(method, path, json=json, _retry=False)
            if resp.status >= 400:
                text = await resp.text()
                raise SunologyCloudError(
                    f"{method} {path} → HTTP {resp.status}: {text[:200]}"
                )
            if resp.status == 204:
                return None
            return await resp.json()

    async def list_devices(self) -> list[dict]:
        """List PLAYs and STOREYs for this account.

        Each item contains: id (cloud UUID), serialNumber (local MAC for STOREY,
        manufacturer serial for PLAY), type, workingMode, connectedPacks,
        inhibitionTimeout. Note: minSoc is NOT in this payload — read it from
        the local WebSocket productInfo event instead.
        """
        return await self._request("GET", "/api/devices/stations-and-storages")

    async def patch_storey(
        self,
        storey_uuid: str,
        *,
        min_soc: int,
        working_mode: str,
        inhibition_timeout: datetime | None,
        name: str = "",
    ) -> dict:
        """Update a STOREY's full configuration.

        The /api/storage-battery/{uuid} endpoint behaves like a PUT despite the
        PATCH method — all fields must be present. Callers should pass the
        current values (typically read from the local WebSocket) for the fields
        they don't want to change.

        Args:
            storey_uuid: cloud UUID of the STOREY (from list_devices).
            min_soc: battery reserve percentage (5-70).
            working_mode: e.g. "HUB_REMOTE". Other known values: TBD.
            inhibition_timeout: datetime (UTC) until which the battery is
                paused, or None to clear the pause.
            name: storey display name (rarely set, "" is fine).

        Returns:
            The server's response body (echoes the new state).
        """
        if not 5 <= min_soc <= 70:
            raise ValueError(f"min_soc must be in [5, 70], got {min_soc}")

        if inhibition_timeout is None:
            inhibition_iso = _INHIBITION_CLEAR_ISO
        else:
            inhibition_iso = inhibition_timeout.astimezone(timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%S.000Z"
            )

        body = {
            "id": storey_uuid,
            "name": name,
            "workingMode": working_mode,
            "minSoc": str(min_soc),  # API expects string in request, returns int
            "inhibitionTimeout": inhibition_iso,
        }
        return await self._request(
            "PATCH", f"/api/storage-battery/{storey_uuid}", json=body
        )