"""Button entities for Sunology STOREY quick actions (pause/unpause)."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from homeassistant.components.button import ENTITY_ID_FORMAT, ButtonEntity
from homeassistant.const import EntityCategory

from .const import PACKAGE_NAME
from .device import StoreyMaster

_LOGGER = logging.getLogger(PACKAGE_NAME)

# Pause presets: (slug, label, minutes). 0 = stop the pause.
_PAUSE_PRESETS = [
    ("stop", "stop pause", 0),
    ("30min", "pause 30 min", 30),
    ("1h", "pause 1 h", 60),
    ("4h", "pause 4 h", 240),
]


def _format_devid_mac(mac: str) -> str:
    """Format a device MAC/ID for use in entity IDs."""
    if len(mac) == 12:
        return "_".join(mac.lower()[i : i + 2] for i in range(0, 12, 2))
    if "#" in mac:
        return mac.replace("#", "_")
    return mac


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up button entities for the Sunology integration."""
    sunology_context = config_entry.runtime_data
    coordinated_devices = sunology_context.sunology_devices_coordinated

    entities: list[ButtonEntity] = []
    for cd in coordinated_devices:
        device = cd["device"]
        if not isinstance(device, StoreyMaster):
            continue
        if sunology_context.cloud is None:
            continue
        existing = cd.get("device_entities", [])
        existing_uids = {
            e.unique_id for e in existing if hasattr(e, "unique_id")
        }
        for suffix, label, minutes in _PAUSE_PRESETS:
            slug = _format_devid_mac(device.device_id)
            uid = f"pause_{suffix}_{slug}".lower()
            if uid in existing_uids:
                continue
            ent = SunologyPauseButton(
                device, sunology_context, hass, suffix, label, minutes
            )
            cd.setdefault("device_entities", []).append(ent)
            entities.append(ent)
            _LOGGER.info(
                "Added pause button '%s' for STOREY %s", label, device.device_id
            )

    if entities:
        async_add_entities(entities)
    return True


class SunologyPauseButton(ButtonEntity):
    """One-click action to pause the battery for a preset duration (or stop)."""

    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, device, sunology_context, hass, suffix, label, minutes):
        """Initialize the entity."""
        self._device = device
        self._sunology_context = sunology_context
        self._hass = hass
        self._minutes = minutes
        slug = _format_devid_mac(device.device_id)
        self._attr_unique_id = f"pause_{suffix}_{slug}".lower()
        self.entity_id = ENTITY_ID_FORMAT.format(f"pause_{suffix}_{slug}").lower()
        self._attr_name = f"{device.name} {label}"
        self._attr_icon = (
            "mdi:play-circle-outline" if minutes == 0 else "mdi:pause-circle-outline"
        )
        self._attr_device_info = device.device_info

    @property
    def available(self):
        """Available when we have a cloud UUID and a cloud client."""
        return (
            self._device.cloud_uuid is not None
            and self._sunology_context.cloud is not None
        )

    async def async_press(self) -> None:
        """Apply the pause or clear it via the cloud."""
        if self._minutes == 0:
            # Clear pause: send a past datetime
            target = datetime(2020, 1, 1, tzinfo=timezone.utc)
        else:
            target = datetime.now(timezone.utc) + timedelta(minutes=self._minutes)
        await self._device.async_set_inhibition_timeout(
            self._sunology_context.cloud, target
        )
        # Optimistic local update
        self._device.update_inhibition_timeout(int(target.timestamp() * 1000))
        _LOGGER.info(
            "Pause action '%s' applied to STOREY %s (target=%s)",
            self._attr_name,
            self._device.device_id,
            target.isoformat(),
        )