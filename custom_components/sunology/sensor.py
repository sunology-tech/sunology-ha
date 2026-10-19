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

from .const import SmartMeterPhase, SmartMeterTarifIndex, ElectricalDataFeature, ContactorMode, ContactorStatus,  PACKAGE_NAME, DOMAIN as SUNOLOGY_DOMAIN
from .device import (
    PLAYMax,
    PLAY,
    CITY,
    HOMEInverter,
    Gateway,
    StoreyMaster,
    StoreyPack,
    SunologyAbstractDevice,
    SolarEventInterface,
    BatteryEventInterface,
    SmartMeter_3P,
    LinkyTransmitter,
    OnOffDevice,
    LegrandContactor,
    MpptInterface
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

                if isinstance(device, SolarEventInterface):
                    new_entities.append(SunologPvPowerSensorEntity(device, hass))
                    new_entities.append(SunologMiPowerSensorEntity(device, hass))
                    
                    if device.mppts_data:
                        for mppt_index, mppt in device.mppts_data.items():
                            new_entities.append(SunologyMpptPowerSensorEntity(device, mppt_index, hass))
                            new_entities.append(SunologyMpptCurrentSensorEntity(device, mppt_index, hass))
                            new_entities.append(SunologyMpptVoltageSensorEntity(device, mppt_index, hass))
                            new_entities.append(SunologyMpptEnergySensorEntity(device, mppt_index, hass))
                if isinstance(device, BatteryEventInterface):
                    new_entities.append(SunologyBatteryPowerSensorEntity(device, hass))
                    new_entities.append(SunologyBatterySocSensorEntity(device, hass))
                    new_entities.append(SunologyBatteryTempSensorEntity(device, hass))
                    if(isinstance(device,(StoreyMaster, StoreyPack))):
                        new_entities.append(SunologyBatteryCellsTempSensorEntity(device, hass))
                        new_entities.append(SunologyBatteryRadTempSensorEntity(device, hass))
                        new_entities.append(SunologyBatteryTargetPowerSensorEntity(device, hass))
                        new_entities.append(SunologyBatteryDcVoltageSensorEntity(device, hass))
                        new_entities.append(SunologyBatteryDcCurrentSensorEntity(device, hass))
                        new_entities.append(SunologyBatteryEnergyProducedSensorEntity(device, hass))
                        new_entities.append(SunologyBatteryEnergyConsumedSensorEntity(device, hass))
                
                if isinstance(device, StoreyMaster):
                    new_entities.append(SunologyBatteryMasterStatusSensorEntity(device, hass))
                    new_entities.append(SunologyBatteryMasterAcVoltageSensorEntity(device, hass))

                if isinstance(device, SmartMeter_3P):
                    new_entities.append(SunologyElectricalDataSensorEntity_Power(device,  SmartMeterPhase.ALL, hass))
                    new_entities.append(SunologyElectricalDataSensorEntity_Power(device,  SmartMeterPhase.ALL, hass, True))
                    new_entities.append(SunologyTotalExportSensorEntity(device,  SmartMeterPhase.ALL, hass))
                    new_entities.append(SunologyTotalImportSensorEntity(device,  SmartMeterPhase.ALL, hass))
                    new_entities.append(SunologyElectricalDataSensorEntityFeature(device, SmartMeterPhase.ALL, hass))
                    new_entities.append(SunologyElectricalDataSensorEntity_Power(device,  SmartMeterPhase.PHASE_1, hass))
                    new_entities.append(SunologyElectricalDataSensorEntity_Power(device,  SmartMeterPhase.PHASE_1, hass, True))
                    new_entities.append(SunologyTotalExportSensorEntity(device,  SmartMeterPhase.PHASE_1, hass))
                    new_entities.append(SunologyTotalImportSensorEntity(device,  SmartMeterPhase.PHASE_1, hass))
                    new_entities.append(SunologyElectricalDataSensorEntityFeature(device, SmartMeterPhase.PHASE_1, hass))
                    new_entities.append(SunologyElectricalDataSensorEntity_Power(device,  SmartMeterPhase.PHASE_2, hass))
                    new_entities.append(SunologyElectricalDataSensorEntity_Power(device,  SmartMeterPhase.PHASE_2, hass, True))
                    new_entities.append(SunologyTotalExportSensorEntity(device,  SmartMeterPhase.PHASE_2, hass))
                    new_entities.append(SunologyTotalImportSensorEntity(device,  SmartMeterPhase.PHASE_2, hass))
                    new_entities.append(SunologyElectricalDataSensorEntityFeature(device, SmartMeterPhase.PHASE_2, hass))
                    new_entities.append(SunologyElectricalDataSensorEntity_Power(device,  SmartMeterPhase.PHASE_3, hass))
                    new_entities.append(SunologyElectricalDataSensorEntity_Power(device,  SmartMeterPhase.PHASE_3, hass, True))
                    new_entities.append(SunologyTotalExportSensorEntity(device,  SmartMeterPhase.PHASE_3, hass))
                    new_entities.append(SunologyTotalImportSensorEntity(device,  SmartMeterPhase.PHASE_3, hass))
                    new_entities.append(SunologyElectricalDataSensorEntityFeature(device, SmartMeterPhase.PHASE_3, hass))
                    new_entities.append(SunologyElectricityFrequencySensorEntity(device, hass))

                if isinstance(device, LinkyTransmitter):
                    new_entities.append(SunologyApparentPowerImportSensorEntity(device, hass))
                    new_entities.append(SunologyApparentPowerExportSensorEntity(device, hass))
                    new_entities.append(SunologyTotalExportSensorEntity(device,  SmartMeterPhase.ALL, hass))
                    new_entities.append(SunologyTotalImportSensorEntity(device,  SmartMeterPhase.ALL, hass))
                    new_entities.append(SunologyImportSensorEntity_PeriodIndex(device,  SmartMeterTarifIndex.INDEX_1, hass))
                    new_entities.append(SunologyImportSensorEntity_PeriodIndex(device,  SmartMeterTarifIndex.INDEX_2, hass))
                    new_entities.append(SunologyImportSensorEntity_PeriodIndex(device,  SmartMeterTarifIndex.INDEX_3, hass))
                    new_entities.append(SunologyImportSensorEntity_PeriodIndex(device,  SmartMeterTarifIndex.INDEX_4, hass))
                    new_entities.append(SunologyImportSensorEntity_PeriodIndex(device,  SmartMeterTarifIndex.INDEX_5, hass))
                    new_entities.append(SunologyImportSensorEntity_PeriodIndex(device,  SmartMeterTarifIndex.INDEX_6, hass))
                    new_entities.append(SunologyImportSensorEntity_PeriodIndex(device,  SmartMeterTarifIndex.INDEX_7, hass))
                    new_entities.append(SunologyImportSensorEntity_PeriodIndex(device,  SmartMeterTarifIndex.INDEX_8, hass))
                    new_entities.append(SunologyImportSensorEntity_PeriodIndex(device,  SmartMeterTarifIndex.INDEX_9, hass))
                    new_entities.append(SunologyImportSensorEntity_PeriodIndex(device,  SmartMeterTarifIndex.INDEX_10, hass))
                    new_entities.append(SunologyContractSensorEntity(device, hass))
                    new_entities.append(SunologyCurrentTarifSensorEntity(device, hass))
                
                if isinstance(device, OnOffDevice):
                    new_entities.append(SunologyElectricalDataSensorEntity_Power(device,  SmartMeterPhase.ALL, hass))
                    new_entities.append(SunologyElectricalDataSensorEntity_Power(device,  SmartMeterPhase.ALL, hass, True))
                    if not isinstance (device, LegrandContactor):
                        new_entities.append(SunologyElectricalDataSensorEntity_ApparentPower(device,  SmartMeterPhase.ALL, hass))
                    # A device without a METERING cluster never reports a cumulated
                    # counter: an energy sensor would stay None forever and pollute the
                    # Energy dashboard.
                    if device.has_energy_metering:
                        new_entities.append(SunologyTotalImportSensorEntity(device,  SmartMeterPhase.ALL, hass))

                    new_entities.append(SunologyOnOffValueSensorEntity(device, hass, "runtime_on"))
                    new_entities.append(SunologyOnOffValueSensorEntity(device, hass, "target_power"))

                if isinstance(device, LegrandContactor):
                    new_entities.append(SunologyContactorStatusSensorEntity(device, hass))
                    new_entities.append(SunologyContactorModeSensorEntity(device, hass))
                    new_entities.append(SunologyOnOffValueSensorEntity(device, hass, "min_on_time"))
                    new_entities.append(SunologyOnOffValueSensorEntity(device, hass, "runtime_min"))
                    new_entities.append(SunologyOnOffValueSensorEntity(device, hass, "max_cons"))


                if isinstance(device, (Gateway)):
                    new_entities.append(SunologyWifiApBssidSensorEntity(device, hass))
                    new_entities.append(SunologyWifiIpSensorEntity(device, hass))
                    new_entities.append(SunologyEthIpSensorEntity(device, hass))

                new_entities.append(SunologyRssiSensorEntity(device, hass))

                if not 'device_entities' in coordinated_device: 
                    coordinated_device['device_entities'] = []
                coordinated_device['device_entities'].extend(new_entities)

                entities.extend(new_entities)
            async_add_entities(entities)
    _check_device()
    return True

class SunologPvPowerSensorEntity(SensorEntity):
    """Represent a pvpower of a  device."""

    def __init__(self, device:SunologyAbstractDevice, hass):
        """Set up SunologPvPowerSensor entity."""
        
        self._device = device
        self._name = device.name
        self._unit_of_measurement = "W"
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"pvP")}_{_format_devid_mac(device.device_id)}".lower()# pylint: disable=C0301
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
        return f"pvP_{_format_devid_mac(self._device.device_id)}".lower()

    @property
    def state(self):
        """state property"""
        self._state = self._device.pvP
        return self._state

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


