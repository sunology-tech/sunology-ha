"""Home Assistant representation of an Sunology device."""
from .const import SmartMeterPhase, SmartMeterTarifIndex,  DOMAIN as SUNOLOGY_DOMAIN
from homeassistant.helpers.device_registry import DeviceInfo, DeviceEntry
from typing import List

class SunologyAbstractDevice():
    """Home Assistant representation of a Sunology abstract device."""

    def __init__(self, raw_device):
        """Initialize PLAYMax device."""
        self._unique_id: str = raw_device['id']
        self._software_version: str = raw_device['fwVersion'] if 'fwVersion' in raw_device.keys() else None
        self._hw_version: str = raw_device['hwVersion'] if 'hwVersion' in raw_device.keys() else None
        self._device_entry_id = None
        self._parent_id: str = raw_device['parentId'] if 'parentId' in raw_device.keys() else None
        self._name: str = raw_device['name'] if 'name' in raw_device.keys() else f"{self.model_name} {self.device_id}"
        self._rssi: int = raw_device['rssi'] if 'rssi' in raw_device.keys() else None

    @property
    def default_manufacturer(self) -> str:
        """Get the default_manufacturer."""
        return "Sunology"

    @property
    def manufacturer(self) -> str:
        """Get the manufacturer."""
        return "Sunology"
    
    @property
    def model_name(self) -> str:
        """Get the model."""
        return "Abstract"

    @property
    def name(self) -> str:
        """Get the name."""
        return self._name

    @property
    def via_device(self):
        """Get the unique id."""
        return (SUNOLOGY_DOMAIN, self._parent_id)

    @property
    def sw_version(self) -> str:
        """Get the software version."""
        return str(self._software_version)

    @property
    def hw_version(self) -> str:
        """Get the hardware version."""
        return str(self._hw_version)

    @property
    def device_id(self) -> str:
        """Get the device unique id."""
        return self._unique_id
    
    @property
    def unique_id(self):
        """Get the unique id."""
        return {(SUNOLOGY_DOMAIN, self._unique_id)}

    @property
    def device_entry_id(self):
        return self._device_entry_id
    
    @device_entry_id.setter
    def device_entry_id(self, device_entry_id):
        """ change auth_token """
        self._device_entry_id = device_entry_id

    @property
    def rssi(self):
        return self._rssi

    def update_product(self, raw_event):
        if 'rssi' in raw_event.keys():
            self._rssi = raw_event['rssi']
        
        if 'sw_version' in raw_event.keys():
            self._software_version = raw_event['swVersion']

    
    @property
    def device_info(self):
        """Return the device info."""
        dev_info = DeviceInfo(
            name=self.name,
            identifiers=self.unique_id,
            manufacturer=self.manufacturer,
            model=self.model_name,
            sw_version=self.sw_version,
            hw_version=self.hw_version,
            via_device=self.via_device if self._parent_id is not None else None
        )
        return dev_info

    def register(self, hass, entry) -> DeviceEntry :
        from homeassistant.helpers import device_registry as dr
        device_registry = dr.async_get(hass)

        return device_registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            **self.device_info
        )

class SolarEventInterface():
    """Sunology extra porperties for events."""
    def __init__(self, raw_device):
        pass
    
    @property
    def pvP(self):
        """Return the pvP value"""
        return self._pvP
    
    @property
    def miP(self):
        """Return the miP value"""
        return self._miP
    
    def solar_event_update(self, data):
        self._miP = data['miP']
        self._pvP = data['pvP']

class BatteryPackInterface():
    """Sunology extra porperties for events."""
    def __init__(self, raw_device):
        self._capacity = None
        self._maxInput = None
        self._maxOutput = None
    
    @property
    def capacity(self) -> int:
        """Get the capacity."""
        return self._capacity

    @capacity.setter
    def capacity(self, capacity):
        """Set the capacity."""
        self._capacity = capacity
    
    @property
    def maxInput(self) -> int:
        """Get the maxInput."""
        return self._maxInput
    
    @maxInput.setter
    def maxInput(self, maxInput):
        """Set the maxInput."""
        self._maxInput = maxInput

    @property
    def maxOutput(self) -> int:
        """Get the maxOutput."""
        return self._maxOutput
    
    @maxOutput.setter
    def maxOutput(self, maxOutput):
        """Set the maxInput."""
        self._maxOutput = maxOutput



class BatteryEventInterface():
    """Sunology extra porperties for events."""
    def __init__(self, raw_device):
        pass

    @property
    def batP(self):
        """Return the batP value"""
        return self._batP
    
    @property
    def batPct(self):
        """Return the batPct value"""
        return self._batPct
    
    @property
    def batTmp(self):
        """Return the batTmp value"""
        return self._batTmp
    
    def battery_event_update(self, data):
        """Return the miP value"""
        """ 
        """

        self._batP = data['batPow']
        self._batPct = data['batPct']
        self._batTmp = data['batTmp']


