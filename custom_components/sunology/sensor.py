""" odometter sensor for GeoRide object """

import logging
from typing import Any, Mapping

from homeassistant.core import callback
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, ENTITY_ID_FORMAT
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import PACKAGE_NAME, DOMAIN as SUNOLOGY_DOMAIN
from .device import (
    PLAYMax,
    Gateway,
    SunologyAbstractDevice,
    SolarEventInterface
)

_LOGGER = logging.getLogger(PACKAGE_NAME) 


async def async_setup_entry(hass, config_entry, async_add_entities): # pylint: disable=W0613
    """Set up Sunology device based off an entry."""
    sunology_context = hass.data[SUNOLOGY_DOMAIN]["context"]
    coordoned_devices = sunology_context.sunology_devices_coordoned

    entities = []
    for coordoned_device in coordoned_devices:
        device = coordoned_device['device']
        coordinator = coordoned_device['coordinator']
        hass.data[SUNOLOGY_DOMAIN]["devices"][device.unique_id] = coordinator
        if isinstance(device, SolarEventInterface):
            entities.append(SunologPvPowerSensorEntity(coordinator, device, hass))
            entities.append(SunologMiPowerSensorEntity(coordinator, device, hass))

    async_add_entities(entities)

    return True

class SunologPvPowerSensorEntity(CoordinatorEntity, SensorEntity):
    """Represent a pvpower of a  device."""

    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]],
                 device:SunologyAbstractDevice, hass):
        """Set up SunologPvPowerSensor entity."""
        super().__init__(coordinator)
        self._device = device
        self._name = device.name
        self._unit_of_measurement = "W"
        self.entity_id = f"{ENTITY_ID_FORMAT.format('pvP')}.{device.device_id}"# pylint: disable=C0301
        self._attr_device_info = device.device_info # For automatic device registration
        self._state = 0
        self._hass = hass

    @property
    def entity_category(self):
        return None

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"pvP_{self._device.device_id}"

    @property
    def state(self):
        """state property"""
        pvP = self._device.pvP
        return pvP

    @property
    def unit_of_measurement(self):
        """unit of mesurment property"""
        return self._unit_of_measurement

    @property
    def name(self):
        """ pvP name """
        return f"{self._name} pv Power"

    @property
    def icon(self):
        """icon getter"""
        return "mdi:solar-power-variant"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self._device.device_info

    def register(self, hass, entry):
        from homeassistant.helpers import entity_registry as er
        entity_registry = er.async_get(hass)

        entity_registry.async_get_or_create(
            SUNOLOGY_DOMAIN,
            self.platform.platform_name,
            self.unique_id(),

            config_entry_id=entry.entry_id,
            original_name=self.name
        )

class SunologMiPowerSensorEntity(CoordinatorEntity, SensorEntity):
    """Represent a mipower of a  device."""

    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]],
                 device:SunologyAbstractDevice, hass):
        """Set up SunologMiPowerSensor entity."""
        super().__init__(coordinator)
        self._device = device
        self._name = device.name
        self._unit_of_measurement = "W"
        self.entity_id = f"{ENTITY_ID_FORMAT.format('miP')}.{device.device_id}"# pylint: disable=C0301
        self._state = 0
        self._hass = hass

    @property
    def entity_category(self):
        return None

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"pvP_{self._device.device_id}"

    @property
    def state(self):
        """state property"""
        miP = self._device.miP
        return miP

    @property
    def unit_of_measurement(self):
        """unit of mesurment property"""
        return self._unit_of_measurement

    @property
    def name(self):
        """ GeoRide odometer name """
        return f"{self._name} mi Power"

    @property
    def icon(self):
        """icon getter"""
        return "mdi:generator-portable"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self._device.device_info

    def register(self, hass, entry):
        from homeassistant.helpers import entity_registry as er
        entity_registry = er.async_get(hass)

        entity_registry.async_get_or_create(
            SUNOLOGY_DOMAIN,
            self.platform.platform_name,
            self.unique_id(),

            config_entry_id=entry.entry_id,
            original_name=self.name
        )