class SunologMiPowerSensorEntity(SensorEntity):
    """Represent a mipower of a  device."""

    def __init__(self, device:SunologyAbstractDevice, hass):
        """Set up SunologMiPowerSensor entity."""
        self._device = device
        self._name = device.name
        self._unit_of_measurement = "W"
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"miP")}_{_format_devid_mac(device.device_id)}".lower()# pylint: disable=C0301
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
        return f"miP_{_format_devid_mac(self._device.device_id)}".lower()

    @property
    def state(self):
        """state property"""
        self._state = self._device.miP
        return self._state

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

    @property
    def should_poll(self) -> bool:
        """No need to poll. Coordinator notifies entity of updates."""
        return False


class SunologyMpptPowerSensorEntity(SensorEntity):
    """Represent a MPPT power sensor."""

    def __init__(self, device:SunologyAbstractDevice, mppt_index, hass):
        """Set up MPPT power sensor entity."""
        self._device = device
        self._mppt_index = mppt_index
        self._name = device.name
        self._unit_of_measurement = "W"
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f'mppt_{mppt_index}_power')}_{_format_devid_mac(device.device_id)}".lower()
        self._state = None
        self._hass = hass

    @property
    def entity_category(self):
        return EntityCategory.DIAGNOSTIC

    @property
    def hass(self):
        return self._hass

    @hass.setter
    def hass(self, hass):
        pass

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"mppt_{self._mppt_index}_power_{_format_devid_mac(self._device.device_id)}".lower()

    @property
    def state(self):
        """state property"""
        if self._mppt_index in self._device.mppts_data:
            self._state = self._device.mppts_data[self._mppt_index].power
        return self._state

    @property
    def unit_of_measurement(self):
        """unit of measurement property"""
        return self._unit_of_measurement

    @property
    def name(self):
        """Entity name"""
        return f"{self._name} MPPT {self._mppt_index} Power"

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
        """Entity device_class"""
        return SensorDeviceClass.POWER

    @property
    def state_class(self):
        """Entity state_class"""
        return SensorStateClass.MEASUREMENT

    @property
    def should_poll(self) -> bool:
        """No need to poll. Coordinator notifies entity of updates."""
        return False