class PLAY(SunologyAbstractDevice, SolarEventInterface):
    """Home Assistant representation of a Sunology device PLAY."""

    def __init__(self, raw_play):
        """Initialize PLAYMax device."""
        super().__init__(raw_play)
        self._pvP = None
        self._miP = None

    @property
    def suggested_area(self) -> str:
        """Get the suggested_area."""
        return "Garden"
        
    @property
    def model_name(self) -> str:
        """Get the model name."""
        return "PLAY"
    
    @property
    def device_info(self):
        dev_info = super().device_info
        return dev_info


    def __str__(self) -> str:
        """Get string representation."""
        return f"Sunology Device: {self.name}::{self.model_name}::{self.unique_id}"

class StoreyMaster(SunologyAbstractDevice, BatteryPackInterface, BatteryEventInterface):
    """Home Assistant representation of a Sunology device PLAY."""

    def __init__(self, raw_storey):
        """Initialize PLAYMax device."""
        super().__init__(raw_storey)
        self._unique_id: str = f"{raw_storey['id']}"
        self._power = None
        self._percent = None


    @property
    def suggested_area(self) -> str:
        """Get the suggested_area."""
        return "Livinroom"
        
    @property
    def model_name(self) -> str:
        """Get the model name."""
        return "Storey Master"
    
    @property
    def device_info(self):
        dev_info = super().device_info
        return dev_info

    def __str__(self) -> str:
        """Get string representation."""
        return f"Sunology Device: {self.name}::{self.model_name}::{self.unique_id}"
    
    @property
    def power(self):
        """Return the power value"""
        return self._power

    @power.setter
    def power(self, power):
        """Set the power value"""
        self._power = power
    
    @property
    def percent(self):
        """Return the percent value"""
        return self._percent
    
    @percent.setter
    def percent(self, percent):
        """set the percent value"""
        self._percent = percent

class StoreyPack(SunologyAbstractDevice, BatteryPackInterface, BatteryEventInterface):
    """Home Assistant representation of a Sunology device PLAY."""

    def __init__(self, raw_storey_pack, pack_index):
        """Initialize PLAYMax device."""
        super().__init__(raw_storey_pack)
        self._unique_id: str = f"{raw_storey_pack['id']}#{pack_index}"
        self._parent_id: str = f"{raw_storey_pack['id']}"
        self._name: str = raw_storey_pack['name'] if 'name' in raw_storey_pack.keys() else f"{self.model_name} {self._unique_id}"


    @property
    def suggested_area(self) -> str:
        """Get the suggested_area."""
        return "Livinroom"
        
    @property
    def model_name(self) -> str:
        """Get the model name."""
        return "Storey Pack"
    
    @property
    def device_info(self):
        dev_info = super().device_info
        return dev_info

    def __str__(self) -> str:
        """Get string representation."""
        return f"Sunology Device: {self.name}::{self.model_name}::{self.unique_id}"

class PLAYMax(SunologyAbstractDevice, SolarEventInterface, BatteryEventInterface):
    """Home Assistant representation of a Sunology device PLAYMax."""

    def __init__(self, raw_playmax):
        """Initialize PLAYMax device."""
        super().__init__(raw_playmax)
        self._batP = None
        self._batPct = None
        self._batTmp = None
        self._pvP = None
        self._miP = None

    @property
    def suggested_area(self) -> str:
        """Get the suggested_area."""
        return "Garden"
        
    @property
    def model_name(self) -> str:
        """Get the model name."""
        return "PLAY Max"
    
    @property
    def device_info(self):
        dev_info = super().device_info
        return dev_info


    def __str__(self) -> str:
        """Get string representation."""
        return f"Sunology Device: {self.name}::{self.model_name}::{self.unique_id}"

class SmartMeter_ElectricalData():
    """Home Assistant representation of a Sunology SmartMeter_electrical_data property."""

    def __init__(self, current=None, voltage=None, power_factor=None, power=None, conso_tot=None, prod_tot=None):
        """Initialize SmartMeter_electrical_data property."""
        self._current = current
        self._voltage = voltage
        self._power_factor = power_factor
        self._power = power
        self._conso_tot = conso_tot
        self._prod_tot = prod_tot

    @property
    def current(self):
        """Get the current"""
        return self._current

    @property
    def voltage(self):
        """Get the voltage"""
        return self._voltage

    @property
    def power_factor(self):
        """Get the power_factor"""
        return self._power_factor

    @property
    def power(self):
        """Get the power"""
        return self._power

    @property
    def conso_tot(self):
        """Get the conso_tot"""
        return self._conso_tot

    @property
    def prod_tot(self):
        """Get the prod_tot"""
        return self._prod_tot
    
    def update_electrical_data(self, raw_electrical_data):
        if 'current' in raw_electrical_data.keys():
            self._current = raw_electrical_data['current']
        if 'voltage' in raw_electrical_data.keys():
            self._voltage = raw_electrical_data['voltage']
        if 'powerFactor' in raw_electrical_data.keys():
            self._power_factor = raw_electrical_data['powerFactor']
        if 'power' in raw_electrical_data.keys():
            self._power = raw_electrical_data['power']
        if 'consoTot' in raw_electrical_data.keys():
            self._conso_tot = raw_electrical_data['consoTot']
        if 'prodTot' in raw_electrical_data.keys():
            self._prod_tot = raw_electrical_data['prodTot']

