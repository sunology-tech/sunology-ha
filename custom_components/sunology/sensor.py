""" odometter sensor for GeoRide object """

import logging
from typing import Any, Mapping

from homeassistant.core import callback
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers import device_registry
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
    SolarEventInterface,
    BatteryEventInterface
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
        coordoned_device['device_entities'] = []
        hass.data[SUNOLOGY_DOMAIN]["devices"][device.device_id] = coordinator
        if isinstance(device, SolarEventInterface):
            coordoned_device['device_entities'].append(SunologPvPowerSensorEntity(coordinator, device, hass))
            coordoned_device['device_entities'].append(SunologMiPowerSensorEntity(coordinator, device, hass))

        if isinstance(device, BatteryEventInterface):
            coordoned_device['device_entities'].append(SunologyBatteryPowerSensorEntity(coordinator, device, hass))
            coordoned_device['device_entities'].append(SunologyBatterySocSensorEntity(coordinator, device, hass))
            coordoned_device['device_entities'].append(SunologyBatteryTempSensorEntity(coordinator, device, hass))

        entities.extend(coordoned_device['device_entities'])

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
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"pvP")}_{device_registry.format_mac(device.device_id)}"# pylint: disable=C0301
        self._attr_device_info = device.device_info # For automatic device registration
        self._state = 0
        self._hass = hass

    @property
    def entity_category(self):
        return None

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"pvP_{device_registry.format_mac(self._device.device_id)}"

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

class SunologMiPowerSensorEntity(CoordinatorEntity, SensorEntity):
    """Represent a mipower of a  device."""

    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]],
                 device:SunologyAbstractDevice, hass):
        """Set up SunologMiPowerSensor entity."""
        super().__init__(coordinator)
        self._device = device
        self._name = device.name
        self._unit_of_measurement = "W"
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"miP")}_{device_registry.format_mac(device.device_id)}"# pylint: disable=C0301
        self._state = 0
        self._hass = hass

    @property
    def entity_category(self):
        return None

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"miP_{device_registry.format_mac(self._device.device_id)}"

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
        """ Entity name """
        return f"{self._name} mi Power"

    @property
    def icon(self):
        """icon getter"""
        return "mdi:generator-portable"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self._device.device_info


class SunologyBatteryPowerSensorEntity(CoordinatorEntity, SensorEntity):
    """Represent a mipower of a  device."""

    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]],
                 device:SunologyAbstractDevice, hass):
        """Set up SunologBatteryPowerSensor entity."""
        super().__init__(coordinator)
        self._device = device
        self._name = device.name
        self._unit_of_measurement = "W"
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"batP")}_{device_registry.format_mac(device.device_id)}"# pylint: disable=C0301
        self._state = 0
        self._hass = hass

    @property
    def entity_category(self):
        return None

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"batP_{device_registry.format_mac(self._device.device_id)}"

    @property
    def state(self):
        """state property"""
        batP = self._device.batP
        return batP

    @property
    def unit_of_measurement(self):
        """unit of mesurment property"""
        return self._unit_of_measurement

    @property
    def name(self):
        """ Entity name """
        return f"{self._name} battery Power"

    @property
    def icon(self):
        """icon getter"""
        return "mdi:battery-charging"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self._device.device_info

class SunologyBatterySocSensorEntity(CoordinatorEntity, SensorEntity):
    """Represent a mipower of a  device."""

    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]],
                 device:SunologyAbstractDevice, hass):
        """Set up SunologBatteryPowerSensor entity."""
        super().__init__(coordinator)
        self._device = device
        self._name = device.name
        self._unit_of_measurement = "%"
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"batPct")}_{device_registry.format_mac(device.device_id)}"# pylint: disable=C0301
        self._state = 0
        self._hass = hass

    @property
    def entity_category(self):
        return None

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"batPct_{device_registry.format_mac(self._device.device_id)}"

    @property
    def state(self):
        """state property"""
        batP = self._device.batPct
        return batP

    @property
    def unit_of_measurement(self):
        """unit of mesurment property"""
        return self._unit_of_measurement

    @property
    def name(self):
        """ Entity name """
        return f"{self._name} battery Soc"

    @property
    def icon(self):
        """icon getter"""
        icon = "mdi:battery-alert-variant-outline"
        if self.state < 10:
            icon = "mdi:battery-outline"
        elif self.state < 20:
            icon = "mdi:battery-10"
        elif self.state < 30:
            icon = "mdi:battery-20"
        elif self.state < 40:
            icon = "mdi:battery-30"
        elif self.state < 50:
            icon = "mdi:battery-40"
        elif self.state < 60:
            icon = "mdi:battery-50"
        elif self.state < 70:
            icon = "mdi:battery-60"
        elif self.state < 80:
            icon = "mdi:battery-70"
        elif self.state < 90:
            icon = "mdi:battery-80"
        elif self.state < 100:
            icon = "mdi:battery-90"
        else:
            icon = "mdi:battery"

        return icon
    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self._device.device_info


class SunologyBatteryTempSensorEntity(CoordinatorEntity, SensorEntity):
    """Represent a mipower of a  device."""

    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]],
                 device:SunologyAbstractDevice, hass):
        """Set up SunologBatteryPowerSensor entity."""
        super().__init__(coordinator)
        self._device = device
        self._name = device.name
        self._unit_of_measurement = "°C"
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"batTmp")}_{device_registry.format_mac(device.device_id)}"# pylint: disable=C0301
        self._state = 0
        self._hass = hass

    @property
    def entity_category(self):
        return None

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"batTmp_{device_registry.format_mac(self._device.device_id)}"

    @property
    def state(self):
        """state property"""
        batP = self._device.batTmp
        return batP

    @property
    def unit_of_measurement(self):
        """unit of mesurment property"""
        return self._unit_of_measurement

    @property
    def name(self):
        """ Entity name """
        return f"{self._name} battery Temperature"

    @property
    def icon(self):
        """icon getter"""
        return "mdi:thermometer"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self._device.device_info