class SunologyMpptCurrentSensorEntity(SensorEntity):
    """Represent a MPPT current sensor."""

    def __init__(self, device:SunologyAbstractDevice, mppt_index, hass):
        """Set up MPPT current sensor entity."""
        self._device = device
        self._mppt_index = mppt_index
        self._name = device.name
        self._unit_of_measurement = "A"
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f'mppt_{mppt_index}_current')}_{_format_devid_mac(device.device_id)}".lower()
        self._state = None
        self._hass = hass

    @property
    def entity_category(self):
        return EntityCategory.DIAGNOSTIC

    @property
    def hass(self):
        return self._hass

    @hass.setter
    def hass(self, hass):
        pass

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"mppt_{self._mppt_index}_current_{_format_devid_mac(self._device.device_id)}".lower()

    @property
    def state(self):
        """state property"""
        if self._mppt_index in self._device.mppts_data:
            self._state = self._device.mppts_data[self._mppt_index].current
        return self._state

    @property
    def unit_of_measurement(self):
        """unit of measurement property"""
        return self._unit_of_measurement

    @property
    def name(self):
        """Entity name"""
        return f"{self._name} MPPT {self._mppt_index} Current"

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
        """Entity device_class"""
        return SensorDeviceClass.CURRENT

    @property
    def state_class(self):
        """Entity state_class"""
        return SensorStateClass.MEASUREMENT

    @property
    def should_poll(self) -> bool:
        """No need to poll. Coordinator notifies entity of updates."""
        return False


class SunologyMpptVoltageSensorEntity(SensorEntity):
    """Represent a MPPT voltage sensor."""

    def __init__(self, device:SunologyAbstractDevice, mppt_index, hass):
        """Set up MPPT voltage sensor entity."""
        self._device = device
        self._mppt_index = mppt_index
        self._name = device.name
        self._unit_of_measurement = "V"
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f'mppt_{mppt_index}_voltage')}_{_format_devid_mac(device.device_id)}".lower()
        self._state = None
        self._hass = hass

    @property
    def entity_category(self):
        return EntityCategory.DIAGNOSTIC

    @property
    def hass(self):
        return self._hass

    @hass.setter
    def hass(self, hass):
        pass

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"mppt_{self._mppt_index}_voltage_{_format_devid_mac(self._device.device_id)}".lower()

    @property
    def state(self):
        """state property"""
        if self._mppt_index in self._device.mppts_data:
            self._state = self._device.mppts_data[self._mppt_index].voltage
        return self._state

    @property
    def unit_of_measurement(self):
        """unit of measurement property"""
        return self._unit_of_measurement

    @property
    def name(self):
        """Entity name"""
        return f"{self._name} MPPT {self._mppt_index} Voltage"

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
        """Entity device_class"""
        return SensorDeviceClass.VOLTAGE

    @property
    def state_class(self):
        """Entity state_class"""
        return SensorStateClass.MEASUREMENT

    @property
    def should_poll(self) -> bool:
        """No need to poll. Coordinator notifies entity of updates."""
        return False


class SunologyMpptEnergySensorEntity(SensorEntity):
    """Represent a MPPT energy sensor."""

    def __init__(self, device:SunologyAbstractDevice, mppt_index, hass):
        """Set up MPPT energy sensor entity."""
        self._device = device
        self._mppt_index = mppt_index
        self._name = device.name
        self._unit_of_measurement = "Wh"
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f'mppt_{mppt_index}_energy')}_{_format_devid_mac(device.device_id)}".lower()
        self._state = None
        self._hass = hass

    @property
    def entity_category(self):
        return EntityCategory.DIAGNOSTIC

    @property
    def hass(self):
        return self._hass

    @hass.setter
    def hass(self, hass):
        pass

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"mppt_{self._mppt_index}_energy_{_format_devid_mac(self._device.device_id)}".lower()

    @property
    def state(self):
        """state property"""
        if self._mppt_index in self._device.mppts_data:
            self._state = self._device.mppts_data[self._mppt_index].prod_tot
        return self._state

    @property
    def unit_of_measurement(self):
        """unit of measurement property"""
        return self._unit_of_measurement

    @property
    def name(self):
        """Entity name"""
        return f"{self._name} MPPT {self._mppt_index} Energy"

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
        """Entity device_class"""
        return SensorDeviceClass.ENERGY

    @property
    def state_class(self):
        """Entity state_class"""
        return SensorStateClass.TOTAL_INCREASING

    @property
    def should_poll(self) -> bool:
        """No need to poll. Coordinator notifies entity of updates."""
        return False


class SunologyBatteryPowerSensorEntity(SensorEntity):
    """Represent a mipower of a  device."""

    def __init__(self, device:SunologyAbstractDevice, hass):
        """Set up SunologBatteryPowerSensor entity."""
        self._device = device
        self._name = device.name
        self._unit_of_measurement = "W"
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"batP")}_{_format_devid_mac(device.device_id)}".lower()# pylint: disable=C0301
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
        return f"batP_{_format_devid_mac(self._device.device_id)}".lower()

    @property
    def state(self):
        """state property"""
        self._state = (self._device.batP * -1) if self._device.batP is not None else self._device.batP
        return self._state

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

    @property
    def should_poll(self) -> bool:
        """No need to poll. Coordinator notifies entity of updates."""
        return False

