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
    StoreyPack,
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
            if(isinstance(device,(StoreyMaster, StoreyPack))):
                coordoned_device['device_entities'].append(SunologyBatteryCellsTempSensorEntity(coordinator, device, hass))
                coordoned_device['device_entities'].append(SunologyBatteryRadTempSensorEntity(coordinator, device, hass))
                coordoned_device['device_entities'].append(SunologyBatteryTargetPowerSensorEntity(coordinator, device, hass))
                coordoned_device['device_entities'].append(SunologyBatteryDcVoltageSensorEntity(coordinator, device, hass))
                coordoned_device['device_entities'].append(SunologyBatteryDcCurrentSensorEntity(coordinator, device, hass))
                coordoned_device['device_entities'].append(SunologyBatteryEnergyProducedSensorEntity(coordinator, device, hass))
                coordoned_device['device_entities'].append(SunologyBatteryEnergyConsumedSensorEntity(coordinator, device, hass))
        
        if isinstance(device, StoreyMaster):
            coordoned_device['device_entities'].append(SunologyBatteryMasterStatusSensorEntity(coordinator, device, hass))
            coordoned_device['device_entities'].append(SunologyBatteryMasterAcVoltageSensorEntity(coordinator, device, hass))

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
            coordoned_device['device_entities'].append(SunologyContractSensorEntity(coordinator, device, hass))
            coordoned_device['device_entities'].append(SunologyCurrentTarifSensorEntity(coordinator, device, hass))

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
        self._state = None
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
        self._state = None
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
        self._state = None
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

class SunologyBatteryTargetPowerSensorEntity(CoordinatorEntity, SensorEntity):
    """Represent a mipower of a  device."""

    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]],
                 device:SunologyAbstractDevice, hass):
        """Set up SunologBatteryTargetPowerSensor entity."""
        super().__init__(coordinator)
        self._device = device
        self._name = device.name
        self._unit_of_measurement = "W"
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"targetPow")}_{device_registry.format_mac(device.device_id)}"# pylint: disable=C0301
        self._state = None
        self._hass = hass

    @property
    def entity_category(self):
        return None

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"targetP_{device_registry.format_mac(self._device.device_id)}"

    @property
    def state(self):
        """state property"""
        state = self._device.targetPow
        return state

    @property
    def unit_of_measurement(self):
        """unit of mesurment property"""
        return self._unit_of_measurement

    @property
    def name(self):
        """ Entity name """
        return f"{self._name} battery target Power"

    @property
    def icon(self):
        """icon getter"""
        return "mdi:target"

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

class SunologyBatteryDcVoltageSensorEntity(CoordinatorEntity, SensorEntity):
    """Represent a mipower of a  device."""

    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]],
                 device:SunologyAbstractDevice, hass):
        """Set up SunologyBatteryDcVoltageSensor entity."""
        super().__init__(coordinator)
        self._device = device
        self._name = device.name
        self._unit_of_measurement = "V"
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"dcVoltage")}_{device_registry.format_mac(device.device_id)}"# pylint: disable=C0301
        self._state = None
        self._hass = hass

    @property
    def entity_category(self):
        return None

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"dcVoltage_{device_registry.format_mac(self._device.device_id)}"

    @property
    def state(self):
        """state property"""
        state = self._device.dcVoltage
        return state

    @property
    def unit_of_measurement(self):
        """unit of mesurment property"""
        return self._unit_of_measurement

    @property
    def name(self):
        """ Entity name """
        return f"{self._name} battery DC Voltage"

    @property
    def icon(self):
        """icon getter"""
        return "mdi:flash-triangle-outline"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self._device.device_info
    
    @property
    def device_class(self):
        """ Entity device_class """
        return SensorDeviceClass.VOLTAGE

    @property
    def state_class(self):
        """ Entity state_class """
        return SensorStateClass.MEASUREMENT


class SunologyBatteryMasterAcVoltageSensorEntity(CoordinatorEntity, SensorEntity):
    """Represent a mipower of a  device."""

    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]],
                 device:SunologyAbstractDevice, hass):
        """Set up SunologyBatteryAcVoltageSensor entity."""
        super().__init__(coordinator)
        self._device = device
        self._name = device.name
        self._unit_of_measurement = "V"
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"acVoltage")}_{device_registry.format_mac(device.device_id)}"# pylint: disable=C0301
        self._state = None
        self._hass = hass

    @property
    def entity_category(self):
        return None

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"acVoltage_{device_registry.format_mac(self._device.device_id)}"

    @property
    def state(self):
        """state property"""
        state = self._device.acVoltage
        return state

    @property
    def unit_of_measurement(self):
        """unit of mesurment property"""
        return self._unit_of_measurement

    @property
    def name(self):
        """ Entity name """
        return f"{self._name} battery master AC Voltage"

    @property
    def icon(self):
        """icon getter"""
        return "mdi:flash-triangle"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self._device.device_info
    
    @property
    def device_class(self):
        """ Entity device_class """
        return SensorDeviceClass.VOLTAGE

    @property
    def state_class(self):
        """ Entity state_class """
        return SensorStateClass.MEASUREMENT

