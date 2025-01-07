"""Home Assistant representation of an Sunology device."""
from .const import DOMAIN as SUNOLOGY_DOMAIN
from homeassistant.helpers.device_registry import DeviceInfo, DeviceEntry


class SunologyAbstractDevice():
    """Home Assistant representation of a Sunology abstract device."""

    def __init__(self, raw_device):
        """Initialize PLAYMax device."""
        self._name: str = raw_device['name'] if 'name' in raw_device.keys() else f"Sun {raw_device['id']}"
        self._unique_id: str = raw_device['id']
        self._software_version: str = raw_device['sw_version']
        self._hw_version: str = raw_device['hw_version']
        self._device_entry_id = None
        self._parent_id: str = raw_device['parent_id'] if 'parent_id' in raw_device.keys() else None

    
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
        return {(SUNOLOGY_DOMAIN, self._parent_id)}

    
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
            hw_version=self.hw_version
        )

        if self._parent_id is not None:
            dev_info.via_device = {(SUNOLOGY_DOMAIN, self.parent_id)}
        return dev_info

    def register(self, hass, entry) -> DeviceEntry :
        from homeassistant.helpers import device_registry as dr
        device_registry = dr.async_get(hass)

        return device_registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            name=self.name,
            identifiers=self.unique_id,
            manufacturer=self.manufacturer,
            model=self.model_name,
            sw_version= self.sw_version,
            hw_version=self.hw_version
        )



class SolarEventInterface():
    """Sunology extra porperties for events."""
    def __init__(self, raw_device):
        self._pvP = 0
        self._miP = 0
    
    @property
    def pvP(self):
        """Return the pvP value"""
        return self._pvP
    
    @property
    def miP(self):
        """Return the miP value"""
        return self._miP
    
    def solar_event_update(self, data):
        """Return the miP value"""
        """ 
            "pvP": 100.05,
            "miP": 88,
            "batTmp": 21.25, --> Deprecated
            "batP": 12.05, --> Deprecated
            "batPct": 99, --> Deprecated
            "time": 1688043930 --> Unused
        """

        self._miP = data['miP']
        self._miP = data['pvP']

    


class PLAYMax(SunologyAbstractDevice, SolarEventInterface):
    """Home Assistant representation of a Sunology device PLAYMax."""

    def __init__(self, raw_playmax):
        """Initialize PLAYMax device."""
        super().__init__(raw_playmax)

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
        super().__init__(raw_playmax)

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

