"""Sunology config flow."""

from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import callback
from homeassistant.helpers.service_info import zeroconf

from .cloud import SunologyAuthError, SunologyCloud
from .const import (
    CONF_GATEWAY_HOST,
    CONF_GATEWAY_PORT,
    DOMAIN,
    GATEWAY_DEFAULT_PORT,
    PACKAGE_NAME,
)

_LOGGER = logging.getLogger(PACKAGE_NAME)


def _build_schema(
    host_default: str | None,
    port_default: int,
    username_default: str = "",
    password_default: str = "",
) -> vol.Schema:
    """Build the form schema shared by config and options flows."""
    return vol.Schema({
        vol.Required(CONF_GATEWAY_HOST, default=host_default): vol.All(str),
        vol.Required(CONF_GATEWAY_PORT, default=port_default): vol.All(
            int, vol.Range(min=1, max=65535)
        ),
        # Cloud credentials are optional — only needed to enable write entities
        vol.Optional(CONF_USERNAME, default=username_default): str,
        vol.Optional(CONF_PASSWORD, default=password_default): str,
    })


async def _validate_cloud_credentials(
    hass, username: str, password: str
) -> str | None:
    """Try logging in with the given credentials.

    Returns an error key suitable for the form (``invalid_auth`` or
    ``cloud_unreachable``), or ``None`` if the login succeeded.
    """
    cloud = SunologyCloud(hass, username, password)
    try:
        await cloud.login()
    except SunologyAuthError as err:
        _LOGGER.warning("Sunology cloud login failed: %s", err)
        return "invalid_auth"
    except Exception:  # pylint: disable=broad-except
        _LOGGER.exception("Unexpected Sunology cloud login failure")
        return "cloud_unreachable"
    return None


class SunologyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Sunology config flow."""

    def __init__(self):
        """Initialize the Sunology config flow."""
        self.hostname = None
        self.port = GATEWAY_DEFAULT_PORT

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> "SunologyOptionsFlow":
        """Return the options flow handler."""
        return SunologyOptionsFlow()

    async def async_step_user(self, user_input=None):
        """Handle user-initiated config."""
        errors: dict[str, str] = {}
        if user_input is not None:
            _LOGGER.info("Sunology config user_input received")
            username = user_input.get(CONF_USERNAME, "").strip()
            password = user_input.get(CONF_PASSWORD, "")

            if username and password:
                error = await _validate_cloud_credentials(
                    self.hass, username, password
                )
                if error:
                    errors["base"] = error

            if not errors:
                data = {
                    CONF_GATEWAY_HOST: user_input[CONF_GATEWAY_HOST],
                    CONF_GATEWAY_PORT: user_input[CONF_GATEWAY_PORT],
                }
                if username and password:
                    data[CONF_USERNAME] = username
                    data[CONF_PASSWORD] = password
                return self.async_create_entry(
                    title=user_input[CONF_GATEWAY_HOST], data=data
                )

        return self.async_show_form(
            step_id="user",
            data_schema=_build_schema(self.hostname, self.port),
            errors=errors,
        )

    async def async_step_zeroconf(
        self, discovery_info: zeroconf.ZeroconfServiceInfo
    ):
        """Handle zeroconf discovery."""
        hostname = discovery_info.hostname
        if hostname is None or not hostname.lower().startswith("sunology"):
            return self.async_abort(reason="not_sunology_device")
        if discovery_info.ip_address.version != 4:
            return self.async_abort(reason="not_ipv4_address")

        await self.async_set_unique_id(discovery_info.hostname)
        # NOTE: rest of zeroconf logic preserved as-is from upstream


class SunologyOptionsFlow(config_entries.OptionsFlow):
    """Options flow: update gateway settings or Sunology cloud credentials.

    Lets users change credentials (typical case: password rotation) without
    removing and re-adding the integration. Gateway host/port are also
    editable here for convenience.

    On save, the entry data is updated and the integration is reloaded so
    the new cloud client picks up the new credentials.
    """

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        errors: dict[str, str] = {}
        # self.config_entry is auto-populated by the HA framework (2024.7+)
        data = self.config_entry.data

        if user_input is not None:
            username = user_input.get(CONF_USERNAME, "").strip()
            password = user_input.get(CONF_PASSWORD, "")

            # Re-validate only if credentials are present AND changed.
            # No network round-trip for the no-op or credentials-cleared cases.
            creds_changed = (
                username != data.get(CONF_USERNAME, "")
                or password != data.get(CONF_PASSWORD, "")
            )
            if username and password and creds_changed:
                error = await _validate_cloud_credentials(
                    self.hass, username, password
                )
                if error:
                    errors["base"] = error

            if not errors:
                new_data = {
                    CONF_GATEWAY_HOST: user_input[CONF_GATEWAY_HOST],
                    CONF_GATEWAY_PORT: user_input[CONF_GATEWAY_PORT],
                }
                if username and password:
                    new_data[CONF_USERNAME] = username
                    new_data[CONF_PASSWORD] = password
                # If credentials are cleared, the keys are absent from
                # new_data — which __init__.py already interprets as
                # "no cloud client" (read-only mode).

                changed = self.hass.config_entries.async_update_entry(
                    self.config_entry, data=new_data
                )
                if changed:
                    await self.hass.config_entries.async_reload(
                        self.config_entry.entry_id
                    )
                return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="init",
            data_schema=_build_schema(
                data.get(CONF_GATEWAY_HOST),
                data.get(CONF_GATEWAY_PORT, GATEWAY_DEFAULT_PORT),
                data.get(CONF_USERNAME, ""),
                data.get(CONF_PASSWORD, ""),
            ),
            errors=errors,
        )