class SmartMeter_IndexesErl():
    """Home Assistant representation of a Sunology SmartMeter_IndexesErl property."""

    def __init__(self):
        """Initialize SmartMeter_electrical_data property."""
        self._contract = None
        self._current_tarif = None
        self._energy_consumed_total = None
        self._energy_produced_total = None
        self._energy_consumed_indexed = {
            SmartMeterTarifIndex.INDEX_1: None,
            SmartMeterTarifIndex.INDEX_2: None,
            SmartMeterTarifIndex.INDEX_3: None,
            SmartMeterTarifIndex.INDEX_4: None,
            SmartMeterTarifIndex.INDEX_5: None,
            SmartMeterTarifIndex.INDEX_6: None,
            SmartMeterTarifIndex.INDEX_7: None,
            SmartMeterTarifIndex.INDEX_8: None,
            SmartMeterTarifIndex.INDEX_9: None,
            SmartMeterTarifIndex.INDEX_10: None
        }

    @property
    def contract(self):
        """get the contract"""
        return self._contract

    @property
    def current_tarif(self):
        """get the current_tarif"""
        return self._current_tarif

    @property
    def energy_consumed_total(self):
        """get the energy_consumed_total"""
        return self._energy_consumed_total

    @property
    def energy_produced_total(self):
        """get the energy_produced_total"""
        return self._energy_produced_total

    @property
    def energy_consumed_indexed(self):
        """get the energy_consumed_indexed"""
        return self._energy_consumed_indexed

    def update_indexes_erl(self, raw_indexes_erl):
        if 'contract' in raw_indexes_erl.keys():
            self._contract = raw_indexes_erl['contract']
        if 'currentTarif' in raw_indexes_erl.keys():
            self._current_tarif = raw_indexes_erl['currentTarif']
        if 'energyConsumedTotal' in raw_indexes_erl.keys():
            self._energy_consumed_total = raw_indexes_erl['energyConsumedTotal']
        if 'energyProducedTotal' in raw_indexes_erl.keys():
            self._energy_produced_total = raw_indexes_erl['energyProducedTotal']
        if 'energyConsumedIdx1' in raw_indexes_erl.keys():
            self._energy_consumed_indexed[SmartMeterTarifIndex.INDEX_1] = raw_indexes_erl['energyConsumedIdx1']
        if 'energyConsumedIdx2' in raw_indexes_erl.keys():
            self._energy_consumed_indexed[SmartMeterTarifIndex.INDEX_2] = raw_indexes_erl['energyConsumedIdx2']
        if 'energyConsumedIdx3' in raw_indexes_erl.keys():
            self._energy_consumed_indexed[SmartMeterTarifIndex.INDEX_3] = raw_indexes_erl['energyConsumedIdx3']
        if 'energyConsumedIdx4' in raw_indexes_erl.keys():
            self._energy_consumed_indexed[SmartMeterTarifIndex.INDEX_4] = raw_indexes_erl['energyConsumedIdx4']
        if 'energyConsumedIdx5' in raw_indexes_erl.keys():
            self._energy_consumed_indexed[SmartMeterTarifIndex.INDEX_5] = raw_indexes_erl['energyConsumedIdx5']
        if 'energyConsumedIdx6' in raw_indexes_erl.keys():
            self._energy_consumed_indexed[SmartMeterTarifIndex.INDEX_6] = raw_indexes_erl['energyConsumedIdx6']
        if 'energyConsumedIdx7' in raw_indexes_erl.keys():
            self._energy_consumed_indexed[SmartMeterTarifIndex.INDEX_7] = raw_indexes_erl['energyConsumedIdx7']
        if 'energyConsumedIdx8' in raw_indexes_erl.keys():
            self._energy_consumed_indexed[SmartMeterTarifIndex.INDEX_8] = raw_indexes_erl['energyConsumedIdx8']
        if 'energyConsumedIdx9' in raw_indexes_erl.keys():
            self._energy_consumed_indexed[SmartMeterTarifIndex.INDEX_9] = raw_indexes_erl['energyConsumedIdx9']
        if 'energyConsumed_Ix10' in raw_indexes_erl.keys():
            self._energy_consumed_indexed[SmartMeterTarifIndex.INDEX_10] = raw_indexes_erl['energyConsumedIdx10']


