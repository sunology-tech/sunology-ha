""" sensor for Sunology objects """

import logging
from typing import Any, Mapping

from homeassistant.core import callback
from homeassistant.const import EntityCategory
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers import device_registry
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass, ENTITY_ID_FORMAT
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import SmartMeterPhase, SmartMeterTarifIndex, PACKAGE_NAME, DOMAIN as SUNOLOGY_DOMAIN
from .device import (
    PLAYMax,
    Gateway,
    StoreyMaster,
    SunologyAbstractDevice,
    SolarEventInterface,
    BatteryEventInterface,
    SmartMeter_3P,
    LinkyTransmitter
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
        
        if isinstance(device, StoreyMaster):
            coordoned_device['device_entities'].append(SunologyBatteryMasterSocSensorEntity(coordinator, device, hass))
            coordoned_device['device_entities'].append(SunologyBatteryMasterPowerSensorEntity(coordinator, device, hass))
        
        if isinstance(device, SmartMeter_3P):
            coordoned_device['device_entities'].append(SunologyElectricalDataSensorEntity_Power(coordinator, device,  SmartMeterPhase.ALL, hass))
            coordoned_device['device_entities'].append(SunologyTotalExportSensorEntity(coordinator, device,  SmartMeterPhase.ALL, hass))
            coordoned_device['device_entities'].append(SunologyTotalImportSensorEntity(coordinator, device,  SmartMeterPhase.ALL, hass))
            coordoned_device['device_entities'].append(SunologyElectricalDataSensorEntity_Power(coordinator, device,  SmartMeterPhase.PHASE_1, hass))
            coordoned_device['device_entities'].append(SunologyTotalExportSensorEntity(coordinator, device,  SmartMeterPhase.PHASE_1, hass))
            coordoned_device['device_entities'].append(SunologyTotalImportSensorEntity(coordinator, device,  SmartMeterPhase.PHASE_1, hass))
            coordoned_device['device_entities'].append(SunologyElectricalDataSensorEntity_Power(coordinator, device,  SmartMeterPhase.PHASE_2, hass))
            coordoned_device['device_entities'].append(SunologyTotalExportSensorEntity(coordinator, device,  SmartMeterPhase.PHASE_2, hass))
            coordoned_device['device_entities'].append(SunologyTotalImportSensorEntity(coordinator, device,  SmartMeterPhase.PHASE_2, hass))
            coordoned_device['device_entities'].append(SunologyElectricalDataSensorEntity_Power(coordinator, device,  SmartMeterPhase.PHASE_3, hass))
            coordoned_device['device_entities'].append(SunologyTotalExportSensorEntity(coordinator, device,  SmartMeterPhase.PHASE_3, hass))
            coordoned_device['device_entities'].append(SunologyTotalImportSensorEntity(coordinator, device,  SmartMeterPhase.PHASE_3, hass))
            coordoned_device['device_entities'].append(SunologyElectricityFrequencySensorEntity(coordinator, device, hass))
        if isinstance(device, LinkyTransmitter):
            coordoned_device['device_entities'].append(SunologyApparentPowerImportSensorEntity(coordinator, device, hass))
            coordoned_device['device_entities'].append(SunologyApparentPowerExportSensorEntity(coordinator, device, hass))
            coordoned_device['device_entities'].append(SunologyTotalExportSensorEntity(coordinator, device,  SmartMeterPhase.ALL, hass))
            coordoned_device['device_entities'].append(SunologyTotalImportSensorEntity(coordinator, device,  SmartMeterPhase.ALL, hass))
            coordoned_device['device_entities'].append(SunologyImportSensorEntity_PeriodIndex(coordinator, device,  SmartMeterTarifIndex.INDEX_1, hass))
            coordoned_device['device_entities'].append(SunologyImportSensorEntity_PeriodIndex(coordinator, device,  SmartMeterTarifIndex.INDEX_2, hass))
            coordoned_device['device_entities'].append(SunologyImportSensorEntity_PeriodIndex(coordinator, device,  SmartMeterTarifIndex.INDEX_3, hass))
            coordoned_device['device_entities'].append(SunologyImportSensorEntity_PeriodIndex(coordinator, device,  SmartMeterTarifIndex.INDEX_4, hass))
            coordoned_device['device_entities'].append(SunologyImportSensorEntity_PeriodIndex(coordinator, device,  SmartMeterTarifIndex.INDEX_5, hass))
            coordoned_device['device_entities'].append(SunologyImportSensorEntity_PeriodIndex(coordinator, device,  SmartMeterTarifIndex.INDEX_6, hass))
            coordoned_device['device_entities'].append(SunologyImportSensorEntity_PeriodIndex(coordinator, device,  SmartMeterTarifIndex.INDEX_7, hass))
            coordoned_device['device_entities'].append(SunologyImportSensorEntity_PeriodIndex(coordinator, device,  SmartMeterTarifIndex.INDEX_8, hass))
            coordoned_device['device_entities'].append(SunologyImportSensorEntity_PeriodIndex(coordinator, device,  SmartMeterTarifIndex.INDEX_9, hass))
            coordoned_device['device_entities'].append(SunologyImportSensorEntity_PeriodIndex(coordinator, device,  SmartMeterTarifIndex.INDEX_10, hass))

        coordoned_device['device_entities'].append(SunologyRssiSensorEntity(coordinator, device, hass))


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
    
    @property
    def device_class(self):
        """ Entity device_class """
        return SensorDeviceClass.POWER

    @property
    def state_class(self):
        """ Entity state_class """
        return SensorStateClass.MEASUREMENT

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
    
    @property
    def device_class(self):
        """ Entity device_class """
        return SensorDeviceClass.POWER

    @property
    def state_class(self):
        """ Entity state_class """
        return SensorStateClass.MEASUREMENT


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
    
    @property
    def device_class(self):
        """ Entity device_class """
        return SensorDeviceClass.POWER

    @property
    def state_class(self):
        """ Entity state_class """
        return SensorStateClass.MEASUREMENT

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
    
    @property
    def device_class(self):
        """ Entity device_class """
        return SensorDeviceClass.BATTERY

class SunologyBatteryMasterSocSensorEntity(CoordinatorEntity, SensorEntity):
    """Represent a mipower of a  device."""

    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]],
                 device:SunologyAbstractDevice, hass):
        """Set up SunologyBatteryMasterSocSensorEntity entity."""
        super().__init__(coordinator)
        self._device = device
        self._name = device.name
        self._unit_of_measurement = "%"
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"materPct")}_{device_registry.format_mac(device.device_id)}"# pylint: disable=C0301
        self._state = 0
        self._hass = hass

    @property
    def entity_category(self):
        return None

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"materPct_{device_registry.format_mac(self._device.device_id)}"

    @property
    def state(self):
        """state property"""
        percent = self._device.percent
        return percent

    @property
    def unit_of_measurement(self):
        """unit of mesurment property"""
        return self._unit_of_measurement

    @property
    def name(self):
        """ Entity name """
        return f"{self._name} battery master Soc"

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
    
    @property
    def device_class(self):
        """ Entity device_class """
        return SensorDeviceClass.BATTERY