class SunologyBatteryTargetPowerSensorEntity(SensorEntity):
    """Represent a mipower of a  device."""

    def __init__(self, device:SunologyAbstractDevice, hass):
        """Set up SunologBatteryTargetPowerSensor entity."""
        self._device = device
        self._name = device.name
        self._unit_of_measurement = "W"
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"targetPow")}_{_format_devid_mac(device.device_id)}".lower()# pylint: disable=C0301
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
        return f"targetP_{_format_devid_mac(self._device.device_id)}".lower()

    @property
    def state(self):
        """state property"""
        self._state = (self._device.targetPow * -1) if self._device.targetPow is not None else self._device.targetPow
        return self._state

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

    @property
    def should_poll(self) -> bool:
        """No need to poll. Coordinator notifies entity of updates."""
        return False

class SunologyBatteryDcVoltageSensorEntity(SensorEntity):
    """Represent a mipower of a  device."""

    def __init__(self, device:SunologyAbstractDevice, hass):
        """Set up SunologyBatteryDcVoltageSensor entity."""
        
        self._device = device
        self._name = device.name
        self._unit_of_measurement = "V"
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"dcVoltage")}_{_format_devid_mac(device.device_id)}".lower()# pylint: disable=C0301
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
        return f"dcVoltage_{_format_devid_mac(self._device.device_id)}".lower()

    @property
    def state(self):
        """state property"""
        self._state = self._device.dcVoltage
        return self._state

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

    @property
    def should_poll(self) -> bool:
        """No need to poll. Coordinator notifies entity of updates."""
        return False

class SunologyBatteryMasterAcVoltageSensorEntity(SensorEntity):
    """Represent a mipower of a  device."""

    def __init__(self, device:SunologyAbstractDevice, hass):
        """Set up SunologyBatteryAcVoltageSensor entity."""
        self._device = device
        self._name = device.name
        self._unit_of_measurement = "V"
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"acVoltage")}_{_format_devid_mac(device.device_id)}".lower()# pylint: disable=C0301
        self._state = None
        self._hass = hass

    @property
    def hass(self):
        return self._hass

    @hass.setter
    def hass(self, hass):
        pass

    @property
    def entity_category(self):
        return None

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"acVoltage_{_format_devid_mac(self._device.device_id)}".lower()

    @property
    def state(self):
        """state property"""
        self._state = self._device.acVoltage
        return self._state

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


class SunologyBatteryDcCurrentSensorEntity(SensorEntity):
    """Represent a mipower of a  device."""

    def __init__(self, device:SunologyAbstractDevice, hass):
        """Set up SunologyBatteryDcCurrentSensor entity."""
        self._device = device
        self._name = device.name
        self._unit_of_measurement = "A"
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"dcCurrent")}_{_format_devid_mac(device.device_id)}".lower()# pylint: disable=C0301
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
        return f"dcCurrent_{_format_devid_mac(self._device.device_id)}".lower()

    @property
    def state(self):
        """state property"""
        self._state = self._device.dcCurrent
        return self._state

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


class SunologyBatteryEnergyProducedSensorEntity(SensorEntity):
    """Represent a mipower of a  device."""

    def __init__(self, device:SunologyAbstractDevice, hass):
        """Set up SunologyBatteryEnergyProducedSensor entity."""
        self._device = device
        self._name = device.name
        self._unit_of_measurement = "Wh"
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"energyProd")}_{_format_devid_mac(device.device_id)}".lower()# pylint: disable=C0301
        self._state = None
        self._hass = hass
        self._last_reset = '1970-01-01T00:00:00+00:00'

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
        return f"energyProd_{_format_devid_mac(self._device.device_id)}".lower()

    @property
    def state(self):
        """state property"""
        # the firmware reports a cumulative counter in mWh; expose it in Wh (valid ENERGY unit)
        raw = self._device.energyProd
        self._state = round(raw / 1000) if raw is not None else None
        return self._state

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
        return SensorStateClass.TOTAL_INCREASING
    
    # @property
    # def last_reset(self):
    #     """ last sensor reset"""
    #     return self._last_reset

    @property
    def should_poll(self) -> bool:
        """No need to poll. Coordinator notifies entity of updates."""
        return False


class SunologyBatteryEnergyConsumedSensorEntity( SensorEntity):
    """Represent a mipower of a  device."""

    def __init__(self, device:SunologyAbstractDevice, hass):
        """Set up SunologyBatteryEnergyConsumedSensor entity."""
        self._device = device
        self._name = device.name
        self._unit_of_measurement = "Wh"
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"energyCons")}_{_format_devid_mac(device.device_id)}".lower()# pylint: disable=C0301
        self._state = None
        self._hass = hass
        self._last_reset = '1970-01-01T00:00:00+00:00'


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
        return f"energyCons_{_format_devid_mac(self._device.device_id)}".lower()

    @property
    def state(self):
        """state property"""
        # the firmware reports a cumulative counter in mWh; expose it in Wh (valid ENERGY unit)
        raw = self._device.energyCons
        self._state = round(raw / 1000) if raw is not None else None
        return self._state

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
        return SensorStateClass.TOTAL_INCREASING
    
    # @property
    # def last_reset(self):
    #     """ last sensor reset"""
    #     return self._last_reset

    @property
    def should_poll(self) -> bool:
        """No need to poll. Coordinator notifies entity of updates."""
        return False

class SunologyBatteryMasterStatusSensorEntity(SensorEntity):
    """Represent a mipower of a  device."""

    def __init__(self, device:SunologyAbstractDevice, hass):
        """Set up SunologyStatusSensorEntity entity."""
        self._device = device
        self._name = device.name
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"status")}_{_format_devid_mac(device.device_id)}".lower()# pylint: disable=C0301
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
        return f"status_{_format_devid_mac(self._device.device_id)}".lower()

    @property
    def state(self):
        """state property"""
        self._state = self._device.status
        return self._state

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

    @property
    def should_poll(self) -> bool:
        """No need to poll. Coordinator notifies entity of updates."""
        return False
        