class SunologyBatteryDcCurrentSensorEntity(CoordinatorEntity, SensorEntity):
    """Represent a mipower of a  device."""

    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]],
                 device:SunologyAbstractDevice, hass):
        """Set up SunologyBatteryDcCurrentSensor entity."""
        super().__init__(coordinator)
        self._device = device
        self._name = device.name
        self._unit_of_measurement = "A"
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"dcCurrent")}_{device_registry.format_mac(device.device_id)}"# pylint: disable=C0301
        self._state = None
        self._hass = hass

    @property
    def entity_category(self):
        return None

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"dcCurrent_{device_registry.format_mac(self._device.device_id)}"

    @property
    def state(self):
        """state property"""
        state = self._device.dcCurrent
        return state

    @property
    def unit_of_measurement(self):
        """unit of mesurment property"""
        return self._unit_of_measurement

    @property
    def name(self):
        """ Entity name """
        return f"{self._name} battery DC Current"

    @property
    def icon(self):
        """icon getter"""
        return "mdi:current-dc"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self._device.device_info
    
    @property
    def device_class(self):
        """ Entity device_class """
        return SensorDeviceClass.CURRENT

    @property
    def state_class(self):
        """ Entity state_class """
        return SensorStateClass.MEASUREMENT

class SunologyBatteryEnergyProducedSensorEntity(CoordinatorEntity, SensorEntity):
    """Represent a mipower of a  device."""

    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]],
                 device:SunologyAbstractDevice, hass):
        """Set up SunologyBatteryEnergyProducedSensor entity."""
        super().__init__(coordinator)
        self._device = device
        self._name = device.name
        self._unit_of_measurement = "mWh"
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"energyProd")}_{device_registry.format_mac(device.device_id)}"# pylint: disable=C0301
        self._state = None
        self._hass = hass

    @property
    def entity_category(self):
        return None

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"energyProd_{device_registry.format_mac(self._device.device_id)}"

    @property
    def state(self):
        """state property"""
        state = self._device.energyProd
        return state

    @property
    def unit_of_measurement(self):
        """unit of mesurment property"""
        return self._unit_of_measurement

    @property
    def name(self):
        """ Entity name """
        return f"{self._name} battery Energy Produced"

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
        return SensorStateClass.MEASUREMENT


class SunologyBatteryEnergyConsumedSensorEntity(CoordinatorEntity, SensorEntity):
    """Represent a mipower of a  device."""

    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]],
                 device:SunologyAbstractDevice, hass):
        """Set up SunologyBatteryEnergyConsumedSensor entity."""
        super().__init__(coordinator)
        self._device = device
        self._name = device.name
        self._unit_of_measurement = "mWh"
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"energyCons")}_{device_registry.format_mac(device.device_id)}"# pylint: disable=C0301
        self._state = None
        self._hass = hass

    @property
    def entity_category(self):
        return None

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"energyCons_{device_registry.format_mac(self._device.device_id)}"

    @property
    def state(self):
        """state property"""
        state = self._device.energyCons
        return state

    @property
    def unit_of_measurement(self):
        """unit of mesurment property"""
        return self._unit_of_measurement

    @property
    def name(self):
        """ Entity name """
        return f"{self._name} battery Energy Consumed"

    @property
    def icon(self):
        """icon getter"""
        return "mdi:lightning-bolt"

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
        return SensorStateClass.MEASUREMENT