class SunologyBatteryMasterPowerSensorEntity(CoordinatorEntity, SensorEntity):
    """Represent a mipower of a  device."""

    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]],
                 device:SunologyAbstractDevice, hass):
        """Set up SunologBatteryPowerSensor entity."""
        super().__init__(coordinator)
        self._device = device
        self._name = device.name
        self._unit_of_measurement = "W"
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"masterP")}_{device_registry.format_mac(device.device_id)}"# pylint: disable=C0301
        self._state = 0
        self._hass = hass

    @property
    def entity_category(self):
        return None

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"masterP_{device_registry.format_mac(self._device.device_id)}"

    @property
    def state(self):
        """state property"""
        power = self._device.power
        return power

    @property
    def unit_of_measurement(self):
        """unit of mesurment property"""
        return self._unit_of_measurement

    @property
    def name(self):
        """ Entity name """
        return f"{self._name} battery master Power"

    @property
    def icon(self):
        """icon getter"""
        return "mdi:battery-charging"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self._device.device_info
    
    @property
    def device_class(self):
        """ Entity device_class """
        return SensorDeviceClass.POWER

    @property
    def state_class(self):
        """ Entity state_class """
        return SensorStateClass.MEASUREMENT


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
    
    @property
    def device_class(self):
        """ Entity device_class """
        return SensorDeviceClass.TEMPERATURE

    @property
    def state_class(self):
        """ Entity state_class """
        return SensorStateClass.MEASUREMENT