class SunologyBatterySocSensorEntity(SensorEntity):
    """Represent a mipower of a  device."""

    def __init__(self, device:SunologyAbstractDevice, hass):
        """Set up SunologBatteryPowerSensor entity."""
        self._device = device
        self._name = device.name
        self._unit_of_measurement = "%"
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"batPct")}_{_format_devid_mac(device.device_id)}".lower()# pylint: disable=C0301
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
        return f"batPct_{_format_devid_mac(self._device.device_id)}".lower()

    @property
    def state(self):
        """state property"""
        self._state = self._device.batPct
        return self._state

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
        if self.state is not None:
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
        else:
            icon = "mdi:battery-alert-variant-outline"


        return icon
    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self._device.device_info
    
    @property
    def device_class(self):
        """ Entity device_class """
        return SensorDeviceClass.BATTERY

    @property
    def state_class(self):
        """ Entity state_class: lets HA keep statistics (Energy dashboard, #27) """
        return SensorStateClass.MEASUREMENT

    @property
    def should_poll(self) -> bool:
        """No need to poll. Coordinator notifies entity of updates."""
        return False

class SunologyBatteryTempSensorEntity(SensorEntity):
    """Represent a mipower of a  device."""

    def __init__(self, device:SunologyAbstractDevice, hass):
        """Set up SunologBatteryPowerSensor entity."""
        self._device = device
        self._name = device.name
        self._unit_of_measurement = "°C"
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"batTmp")}_{_format_devid_mac(device.device_id)}".lower()# pylint: disable=C0301
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
        return f"batTmp_{_format_devid_mac(self._device.device_id)}".lower()

    @property
    def state(self):
        """state property"""
        self._state = self._device.batTmp
        return self._state

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

class SunologyBatteryCellsTempSensorEntity(SensorEntity):
    """Represent a mipower of a  device."""

    def __init__(self, device:SunologyAbstractDevice, hass):
        """Set up SunologBatteryPowerSensor entity."""
        self._device = device
        self._name = device.name
        self._unit_of_measurement = "°C"
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"cellsTmp")}_{_format_devid_mac(device.device_id)}".lower()# pylint: disable=C0301
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
        return f"cellsTmp_{_format_devid_mac(self._device.device_id)}".lower()

    @property
    def state(self):
        """state property"""
        self._state = self._device.cellsTmp
        return self._state

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

    @property
    def should_poll(self) -> bool:
        """No need to poll. Coordinator notifies entity of updates."""
        return False
class SunologyBatteryRadTempSensorEntity(SensorEntity):
    """Represent a mipower of a  device."""

    def __init__(self, device:SunologyAbstractDevice, hass):
        """Set up SunologBatteryRadTempSensor entity."""
        self._device = device
        self._name = device.name
        self._unit_of_measurement = "°C"
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"radTmp")}_{_format_devid_mac(device.device_id)}".lower()# pylint: disable=C0301
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
        return f"radTmp_{_format_devid_mac(self._device.device_id)}".lower()

    @property
    def state(self):
        """state property"""
        self._state = self._device.radTmp
        return self._state

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


class SunologyBatteryMasterPowerSensorEntity(SensorEntity):
    """Represent a mipower of a  device."""

    def __init__(self, device:SunologyAbstractDevice, hass):
        """Set up SunologBatteryPowerSensor entity."""
        self._device = device
        self._name = device.name
        self._unit_of_measurement = "W"
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"masterP")}_{_format_devid_mac(device.device_id)}".lower()# pylint: disable=C0301
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
        return f"masterP_{_format_devid_mac(self._device.device_id)}".lower()

    @property
    def state(self):
        """state property"""
        self._state = self._device.power
        return self._state

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



class SunologyElectricalDataSensorEntity_Power(SensorEntity):
    """Represent a mipower of a  device."""

    def __init__(self, device:SunologyAbstractDevice, phase:SmartMeterPhase, hass, reversed_state=False):
        """Set up SunologBatteryPowerSensor entity.""" 
        self._device = device
        self._name = device.name
        self._unit_of_measurement = "W"
        self._phase = phase
        self._reversed = reversed_state
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"power")}_{self._phase}_{"reversed_" if self._reversed else ""}{_format_devid_mac(device.device_id)}".lower()# pylint: disable=C0301
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
    def hass(self):
        return self._hass

    @hass.setter
    def hass(self, hass):
        pass

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"power_{self._phase}_{"reversed_" if self._reversed else ""}{_format_devid_mac(self._device.device_id)}".lower()

    @property
    def state(self):
        """state property"""
        self._state = self._device.electrical_data[self._phase].power * -1 if self._reversed and self._device.electrical_data[self._phase].power is not None else  self._device.electrical_data[self._phase].power
        return self._state

    @property
    def unit_of_measurement(self):
        """unit of mesurment property"""
        return self._unit_of_measurement

    @property
    def name(self):
        """ Entity name """
        return f"{self._name} {self._phase} electrical data Power{" (reversed)" if self._reversed else ""}"

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
    def entity_registry_enabled_default(self):
        """Reversed entity (Home Assistant sign convention) enabled by default, normal one disabled."""
        return self._reversed

    @property
    def state_class(self):
        """ Entity state_class """
        return SensorStateClass.MEASUREMENT

class SunologyElectricalDataSensorEntity_ApparentPower(SensorEntity):
    """Represent the apparent power of a device."""

    def __init__(self, device:SunologyAbstractDevice, phase:SmartMeterPhase, hass):
        """Set up SunologyElectricalDataSensorEntity_ApparentPower entity."""
        self._device = device
        self._name = device.name
        self._unit_of_measurement = "VA"
        self._phase = phase
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"apparent_power")}_{self._phase}_{_format_devid_mac(device.device_id)}".lower()# pylint: disable=C0301
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
        return f"apparent_power_{self._phase}_{_format_devid_mac(self._device.device_id)}".lower()

    @property
    def state(self):
        """state property"""
        self._state = self._device.electrical_data[self._phase].apparent_power
        return self._state

    @property
    def unit_of_measurement(self):
        """unit of mesurment property"""
        return self._unit_of_measurement

    @property
    def name(self):
        """ Entity name """
        return f"{self._name} {self._phase} electrical data apparent Power"

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
        return SensorDeviceClass.APPARENT_POWER

    @property
    def state_class(self):
        """ Entity state_class """
        return SensorStateClass.MEASUREMENT

