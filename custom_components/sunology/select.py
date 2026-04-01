""" select for Sunology objects """

import logging
from typing import Any, Mapping

from homeassistant.core import callback
from homeassistant.const import EntityCategory
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers import device_registry
from homeassistant.components.select import SelectEntity, ENTITY_ID_FORMAT
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import FlowWorkingModes, PACKAGE_NAME, DOMAIN as SUNOLOGY_DOMAIN
from .device import (
    Gateway
)

_LOGGER = logging.getLogger(PACKAGE_NAME) 


def _format_devid_mac(mac: str):
    """Format a MAC address to a format that can be used as a device ID."""
    to_test = mac
    if len(to_test) == 12:
        # no : included
        return "_".join(to_test.lower()[i : i + 2] for i in range(0, 12, 2))
    if '#' in to_test:
        return to_test.replace('#', '_')
    return mac


async def async_setup_entry(hass, config_entry, async_add_entities): # pylint: disable=W0613
    """Set up Sunology device based off an entry."""
    sunology_context = config_entry.runtime_data
    coordinated_devices = sunology_context.sunology_devices_coordinated

    known_devices_ids: set[str] = set()

    def _check_device() -> None:
        current_devices_ids = set(coordinated_device['device'].device_id for coordinated_device in coordinated_devices)
        new_devices_ids = current_devices_ids - known_devices_ids
        if new_devices_ids:
            known_devices_ids.update(new_devices_ids)
            entities = []
            for coordinated_device_id in new_devices_ids:
                coordinated_device = next((coordinated_device for coordinated_device in coordinated_devices if coordinated_device['device'].device_id == coordinated_device_id), None)
                device = coordinated_device['device']
                coordinator = coordinated_device['coordinator']
                new_entities = []
                if isinstance(device, Gateway):
                    new_entities.append(SunologFlowWorkingModeSelectEntity(device, hass))

                if not 'device_entities' in coordinated_device: 
                    coordinated_device['device_entities'] = []
                coordinated_device['device_entities'].extend(new_entities)
                entities.extend(new_entities)
            async_add_entities(entities)
    _check_device()
    return True

class SunologFlowWorkingModeSelectEntity(SelectEntity):
    """Represent a pvpower of a  device."""

    def __init__(self, device:SunologyAbstractDevice, hass):
        """Set up SunologPvPowerSensor entity."""
        
        self._device = device
        self._name = device.name
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"flowWorkingMode")}_{_format_devid_mac(device.device_id)}".lower()# pylint: disable=C0301
        self._attr_device_info = device.device_info # For automatic device registration
        self._state = None
        self._hass = hass

    @property
    def entity_category(self):
        return None

    @property
    def hass(self):
        return self._hass

    @hass.setter
    def hass(self, hass):
        pass

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"flowWorkingMode_{_format_devid_mac(self._device.device_id)}".lower()

    @property
    def current_option(self):
        """state property"""
        return self.state

    @property
    def state(self):
        """state property"""
        self._state = self._device.flow_working_mode
        return self._state

    @property
    def options(self):
        """options list property"""
        return [e.name for e in FlowWorkingModes]
    

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        await self._device._set_flowWorkingMode(option)

    @property
    def name(self):
        """ pvP name """
        return f"{self._name} flow working mode"

    @property
    def icon(self):
        """icon getter"""
        return "mdi:finance"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self._device.device_info