class SunologyBatteryMasterPowerSensorEntity(CoordinatorEntity, SensorEntity):
    """Represent a mipower of a  device."""

    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]],
                 device:SunologyAbstractDevice, hass):
        """Set up SunologBatteryPowerSensor entity."""
        super().__init__(coordinator)
        self._device = device
        self._name = device.name
        self._unit_of_measurement = "W"
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"masterP")}_{device_registry.format_mac(device.device_id)}"# pylint: disable=C0301
        self._state = 0
        self._hass = hass

    @property
    def entity_category(self):
        return None

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"masterP_{device_registry.format_mac(self._device.device_id)}"

    @property
    def state(self):
        """state property"""
        power = self._device.power
        return power

    @property
    def unit_of_measurement(self):
        """unit of mesurment property"""
        return self._unit_of_measurement

    @property
    def name(self):
        """ Entity name """
        return f"{self._name} battery master Power"

    @property
    def icon(self):
        """icon getter"""
        return "mdi:battery-charging"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self._device.device_info
    
    @property
    def device_class(self):
        """ Entity device_class """
        return SensorDeviceClass.POWER

    @property
    def state_class(self):
        """ Entity state_class """
        return SensorStateClass.MEASUREMENT


class SunologyElectricalDataSensorEntity_Power(CoordinatorEntity, SensorEntity):
    """Represent a mipower of a  device."""

    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]],
                 device:SunologyAbstractDevice, phase:SmartMeterPhase, hass):
        """Set up SunologBatteryPowerSensor entity."""
        super().__init__(coordinator)
        self._device = device
        self._name = device.name
        self._unit_of_measurement = "W"
        self._phase = phase
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"edPower")}_{self._phase}_{device_registry.format_mac(device.device_id)}"# pylint: disable=C0301
        self._state = 0
        self._hass = hass
    
    @property
    def extra_state_attributes(self):
        return {
            "current": self._device.electrical_data[self._phase].current,
            "voltage": self._device.electrical_data[self._phase].voltage,
            "power_factor": self._device.electrical_data[self._phase].power_factor
        }

    @property
    def entity_category(self):
        return None

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"power_{self._phase}_{device_registry.format_mac(self._device.device_id)}"

    @property
    def state(self):
        """state property"""
        edPower = self._device.electrical_data[self._phase].power
        return edPower

    @property
    def unit_of_measurement(self):
        """unit of mesurment property"""
        return self._unit_of_measurement

    @property
    def name(self):
        """ Entity name """
        return f"{self._name} {self._phase} electrical data Power"

    @property
    def icon(self):
        """icon getter"""
        return "mdi:transmission-tower"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self._device.device_info
    
    @property
    def device_class(self):
        """ Entity device_class """
        return SensorDeviceClass.POWER

    @property
    def state_class(self):
        """ Entity state_class """
        return SensorStateClass.MEASUREMENT

class SunologyTotalExportSensorEntity(CoordinatorEntity, SensorEntity):
    """Represent energy surplus exported (energy produced) by a smart metter."""

    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]],
                 device:SunologyAbstractDevice, phase:SmartMeterPhase, hass):
        """Set up SunologyTotalExportSensorEntity entity."""
        super().__init__(coordinator)
        self._device = device
        self._name = device.name
        self._unit_of_measurement = "Wh"
        self._phase = phase
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"total_export")}_{self._phase}_{device_registry.format_mac(device.device_id)}"# pylint: disable=C0301
        self._state = 0
        self._hass = hass

    @property
    def entity_category(self):
        return None

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"total_export_{self._phase}_{device_registry.format_mac(self._device.device_id)}"

    @property
    def state(self):
        """state property"""
        prod_tot = 0
        if isinstance(self._device, SmartMeter_3P):
            prod_tot = self._device.electrical_data[self._phase].prod_tot
        elif isinstance(self._device, LinkyTransmitter):
            prod_tot = self._device.indexes_erl.energy_produced_total
        return prod_tot

    @property
    def unit_of_measurement(self):
        """unit of mesurment property"""
        return self._unit_of_measurement

    @property
    def name(self):
        """ Entity name """
        return f"{self._name} {self._phase} electrical data Total export"

    @property
    def icon(self):
        """icon getter"""
        return "mdi:transmission-tower-import"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self._device.device_info
    
    @property
    def device_class(self):
        """ Entity device_class """
        return SensorDeviceClass.ENERGY

    @property
    def state_class(self):
        """ Entity state_class """
        return SensorStateClass.TOTAL_INCREASING