class SunologyContactorStatusSensorEntity(SensorEntity):
    """Represent the TAP status as the STREAM app shows it."""

    _attr_translation_key = "contactor_status"

    def __init__(self, device:SunologyAbstractDevice, hass):
        """Set up SunologyContactorStatusSensorEntity entity."""
        self._device = device
        self._name = device.name
        self.entity_id = f"{ENTITY_ID_FORMAT.format("contactor_status")}_{_format_devid_mac(device.device_id)}".lower()# pylint: disable=C0301
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
        return f"contactor_status_{_format_devid_mac(self._device.device_id)}".lower()

    @property
    def state(self):
        """state property"""
        status = self._device.status
        self._state = status.value if status is not None else None
        return self._state

    @property
    def options(self):
        """options list property"""
        return [e.value for e in ContactorStatus]

    @property
    def extra_state_attributes(self):
        """Raw values the status is computed from."""
        mode = self._device.contactor_mode
        try:
            mode_name = ContactorMode(mode).name if mode is not None else None
        except ValueError:
            mode_name = None
        return {
            "contactor_mode": mode_name,
            "contactor_mode_code": mode,
            "relay_on": self._device.state,
            "flow_node_mode": self._device.flowNodeConfig.mode,
            "target_power": self._device.target_power,
        }

    @property
    def name(self):
        """ Entity name """
        return f"{self._name} status"

    @property
    def icon(self):
        """icon getter"""
        return "mdi:water-boiler"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self._device.device_info

    @property
    def device_class(self):
        """ Entity device_class """
        return SensorDeviceClass.ENUM

class SunologyContactorModeSensorEntity(SensorEntity):
    """Represent the mode reported by a Legrand contactor (TAP)."""

    def __init__(self, device:SunologyAbstractDevice, hass):
        """Set up SunologyContactorModeSensorEntity entity."""

        self._device = device
        self._name = device.name
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"contactor_mode")}_{_format_devid_mac(device.device_id)}".lower()# pylint: disable=C0301
        self._state = None
        self._hass = hass

    @property
    def entity_category(self):
        # Raw firmware value; the user-facing value is SunologyContactorStatusSensorEntity.
        return EntityCategory.DIAGNOSTIC

    @property
    def extra_state_attributes(self):
        """Raw numeric code, as sent on the LAN WebSocket."""
        return {"code": self._device.contactor_mode}

    @property
    def hass(self):
        return self._hass

    @hass.setter
    def hass(self, hass):
        pass

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"contactor_mode_{_format_devid_mac(self._device.device_id)}".lower()

    @property
    def state(self):
        """state property

        Tells a relay closed by the Flow apart from one closed by the off-peak contact.
        """
        raw_mode = self._device.contactor_mode
        if raw_mode is None:
            self._state = None
            return self._state
        try:
            self._state = ContactorMode(raw_mode).name
        except ValueError:
            _LOGGER.warning("Unknown contactor mode received: %s", raw_mode)
            self._state = None
        return self._state

    @property
    def options(self):
        """options list property"""
        return [e.name for e in ContactorMode]

    @property
    def name(self):
        """ Entity name """
        return f"{self._name} contactor mode"

    @property
    def icon(self):
        """icon getter"""
        return "mdi:electric-switch"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self._device.device_info

    @property
    def device_class(self):
        """ Entity device_class """
        return SensorDeviceClass.ENUM

# key -> (value getter, label, unit, device class, state class, icon, diagnostic)
_ON_OFF_VALUES = {
    "runtime_on": (lambda d: d.runtime_on, "runtime today", "min",
                   SensorDeviceClass.DURATION, SensorStateClass.TOTAL_INCREASING, "mdi:timer-play-outline", False),
    "target_power": (lambda d: d.target_power, "flow target power", "W",
                     SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, "mdi:target", False),
    # Flow node configuration, written by the STREAM app from the hot water tank
    # capacity and power (backend_mobile ClientConsumptionDeviceService).
    "min_on_time": (lambda d: d.flowNodeConfig.minOnTime, "forced on minimal duration", "s",
                    SensorDeviceClass.DURATION, None, "mdi:timer-lock-outline", True),
    "runtime_min": (lambda d: d.flowNodeConfig.runtimeMin, "daily minimal runtime", "min",
                    SensorDeviceClass.DURATION, None, "mdi:timer-sand", True),
    "max_cons": (lambda d: d.flowNodeConfig.maxCons, "driven load power", "W",
                 SensorDeviceClass.POWER, None, "mdi:water-boiler", True),
}

class SunologyOnOffValueSensorEntity(SensorEntity):
    """Represent a numeric value of an on/off device (Flow runtime, target, config)."""

    def __init__(self, device:SunologyAbstractDevice, hass, key:str):
        """Set up SunologyOnOffValueSensorEntity entity."""
        self._device = device
        self._name = device.name
        self._key = key
        (self._getter, self._label, self._unit_of_measurement, self._device_class,
         self._state_class, self._icon, self._diagnostic) = _ON_OFF_VALUES[key]
        self.entity_id = f"{ENTITY_ID_FORMAT.format(key)}_{_format_devid_mac(device.device_id)}".lower()# pylint: disable=C0301
        self._state = None
        self._hass = hass

    @property
    def entity_category(self):
        return EntityCategory.DIAGNOSTIC if self._diagnostic else None

    @property
    def hass(self):
        return self._hass

    @hass.setter
    def hass(self, hass):
        pass

    @property
    def unique_id(self):
        """Return the unique ID."""
        return f"{self._key}_{_format_devid_mac(self._device.device_id)}".lower()

    @property
    def state(self):
        """state property"""
        self._state = self._getter(self._device)
        return self._state

    @property
    def unit_of_measurement(self):
        """unit of mesurment property"""
        return self._unit_of_measurement

    @property
    def name(self):
        """ Entity name """
        return f"{self._name} {self._label}"

    @property
    def icon(self):
        """icon getter"""
        return self._icon

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self._device.device_info

    @property
    def device_class(self):
        """ Entity device_class """
        return self._device_class

    @property
    def state_class(self):
        """ Entity state_class """
        return self._state_class

