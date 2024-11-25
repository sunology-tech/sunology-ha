"""Home Assistant representation of an Sunology device."""
from .const import DOMAIN as SUNOLOGY_DOMAIN


class SunologyAbstractDevice:
    """Home Assistant representation of a Sunology abstract device."""

    def __init__(self, raw_device):
        """Initialize PLAYMax device."""
        self._name: str = raw_device.name
        self._unique_id: str = raw_device.id
        self._software_version: str = raw_device.sw_version
        self._hw_version: str = raw_device.hw_version
        self._parent_id: str = raw_device.parent_id

    
    @property
    def default_manufacturer(self) -> str:
        """Get the default_manufacturer."""
        return "Sunology"

    @property
    def manufacturer(self) -> str:
        """Get the manufacturer."""
        return "Sunology"
        

    @property
    def name(self) -> str:
        """Get the name."""
        return self._name

    @property
    def via_device(self) -> str:
        """Get the unique id."""
        return (GEORIDE_DOMAIN, self._parent_id)

    
    @property
    def sw_version(self) -> str:
        """Get the software version."""
        return str(self._software_version)

    @property
    def hw_version(self) -> str:
        """Get the hardware version."""
        return str(self._hw_version)

    @property
    def unique_id(self) -> str:
        """Get the unique id."""
        return {(SUNOLOGY_DOMAIN, self._unique_id)}

    
    @property
    def device_info(self):
        """Return the device info."""
        dev_info = {
            "name": self.name,
            "identifiers": self.unique_id,
            "manufacturer": self.manufacturer,
            "sw_version" : self.sw_version,
            "hw_version": self.hw_version
        }

        if self._parent_id is not None:
            dev_info['via_device'] = self.unique_id

        return dev_info

class SolarEventInterface():
    """Sunology extra porperties for events."""
    def __init__(self):
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
        dev_info["model"] = self.model_name
        dev_info["suggested_area"] =  self.suggested_area
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
        dev_info["model"] = self.model_name
        dev_info["suggested_area"] =  self.suggested_area
        return dev_info


    def __str__(self) -> str:
        """Get string representation."""
        return f"Sunology Device: {self.name}::{self.model_name}::{self.unique_id}"
