"""DateTime entities for Sunology STOREY configuration."""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from homeassistant.components.datetime import ENTITY_ID_FORMAT, DateTimeEntity
from homeassistant.const import EntityCategory

from .const import PACKAGE_NAME
from .device import StoreyMaster

_LOGGER = logging.getLogger(PACKAGE_NAME)


def _format_devid_mac(mac: str) -> str:
    """Format a device MAC/ID for use in entity IDs."""
    if len(mac) == 12:
        return "_".join(mac.lower()[i : i + 2] for i in range(0, 12, 2))
    if "#" in mac:
        return mac.replace("#", "_")
    return mac


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up datetime entities for the Sunology integration."""
    sunology_context = config_entry.runtime_data
    coordinated_devices = sunology_context.sunology_devices_coordinated

    entities: list[DateTimeEntity] = []
    for cd in coordinated_devices:
        device = cd["device"]
        if not isinstance(device, StoreyMaster):
            continue
        if sunology_context.cloud is None:
            continue
        existing = cd.get("device_entities", [])
        if any(isinstance(e, SunologyInhibitionTimeoutEntity) for e in existing):
            continue
        ent = SunologyInhibitionTimeoutEntity(device, sunology_context, hass)
        cd.setdefault("device_entities", []).append(ent)
        entities.append(ent)
        _LOGGER.info(
            "Added inhibitionTimeout entity for STOREY %s", device.device_id
        )

    if entities:
        async_add_entities(entities)
    return True


class SunologyInhibitionTimeoutEntity(DateTimeEntity):
    """Pause-until timestamp for a STOREY master.

    A future timestamp puts the battery in pause until that moment (no charge,
    no discharge). A past timestamp means no active pause. Mirrors the
    "Paramétrer la pause" feature of the Sunology mobile app.
    """

    _attr_icon = "mdi:pause-circle-outline"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, device, sunology_context, hass):
        """Initialize the entity."""
        self._device = device
        self._sunology_context = sunology_context
        self._hass = hass
        slug = _format_devid_mac(device.device_id)
        self._attr_unique_id = f"pauseuntil_{slug}".lower()
        self.entity_id = ENTITY_ID_FORMAT.format(f"pauseuntil_{slug}").lower()
        self._attr_name = f"{device.name} pause until"
        self._attr_device_info = device.device_info

    @property
    def native_value(self):
        """Return the inhibition timeout as datetime, or None if not set."""
        ts_ms = self._device.inhibition_timeout_ms
        if ts_ms is None:
            return None
        return datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)

    @property
    def available(self):
        """Available when we have a cloud UUID and a cloud client."""
        return (
            self._device.cloud_uuid is not None
            and self._sunology_context.cloud is not None
        )

    async def async_set_value(self, value: datetime) -> None:
        """Send the new pause-until value to the cloud."""
        await self._device.async_set_inhibition_timeout(
            self._sunology_context.cloud, value
        )
        # Optimistic local update so the entity reflects the change immediately
        self._device.update_inhibition_timeout(int(value.timestamp() * 1000))
        self.async_write_ha_state()