class SunologyBatteryMasterStatusSensorEntity(CoordinatorEntity, SensorEntity):
    """Represent a mipower of a  device."""

    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]],
                 device:SunologyAbstractDevice, hass):
        """Set up SunologyStatusSensorEntity entity."""
        super().__init__(coordinator)
        self._device = device
        self._name = device.name
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"status")}_{device_registry.format_mac(device.device_id)}"# pylint: disable=C0301
        self._state = None
        self._hass = hass

    @property
    def entity_category(self):
        return None

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"status_{device_registry.format_mac(self._device.device_id)}"

    @property
    def state(self):
        """state property"""
        state = self._device.status
        return state

    @property
    def name(self):
        """ Entity name """
        return f"{self._name} master Status"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self._device.device_info
    
    @property
    def options(self) -> DeviceInfo:
        """Return the device info."""
        return [
            "CHARGING",
            "DISCHARGING",
            "OFFGRID_DISCHARGING",
            "OFF"
        ]
    
    @property
    def device_class(self):
        """ Entity device_class """
        return SensorDeviceClass.ENUM

        
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
        self._state = None
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
        self._state = None
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
class SunologyBatteryCellsTempSensorEntity(CoordinatorEntity, SensorEntity):
    """Represent a mipower of a  device."""

    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]],
                 device:SunologyAbstractDevice, hass):
        """Set up SunologBatteryPowerSensor entity."""
        super().__init__(coordinator)
        self._device = device
        self._name = device.name
        self._unit_of_measurement = "°C"
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"cellsTmp")}_{device_registry.format_mac(device.device_id)}"# pylint: disable=C0301
        self._state = None
        self._hass = hass

    @property
    def entity_category(self):
        return None

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"cellsTmp_{device_registry.format_mac(self._device.device_id)}"

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
        return f"{self._name} battery cells Temperature"

    @property
    def icon(self):
        """icon getter"""
        return "mdi:temperature-celsius"

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

class SunologyBatteryRadTempSensorEntity(CoordinatorEntity, SensorEntity):
    """Represent a mipower of a  device."""

    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]],
                 device:SunologyAbstractDevice, hass):
        """Set up SunologBatteryRadTempSensor entity."""
        super().__init__(coordinator)
        self._device = device
        self._name = device.name
        self._unit_of_measurement = "°C"
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"radTmp")}_{device_registry.format_mac(device.device_id)}"# pylint: disable=C0301
        self._state = None
        self._hass = hass

    @property
    def entity_category(self):
        return None

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"radTmp_{device_registry.format_mac(self._device.device_id)}"

    @property
    def state(self):
        """state property"""
        batP = self._device.radTmp
        return batP

    @property
    def unit_of_measurement(self):
        """unit of mesurment property"""
        return self._unit_of_measurement

    @property
    def name(self):
        """ Entity name """
        return f"{self._name} battery radiator Temperature"

    @property
    def icon(self):
        """icon getter"""
        return "mdi:thermometer-lines"

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
        self._state = None
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
        self._state = None
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
        self._state = None
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
        prod_tot = None
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
        self._state = None
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
        self._state = None
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
        self._state = None
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
        self._state = None
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
        self._state = None
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
        self._state = None
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

class SunologyContractSensorEntity(CoordinatorEntity, SensorEntity):
    """Represent energy imported (energy consumed) by a smart metter."""

    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]],
                 device:SunologyAbstractDevice, hass):
        """Set up SunologyTotalImportSensorEntity entity."""
        super().__init__(coordinator)
        self._device = device
        self._name = device.name
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"contract")}_{device_registry.format_mac(device.device_id)}"# pylint: disable=C0301
        self._state = None
        self._hass = hass

    @property
    def entity_category(self):
        return None

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"contract_{device_registry.format_mac(self._device.device_id)}"

    @property
    def state(self):
        """state property"""
        contract = self._device.indexes_erl.contract
        return contract

    @property
    def name(self):
        """ Entity name """
        return f"{self._name} energy contract"

    @property
    def icon(self):
        """icon getter"""
        return "mdi:file-sign"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self._device.device_info

class SunologyCurrentTarifSensorEntity(CoordinatorEntity, SensorEntity):
    """Represent energy imported (energy consumed) by a smart metter."""

    def __init__(self, coordinator: DataUpdateCoordinator[Mapping[str, Any]],
                 device:SunologyAbstractDevice, hass):
        """Set up SunologyTotalImportSensorEntity entity."""
        super().__init__(coordinator)
        self._device = device
        self._name = device.name
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"current_tarif")}_{device_registry.format_mac(device.device_id)}"# pylint: disable=C0301
        self._state = None
        self._hass = hass

    @property
    def entity_category(self):
        return None

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"current_tarif_{device_registry.format_mac(self._device.device_id)}"

    @property
    def state(self):
        """state property"""
        contract = self._device.indexes_erl.current_tarif
        return contract

    @property
    def name(self):
        """ Entity name """
        return f"{self._name} energy current tarif"

    @property
    def icon(self):
        """icon getter"""
        return "mdi:cash"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self._device.device_info