class SunologyTotalImportSensorEntity(CoordinatorEntity, SensorEntity):
    """Represent energy imported (energy consumed) by a smart metter."""

    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]],
                 device:SunologyAbstractDevice, phase:SmartMeterPhase, hass):
        """Set up SunologyTotalImportSensorEntity entity."""
        super().__init__(coordinator)
        self._device = device
        self._name = device.name
        self._unit_of_measurement = "Wh"
        self._phase = phase
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"total_import")}_{self._phase}_{device_registry.format_mac(device.device_id)}"# pylint: disable=C0301
        self._state = 0
        self._hass = hass

    @property
    def entity_category(self):
        return None

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"total_import_{self._phase}_{device_registry.format_mac(self._device.device_id)}"

    @property
    def state(self):
        """state property"""
        conso_tot = 0
        if isinstance(self._device, SmartMeter_3P):
            conso_tot = self._device.electrical_data[self._phase].conso_tot
        elif isinstance(self._device, LinkyTransmitter):
            conso_tot = self._device.indexes_erl.energy_consumed_total
        return conso_tot

    @property
    def unit_of_measurement(self):
        """unit of mesurment property"""
        return self._unit_of_measurement

    @property
    def name(self):
        """ Entity name """
        return f"{self._name} {self._phase} electrical data Total import"

    @property
    def icon(self):
        """icon getter"""
        return "mdi:transmission-tower-export"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self._device.device_info
    
    @property
    def device_class(self):
        """ Entity device_class """
        return SensorDeviceClass.ENERGY

    @property
    def state_class(self):
        """ Entity state_class """
        return SensorStateClass.TOTAL_INCREASING

class SunologyImportSensorEntity_PeriodIndex(CoordinatorEntity, SensorEntity):
    """Represent energy imported (energy consumed) by a smart metter."""

    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]],
                 device:SunologyAbstractDevice, tarif_index: SmartMeterTarifIndex, hass):
        """Set up SunologyTotalImportSensorEntity entity."""
        super().__init__(coordinator)
        self._device = device
        self._name = device.name
        self._unit_of_measurement = "Wh"
        self._tarif_index = tarif_index
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"import_on_period")}_{self._tarif_index}_{device_registry.format_mac(device.device_id)}"# pylint: disable=C0301
        self._state = 0
        self._hass = hass
    @property
    def entity_category(self):
        return None

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"import_on_period_{self._tarif_index}_{device_registry.format_mac(self._device.device_id)}"

    @property
    def state(self):
        """state property"""
        conso_tot = self._device.indexes_erl.energy_consumed_indexed[self._tarif_index]
        return conso_tot

    @property
    def unit_of_measurement(self):
        """unit of mesurment property"""
        return self._unit_of_measurement

    @property
    def name(self):
        """ Entity name """
        return f"{self._name} electrical data import on {self._tarif_index}"

    @property
    def icon(self):
        """icon getter"""
        return "mdi:lightning-bolt-outline"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self._device.device_info
    
    @property
    def device_class(self):
        """ Entity device_class """
        return SensorDeviceClass.ENERGY

    @property
    def state_class(self):
        """ Entity state_class """
        return SensorStateClass.TOTAL_INCREASING

