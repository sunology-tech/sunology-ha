"""Home Assistant representation of an Sunology device."""
from .const import DOMAIN as SUNOLOGY_DOMAIN
from homeassistant.helpers.device_registry import DeviceInfo, DeviceEntry


class SunologyAbstractDevice():
    """Home Assistant representation of a Sunology abstract device."""

    def __init__(self, raw_device):
        """Initialize PLAYMax device."""
        self._unique_id: str = raw_device['id']
        self._software_version: str = raw_device['sw_version']
        self._hw_version: str = raw_device['hw_version']
        self._device_entry_id = None
        self._parent_id: str = raw_device['parent_id'] if 'parent_id' in raw_device.keys() else None
        self._name: str = raw_device['name'] if 'name' in raw_device.keys() else f"{self.model_name} {self.device_id}"

    
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
        self._capacity = 0
        self._maxInput = 0
        self._maxOutput = 0
    
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

        self._batP = data['batP']
        self._batPct = data['batPct']
        self._batTmp = data['batTmp']


class PLAY(SunologyAbstractDevice, SolarEventInterface):
    """Home Assistant representation of a Sunology device PLAY."""

    def __init__(self, raw_play):
        """Initialize PLAYMax device."""
        super().__init__(raw_play)
        self._pvP = 0
        self._miP = 0

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
        self._power = 0
        self._percent = 0


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
        self._batP = 0
        self._batPct = 0
        self._batTmp = 0
        self._pvP = 0
        self._miP = 0


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

class Gateway(SunologyAbstractDevice):
    """Home Assistant representation of a Sunology device PLAYMax."""

    def __init__(self, raw_gateway):
        """Initialize PLAYMax device."""        
        super().__init__(raw_gateway)

    @property
    def suggested_area(self) -> str:
        """Get the suggested_area."""
        return "Linving room"
        
    @property
    def model_name(self) -> str:
        """Get the model name."""
        name = "E-Hub"
        return name
    

    @property
    def device_info(self):
        dev_info = super().device_info
        return dev_info


    def __str__(self) -> str:
        """Get string representation."""
        return f"Sunology Device: {self.name}::{self.model_name}::{self.unique_id}"