class LinkyTransmitter(SunologyAbstractDevice):
    """Home Assistant representation of a Sunology device Smart."""

    def __init__(self, raw_smartmeter):
        """Initialize LinkyTransmitter device."""
        super().__init__(raw_smartmeter)
        self._app_power_usage = None
        self._app_power_prod = None
        self._indexes_erl = SmartMeter_IndexesErl()

    @property
    def app_power_usage(self):
        """Get the app_power_usage."""
        return self._app_power_usage

    @property
    def app_power_prod(self):
        """Get the app_power_usage."""
        return self._app_power_prod

    @property
    def suggested_area(self) -> str:
        """Get the suggested_area."""
        return "Garage"
        
    @property
    def model_name(self) -> str:
        """Get the model name."""
        return "Linky Transmitter"
    
    @property
    def device_info(self):
        dev_info = super().device_info
        return dev_info

    @property
    def indexes_erl(self):
        """Get the electrical_data"""
        return self._indexes_erl

    def update_gridevent(self, raw_grid_event):
        if "appPowerUsage" in raw_grid_event.keys():
            self._app_power_usage = raw_grid_event['appPowerUsage']
        if "appPowerProd" in raw_grid_event.keys():
            self._app_power_prod = raw_grid_event['appPowerProd']
        if "indexesErl" in raw_grid_event.keys():
            self.indexes_erl.update_indexes_erl(raw_grid_event['indexesErl'])

    def __str__(self) -> str:
        """Get string representation."""
        return f"Sunology Device: {self.name}::{self.model_name}::{self.unique_id}"

class SmartMeter_3P(SunologyAbstractDevice):
    """Home Assistant representation of a Sunology device Smart."""

    def __init__(self, raw_smartmeter):
        """Initialize SmartMeter_3 device."""
        super().__init__(raw_smartmeter)
        self._freq = None
        self._electrical_data = {
            SmartMeterPhase.ALL:       SmartMeter_ElectricalData(),
            SmartMeterPhase.PHASE_1:   SmartMeter_ElectricalData(),
            SmartMeterPhase.PHASE_2:   SmartMeter_ElectricalData(),
            SmartMeterPhase.PHASE_3:   SmartMeter_ElectricalData()
        }

    @property
    def suggested_area(self) -> str:
        """Get the suggested_area."""
        return "Garden"
        
    @property
    def model_name(self) -> str:
        """Get the model name."""
        return "STREAM Meter"
    
    @property
    def device_info(self):
        dev_info = super().device_info
        return dev_info

    @property
    def freq(self):
        """Get the frequency"""
        return self._freq
    
    @property
    def electrical_data(self):
        """Get the electrical_data"""
        return self._electrical_data

    def update_gridevent(self, raw_grid_event):
        if "freq" in raw_grid_event.keys():
            self._freq = raw_grid_event['freq']
        if "electricalData" in raw_grid_event.keys():
            self.electrical_data[SmartMeterPhase.ALL].update_electrical_data(raw_grid_event['electricalData'])
        if "electricalDataP1" in raw_grid_event.keys():
            self.electrical_data[SmartMeterPhase.PHASE_1].update_electrical_data(raw_grid_event['electricalDataP1'])
        if "electricalDataP2" in raw_grid_event.keys():
            self.electrical_data[SmartMeterPhase.PHASE_2].update_electrical_data(raw_grid_event['electricalDataP2'])
        if "electricalDataP3" in raw_grid_event.keys():
            self.electrical_data[SmartMeterPhase.PHASE_3].update_electrical_data(raw_grid_event['electricalDataP3'])

    def __str__(self) -> str:
        """Get string representation."""
        return f"Sunology Device: {self.name}::{self.model_name}::{self.unique_id}"

class Gateway(SunologyAbstractDevice):
    """Home Assistant representation of a Sunology device PLAYMax."""

    def __init__(self, raw_gateway):
        """Initialize Gateway device."""        
        super().__init__(raw_gateway)

    @property
    def suggested_area(self) -> str:
        """Get the suggested_area."""
        return "Linving room"
        
    @property
    def model_name(self) -> str:
        """Get the model name."""
        name = "STREAM Connect"
        return name
    

    @property
    def device_info(self):
        dev_info = super().device_info
        return dev_info


    def __str__(self) -> str:
        """Get string representation."""
        return f"Sunology Device: {self.name}::{self.model_name}::{self.unique_id}"