class SunologyElectricityFrequencySensorEntity(CoordinatorEntity, SensorEntity):
    """Represent a mipower of a  device."""

    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]],
                 device:SunologyAbstractDevice, hass):
        """Set up SunologBatteryPowerSensor entity."""
        super().__init__(coordinator)
        self._device = device
        self._name = device.name
        self._unit_of_measurement = "Hz"
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"frequency")}_{device_registry.format_mac(device.device_id)}"# pylint: disable=C0301
        self._state = 0
        self._hass = hass

    @property
    def entity_category(self):
        return None

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"frequency_{device_registry.format_mac(self._device.device_id)}"

    @property
    def state(self):
        """state property"""
        prod_tot = self._device.freq
        return prod_tot

    @property
    def unit_of_measurement(self):
        """unit of mesurment property"""
        return self._unit_of_measurement

    @property
    def name(self):
        """ Entity name """
        return f"{self._name} electrical frequency"

    @property
    def icon(self):
        """icon getter"""
        return "mdi:sine-wave"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self._device.device_info
    
    @property
    def device_class(self):
        """ Entity device_class """
        return SensorDeviceClass.FREQUENCY


class SunologyRssiSensorEntity(CoordinatorEntity, SensorEntity):
    """Represent a mipower of a  device."""

    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]],
                 device:SunologyAbstractDevice, hass):
        """Set up SunologBatteryPowerSensor entity."""
        super().__init__(coordinator)
        self._device = device
        self._name = device.name
        self._unit_of_measurement = "dB"
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"rssi")}_{device_registry.format_mac(device.device_id)}"# pylint: disable=C0301
        self._state = 0
        self._hass = hass

    @property
    def entity_category(self):
        return None

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"rssi_{device_registry.format_mac(self._device.device_id)}"

    @property
    def state(self):
        """state property"""
        prod_tot = self._device.rssi
        return prod_tot

    @property
    def unit_of_measurement(self):
        """unit of mesurment property"""
        return self._unit_of_measurement

    @property
    def name(self):
        """ Entity name """
        return f"{self._name} Rssi"

    @property
    def icon(self):
        """icon getter"""
        return "mdi:signal"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self._device.device_info
    
    @property
    def device_class(self):
        """ Entity device_class """
        return SensorDeviceClass.SIGNAL_STRENGTH

    @property
    def entity_category(self):
        """ Entity entity_category """
        return EntityCategory.DIAGNOSTIC

class SunologyApparentPowerExportSensorEntity(CoordinatorEntity, SensorEntity):
    """Represent a mipower of a  device."""

    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]],
                 device:SunologyAbstractDevice, hass):
        """Set up SunologyApparentPowerExportSensorEntity entity."""
        super().__init__(coordinator)
        self._device = device
        self._name = device.name
        self._unit_of_measurement = "VA"
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"app_power_export")}_{device_registry.format_mac(device.device_id)}"# pylint: disable=C0301
        self._state = 0
        self._hass = hass

    @property
    def entity_category(self):
        return None

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"app_power_export_{device_registry.format_mac(self._device.device_id)}"

    @property
    def state(self):
        """state property"""
        prod_tot = self._device.app_power_prod
        return prod_tot

    @property
    def unit_of_measurement(self):
        """unit of mesurment property"""
        return self._unit_of_measurement

    @property
    def name(self):
        """ Entity name """
        return f"{self._name} App power exported"

    @property
    def icon(self):
        """icon getter"""
        return "mdi:meter-electric-outline"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self._device.device_info
    
    @property
    def device_class(self):
        """ Entity device_class """
        return SensorDeviceClass.APPARENT_POWER

class SunologyApparentPowerImportSensorEntity(CoordinatorEntity, SensorEntity):
    """Represent a mipower of a  device."""

    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]],
                 device:SunologyAbstractDevice, hass):
        """Set up SunologyApparentPowerImportSensorEntity entity."""
        super().__init__(coordinator)
        self._device = device
        self._name = device.name
        self._unit_of_measurement = "VA"
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"app_power_import")}_{device_registry.format_mac(device.device_id)}"# pylint: disable=C0301
        self._state = 0
        self._hass = hass

    @property
    def entity_category(self):
        return None

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"app_power_import_{device_registry.format_mac(self._device.device_id)}"

    @property
    def state(self):
        """state property"""
        prod_tot = self._device.app_power_usage
        return prod_tot

    @property
    def unit_of_measurement(self):
        """unit of mesurment property"""
        return self._unit_of_measurement

    @property
    def name(self):
        """ Entity name """
        return f"{self._name} App power imported"

    @property
    def icon(self):
        """icon getter"""
        return "mdi:meter-electric"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self._device.device_info
    
    @property
    def device_class(self):
        """ Entity device_class """
        return SensorDeviceClass.APPARENT_POWER