class SunologyElectricalDataSensorEntityFeature(SensorEntity):
    """Represent a mipower of a  device."""

    def __init__(self, device:SunologyAbstractDevice, phase:SmartMeterPhase, hass):
        """Set up SunologBatteryPowerSensor entity."""
        self._device = device
        self._name = device.name
        self._phase = phase
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"edFeature")}_{self._phase}_{_format_devid_mac(device.device_id)}".lower()# pylint: disable=C0301
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
        return f"edFeature_{self._phase}_{_format_devid_mac(self._device.device_id)}".lower()

    @property
    def state(self):
        """state property"""
        match self._phase:
            case SmartMeterPhase.ALL:
                self._state = self._device.features.electricalData
            case SmartMeterPhase.PHASE_1:
                self._state = self._device.features.electricalDataP1
            case SmartMeterPhase.PHASE_2:
                self._state = self._device.features.electricalDataP2
            case SmartMeterPhase.PHASE_3:
                self._state = self._device.features.electricalDataP3
        return self._state

    @property
    def name(self):
        """ Entity name """
        return f"{self._name} {self._phase} electrical data Feature"

    @property
    def icon(self):
        """icon getter"""
        return "mdi:tune-vertical"
    
    @property
    def options(self):
        return [
            ElectricalDataFeature.UNUSED,
            ElectricalDataFeature.PRODUCER,
            ElectricalDataFeature.LOAD,
            ElectricalDataFeature.GRID,
            ElectricalDataFeature.PRODUCER_REV,
            ElectricalDataFeature.LOAD_REV,
            ElectricalDataFeature.GRID_REV
        ]

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self._device.device_info
    
    @property
    def device_class(self):
        """ Entity device_class """
        return SensorDeviceClass.ENUM
    
    @property
    def entity_category(self):
        """ Entity entity_category """
        return EntityCategory.DIAGNOSTIC


class SunologyTotalExportSensorEntity(SensorEntity):
    """Represent energy surplus exported (energy produced) by a smart metter."""

    def __init__(self, device:SunologyAbstractDevice, phase:SmartMeterPhase, hass):
        """Set up SunologyTotalExportSensorEntity entity."""
        self._device = device
        self._name = device.name
        self._unit_of_measurement = "Wh"
        self._phase = phase
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"total_export")}_{self._phase}_{_format_devid_mac(device.device_id)}".lower()# pylint: disable=C0301
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
        return f"total_export_{self._phase}_{_format_devid_mac(self._device.device_id)}".lower()

    @property
    def state(self):
        """state property"""
        prod_tot = None
        if isinstance(self._device, SmartMeter_3P):
            prod_tot = self._device.electrical_data[self._phase].prod_tot
        elif isinstance(self._device, LinkyTransmitter):
            prod_tot = self._device.indexes_erl.energy_produced_total
        self._state = prod_tot
        return self._state

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


class SunologyTotalImportSensorEntity(SensorEntity):
    """Represent energy imported (energy consumed) by a smart metter."""

    def __init__(self, device:SunologyAbstractDevice, phase:SmartMeterPhase, hass):
        """Set up SunologyTotalImportSensorEntity entity."""
        self._device = device
        self._name = device.name
        self._unit_of_measurement = "Wh"
        self._phase = phase
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"total_import")}_{self._phase}_{_format_devid_mac(device.device_id)}".lower()# pylint: disable=C0301
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
        return f"total_import_{self._phase}_{_format_devid_mac(self._device.device_id)}".lower()

    @property
    def state(self):
        """state property"""
        conso_tot = None
        if isinstance(self._device, SmartMeter_3P):
            conso_tot = self._device.electrical_data[self._phase].conso_tot
        elif isinstance(self._device, LinkyTransmitter):
            conso_tot = self._device.indexes_erl.energy_consumed_total
        self._state = conso_tot
        return self._state

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


class SunologyImportSensorEntity_PeriodIndex(SensorEntity):
    """Represent energy imported (energy consumed) by a smart metter."""

    def __init__(self, device:SunologyAbstractDevice, tarif_index: SmartMeterTarifIndex, hass):
        """Set up SunologyTotalImportSensorEntity entity."""
        self._device = device
        self._name = device.name
        self._unit_of_measurement = "Wh"
        self._tarif_index = tarif_index
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"import_on_period")}_{self._tarif_index}_{_format_devid_mac(device.device_id)}".lower()# pylint: disable=C0301
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
        return f"import_on_period_{self._tarif_index}_{_format_devid_mac(self._device.device_id)}".lower()

    @property
    def state(self):
        """state property"""
        self._state = self._device.indexes_erl.energy_consumed_indexed[self._tarif_index]
        return self._state

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


class SunologyElectricityFrequencySensorEntity(SensorEntity):
    """Represent a mipower of a  device."""

    def __init__(self, device:SunologyAbstractDevice, hass):
        """Set up SunologBatteryPowerSensor entity."""
        self._device = device
        self._name = device.name
        self._unit_of_measurement = "Hz"
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"frequency")}_{_format_devid_mac(device.device_id)}".lower()# pylint: disable=C0301
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
        return f"frequency_{_format_devid_mac(self._device.device_id)}".lower()

    @property
    def state(self):
        """state property"""
        self._state = self._device.freq
        return self._state

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



