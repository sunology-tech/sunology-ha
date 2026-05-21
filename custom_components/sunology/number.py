"""Number entities for Sunology STOREY configuration."""
from __future__ import annotations

import logging

from homeassistant.components.number import ENTITY_ID_FORMAT, NumberEntity, NumberMode
from homeassistant.const import PERCENTAGE, EntityCategory

from .const import PACKAGE_NAME
from .device import StoreyMaster

_LOGGER = logging.getLogger(PACKAGE_NAME)


def _format_devid_mac(mac: str) -> str:
    """Format a device MAC/ID for use in entity IDs (lowercase with underscores)."""
    if len(mac) == 12:
        return "_".join(mac.lower()[i : i + 2] for i in range(0, 12, 2))
    if "#" in mac:
        return mac.replace("#", "_")
    return mac


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up number entities for the Sunology integration.

    Called once at initial setup, and again on every platform reload triggered
    by the integration when new devices are discovered. The dedup check on
    device_entities prevents the "duplicate unique_id" error on subsequent calls.
    """
    sunology_context = config_entry.runtime_data
    coordinated_devices = sunology_context.sunology_devices_coordinated

    entities: list[NumberEntity] = []
    for cd in coordinated_devices:
        device = cd["device"]
        if not isinstance(device, StoreyMaster):
            continue
        if sunology_context.cloud is None:
            _LOGGER.debug(
                "Skipping minSoc entity for %s (no cloud client configured)",
                device.device_id,
            )
            continue
        # Skip if we've already created a NumberEntity for this device
        # (defends against the platform reload triggered by new device discovery)
        existing = cd.get("device_entities", [])
        if any(isinstance(e, SunologyMinSocNumberEntity) for e in existing):
            _LOGGER.debug(
                "minSoc entity already exists for %s, skipping",
                device.device_id,
            )
            continue
        ent = SunologyMinSocNumberEntity(device, sunology_context, hass)
        cd.setdefault("device_entities", []).append(ent)
        entities.append(ent)
        _LOGGER.info("Added minSoc entity for STOREY %s", device.device_id)

    if entities:
        async_add_entities(entities)
    return True


class SunologyMinSocNumberEntity(NumberEntity):
    """Battery reserve percentage for a STOREY master.

    Read value comes from the local WebSocket productInfo event (already
    parsed into StoreyMaster.min_soc). Write goes through the cloud REST API
    because the local WebSocket silently ignores STOREY config writes.
    """

    _attr_native_min_value = 5
    _attr_native_max_value = 70
    _attr_native_step = 1
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_mode = NumberMode.SLIDER
    _attr_icon = "mdi:battery-arrow-down"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, device, sunology_context, hass):
        """Initialize the entity."""
        self._device = device
        self._sunology_context = sunology_context
        self._hass = hass
        slug = _format_devid_mac(device.device_id)
        self._attr_unique_id = f"minsoc_{slug}".lower()
        self.entity_id = ENTITY_ID_FORMAT.format(f"minsoc_{slug}").lower()
        self._attr_name = f"{device.name} battery reserve"
        self._attr_device_info = device.device_info

    @property
    def native_value(self):
        """Current reserve, read from local WebSocket state."""
        return self._device.min_soc

    @property
    def available(self):
        """Available when we have a cloud UUID and a cloud client."""
        return (
            self._device.cloud_uuid is not None
            and self._sunology_context.cloud is not None
        )

    async def async_set_native_value(self, value):
        """Send the new value to the cloud, which propagates to the gateway."""
        await self._device.async_set_min_soc(
            self._sunology_context.cloud, int(value)
        )
        # Optimistic local update — the gateway will re-emit productInfo within 30s
        # but we don't want the slider to snap back in the meantime.
        self._device.update_min_soc(int(value))
        self.async_write_ha_state()