class SunologyRssiSensorEntity(SensorEntity):
    """Represent a mipower of a  device."""

    def __init__(self, device:SunologyAbstractDevice, hass):
        """Set up SunologBatteryPowerSensor entity."""
        self._device = device
        self._name = device.name
        self._unit_of_measurement = "dB"
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"rssi")}_{_format_devid_mac(device.device_id)}".lower()# pylint: disable=C0301
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
        return f"rssi_{_format_devid_mac(self._device.device_id)}".lower()

    @property
    def state(self):
        """state property"""
        self._state = self._device.rssi
        return self._state

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


class SunologyEthIpSensorEntity(SensorEntity):
    """Represent a mipower of a  device."""

    def __init__(self, device:SunologyAbstractDevice, hass):
        """Set up SunologBatteryPowerSensor entity."""
        self._device = device
        self._name = device.name
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"ethIP")}_{_format_devid_mac(device.device_id)}".lower()# pylint: disable=C0301
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
        return f"ethIP_{_format_devid_mac(self._device.device_id)}".lower()

    @property
    def state(self):
        """state property"""
        self._state = self._device.ethIP
        return self._state


    @property
    def name(self):
        """ Entity name """
        return f"{self._name} Ethernet IP"

    @property
    def icon(self):
        """icon getter"""
        return "mdi:ethernet"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self._device.device_info

    @property
    def entity_category(self):
        """ Entity entity_category """
        return EntityCategory.DIAGNOSTIC


class SunologyWifiIpSensorEntity(SensorEntity):
    """Represent a mipower of a  device."""

    def __init__(self, device:SunologyAbstractDevice, hass):
        """Set up SunologBatteryPowerSensor entity."""
        self._device = device
        self._name = device.name
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"wifiIP")}_{_format_devid_mac(device.device_id)}".lower()# pylint: disable=C0301
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
        return f"wifiIP_{_format_devid_mac(self._device.device_id)}".lower()

    @property
    def state(self):
        """state property"""
        self._state = self._device.wifiIP
        return self._state

    @property
    def name(self):
        """ Entity name """
        return f"{self._name} Wifi IP"

    @property
    def icon(self):
        """icon getter"""
        return "mdi:wifi"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self._device.device_info

    @property
    def entity_category(self):
        """ Entity entity_category """
        return EntityCategory.DIAGNOSTIC


class SunologyWifiApBssidSensorEntity(SensorEntity):
    """Represent a mipower of a  device."""

    def __init__(self, device:SunologyAbstractDevice, hass):
        """Set up SunologBatteryPowerSensor entity."""
        self._device = device
        self._name = device.name
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"wifiApBssid")}_{_format_devid_mac(device.device_id)}".lower()# pylint: disable=C0301
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
        return f"wifiApBssid_{_format_devid_mac(self._device.device_id)}".lower()

    @property
    def state(self):
        """state property"""
        self._state = self._device.bssid
        return self._state

    @property
    def name(self):
        """ Entity name """
        return f"{self._name} Wifi access point BSSID"

    @property
    def icon(self):
        """icon getter"""
        return "mdi:access-point"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return self._device.device_info

    @property
    def entity_category(self):
        """ Entity entity_category """
        return EntityCategory.DIAGNOSTIC


class SunologyApparentPowerExportSensorEntity(SensorEntity):
    """Represent a mipower of a  device."""

    def __init__(self, device:SunologyAbstractDevice, hass):
        """Set up SunologyApparentPowerExportSensorEntity entity."""
        self._device = device
        self._name = device.name
        self._unit_of_measurement = "VA"
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"app_power_export")}_{_format_devid_mac(device.device_id)}".lower()# pylint: disable=C0301
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
        return f"app_power_export_{_format_devid_mac(self._device.device_id)}".lower()

    @property
    def state(self):
        """state property"""
        self._state = self._device.app_power_prod
        return self._state

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


class SunologyApparentPowerImportSensorEntity( SensorEntity):
    """Represent a mipower of a  device."""

    def __init__(self, device:SunologyAbstractDevice, hass):
        """Set up SunologyApparentPowerImportSensorEntity entity."""
        self._device = device
        self._name = device.name
        self._unit_of_measurement = "VA"
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"app_power_import")}_{_format_devid_mac(device.device_id)}".lower()# pylint: disable=C0301
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
        return f"app_power_import_{_format_devid_mac(self._device.device_id)}".lower()

    @property
    def state(self):
        """state property"""
        self._state = self._device.app_power_usage
        return self._state

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


class SunologyContractSensorEntity(SensorEntity):
    """Represent energy imported (energy consumed) by a smart metter."""

    def __init__(self, device:SunologyAbstractDevice, hass):
        """Set up SunologyTotalImportSensorEntity entity."""
        
        self._device = device
        self._name = device.name
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"contract")}_{_format_devid_mac(device.device_id)}".lower()# pylint: disable=C0301
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
        return f"contract_{_format_devid_mac(self._device.device_id)}".lower()

    @property
    def state(self):
        """state property"""
        self._state = self._device.indexes_erl.contract
        return self._state

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


class SunologyCurrentTarifSensorEntity(SensorEntity):
    """Represent energy imported (energy consumed) by a smart metter."""

    def __init__(self, device:SunologyAbstractDevice, hass):
        """Set up SunologyTotalImportSensorEntity entity."""
        
        self._device = device
        self._name = device.name
        self.entity_id = f"{ENTITY_ID_FORMAT.format(f"current_tarif")}_{_format_devid_mac(device.device_id)}".lower()# pylint: disable=C0301
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
        return f"current_tarif_{_format_devid_mac(self._device.device_id)}".lower()

    @property
    def state(self):
        """state property"""
        self._state = self._device.indexes_erl.current_tarif
        return self._state

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
