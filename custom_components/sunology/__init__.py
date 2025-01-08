""" sunology custom conpennt """
from collections import defaultdict

import asyncio
import logging
from typing import Any, Mapping
from datetime import timedelta
import math
import time
import json
from threading import Thread
import voluptuous as vol
import jwt

from aiohttp.web import json_response

from homeassistant import config_entries
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv
import homeassistant.helpers.event as ha_event

from homeassistant.setup import async_when_setup
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

import threading


from .socket import SunologySocket
from .device import (
    PLAYMax,
    PLAY,
    Gateway,
    StoreyMaster,
    StoreyPack,
    SunologyAbstractDevice,
    SolarEventInterface,
    BatteryEventInterface
)
from .sensor import(
    SunologMiPowerSensorEntity,
    SunologPvPowerSensorEntity
)

from .const import (
    CONF_GATEWAY_IP,
    MIN_UNTIL_REFRESH,
    DOMAIN,
    PACKAGE_NAME
)

_LOGGER = logging.getLogger(PACKAGE_NAME)

CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(DOMAIN, default={}): {
            vol.Optional(CONF_GATEWAY_IP): vol.All(str, vol.Length(min=3)),
        }
    },
    extra=vol.ALLOW_EXTRA,
)

async def async_setup(hass, config):
    """Setup  Sunology component."""
    hass.data[DOMAIN] = {"config": config[DOMAIN], "devices": {}, "unsub": None}
    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN,
            context={
                "source": config_entries.SOURCE_IMPORT
            },
            data={}
        )
    )

    # Return boolean to indicate that initialization was successful.
    return True

async def async_setup_entry(hass, entry):
    """Set up Sunology entry."""
    config = hass.data[DOMAIN]["config"]
    gateway_ip = config.get(CONF_GATEWAY_IP) or entry.data[CONF_GATEWAY_IP]
    context = SunologyContext(
        hass,
        entry,
        gateway_ip
    )

    _LOGGER.info("Context-setup and start the thread")
    _LOGGER.info("Thread started")

    hass.data[DOMAIN]["context"] = context

    # We add device to the context
    await context.init_context(hass)

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True


async def async_unload_entry(hass, entry):
    """Unload an Sunology config entry."""

    await hass.config_entries.async_forward_entry_unload(entry, "sensor")

    context = hass.data[DOMAIN]["context"]
    context.socket.disconnect() # Disconnect only if all devices is disabled

    return True

async def async_remove_config_entry_device(hass, config_entry, device_entry) -> bool:
    """Remove an Sunology device entry."""
    return True



class SunologyContext:
    """Hold the current Sunology context."""

    def __init__(self, hass, entry, gateway_ip):
        """Initialize an Sunology context."""
        self._hass = hass
        self._entry = entry
        self._gateway_ip = gateway_ip
        self._sunology_devices = []
        self._sunology_devices_coordoned = []
        self._socket = None
        self._thread_started = False
        self._socket_thread = None
        self._previous_refresh = math.floor(time.time()/60)
    @property
    def hass(self):
        """ hass """
        return self._hass

    @property
    def gateway_ip(self):
        """ current gateway_ip """
        return self._gateway_ip

    @property
    def sunology_devices(self):
        """ Sunology devices list """
        return self._sunology_devices

    @sunology_devices.setter
    def sunology_devices(self, devices):
        """ Sunology devices list """
        self._sunology_devices = devices

    def connect_socket(self):
        """subscribe to Sunology socket"""
        _LOGGER.info("Sunology socket creation")
        socket = SunologySocket()
        socket.subscribe_on_productInfo(self.on_productInfo_callback)
        socket.subscribe_on_solarEvent(self.on_solarEvent_callback)
        socket.subscribe_on_batteryEvent(self.on_batteryEvent_callback)
        socket.subscribe_on_gridEvent(self.on_gridEvent_callback)

        self._socket = socket
        # asyncio.run_coroutine_threadsafe(
        #     self._hass.async_create_task(socket.mock_messages_one_shot()), self._hass.loop
        # )

        self._socket_thread = threading.Thread(target=asyncio.run, args=(socket.connect(f"ws://{self.gateway_ip}/ws", None),))
        self._socket_thread.start()

        oneshot_event_thread = threading.Thread(target=asyncio.run, args=(socket.mock_messages_forever(),))
        oneshot_event_thread.start()



    async def get_device(self, device_id):
        """ here we return last device by id"""
        for device in self._sunology_devices:
            if device.unique_id == device_id:
                return device
        return {}


    async def init_context(self, hass):
        """Used to refresh the device list"""
        _LOGGER.info("Init_context")
        update_interval = timedelta(minutes=MIN_UNTIL_REFRESH)

        if not self._thread_started:
            _LOGGER.info("Start the thread")
            # We refresh the tracker list each hours
            self._thread_started = True
            self.connect_socket()

        for device in self._sunology_devices:
            coordinator = DataUpdateCoordinator[Mapping[str, Any]](
                hass,
                _LOGGER,
                name=device.name,
                update_method=self.refresh_devices,
                update_interval=update_interval
            )

            coordoned_device = {
                "device": device,
                "coordinator": coordinator
            }
            self._sunology_devices_coordoned.append(coordoned_device)
        
    
    def add_devices_to_coordinator(self, devices):
        for device in devices:
            self.add_device_to_coordinator(device)
        
    
    def add_device_to_coordinator(self, device: SunologyAbstractDevice):
        update_interval = timedelta(minutes=MIN_UNTIL_REFRESH)
        coordinator = DataUpdateCoordinator[Mapping[str, Any]](
            self._hass,
            _LOGGER,
            name=device.name,
            update_method=self.refresh_devices,
            update_interval=update_interval
        )

        coordoned_device = {
            "device": device,
            "coordinator": coordinator
        }
        self._sunology_devices_coordoned.append(coordoned_device)
        return coordinator

    async def refresh_devices(self):
            """ here we return last device by id"""
            _LOGGER.debug("Call refresh devices")
            epoch_min = math.floor(time.time()/60)
            if epoch_min != self._previous_refresh:
                self._previous_refresh = epoch_min
                ##await self.call_refresh_device() //All is async, not needed
                entities = []
                for device_coordoned in self._sunology_devices_coordoned:
                    device_entry = device_coordoned['device'].register(self.hass, self._entry)
                    device_coordoned['device'].device_entry_id =  device_entry.id

                for entity in entities:
                    entity.register(self.hass, self._entry)

                await self.hass.config_entries.async_forward_entry_unload(self._entry, "sensor")
                await self.hass.config_entries.async_forward_entry_setups(self._entry, ["sensor"])#, self._hass.loop

                #TODO: DELETE-Me mock
                # When calling a blocking function inside Home Assistant
                await self.hass.async_add_executor_job(self._socket.mock_messages_one_shot)

    @property
    def sunology_devices_coordoned(self):
        """Return coordoned device"""
        return self._sunology_devices_coordoned


    @property
    def socket(self):
        """ hold the Sunology socket """
        return self._socket

    @socket.setter
    def socket(self, socket):
        """set the Sunology socket"""
        self._socket = socket

   
    @callback
    def on_productInfo_callback(self, product_data):
        """on device callback"""
        _LOGGER.info("On device received '%s'", product_data['product_name'])
        found = False
        for device in self._sunology_devices:
            if device.device_id == product_data['id']:
                found = True
        if not found:
            devices = []
            match product_data['product_name']:
                case "PLAYMax":
                    devices.append(PLAYMax(product_data))
                case "PLAY":
                    devices.append(PLAY(product_data))
                case "EHub":
                    devices.append(Gateway(product_data))
                case "Storey":
                    master = StoreyMaster(product_data)
                    for pack in product_data['hardware_configuration']['packs']:
                        if pack['packIndex'] == 0:
                            master.capacity = pack['capacity']
                            master.maxInput = pack['maxInput']
                            master.maxOutput = pack['maxOutput']
                        else:
                            st_pack = StoreyPack(product_data, pack['packIndex'])
                            st_pack.capacity = pack['capacity']
                            st_pack.maxInput = pack['maxInput']
                            st_pack.maxOutput = pack['maxOutput']
                            devices.append(st_pack)

                    devices.append(master)

                case _:
                    _LOGGER.warning("Unmanaged device receive on device_event")
                    devices.append(SunologyAbstractDevice(product_data))
            self._sunology_devices.extend(devices)
            coordinator = self.add_devices_to_coordinator(devices)


    @callback
    def on_solarEvent_callback(self, data):
        """on solarEvent callback"""
        _LOGGER.info("On solarEvent received")
        for coordoned_device in self._sunology_devices_coordoned:
            device = coordoned_device['device']
            coordinator = coordoned_device['coordinator']
            if device.device_id == data['id']:
                if isinstance(device, SolarEventInterface):
                    device.solar_event_update(data)
                if isinstance(device, BatteryEventInterface):
                    device.battery_event_update(data)

                else:
                    _LOGGER.info("Solar event receive on non solar device")
                

                event_data = {
                    "device_id": device.unique_id,
                    "device_name": device.name,
                }
                
                asyncio.run_coroutine_threadsafe(
                    coordinator.async_request_refresh(), self._hass.loop
                ).result()
                break
    
    @callback
    def on_batteryEvent_callback(self, data):
        """on batteryEvent callback"""
        _LOGGER.info("On batteryEvent received")
        for coordoned_device in self._sunology_devices_coordoned:
            device = coordoned_device['device']
            coordinator = coordoned_device['coordinator']
            if device.device_id == data['id']:
                if isinstance(device, StoreyMaster):
                    device.percent = data['pct']
                    device.power = data['power']
                    for pack in data['packs']:
                        if pack['packIndex'] == 0:
                            device.battery_event_update(pack)
                        else:
                            for sub_coordoned_device in self._sunology_devices_coordoned:
                                sub_device = sub_coordoned_device['device']
                                if sub_device.device_id == f"{data['id']}#{pack['packIndex'] }":
                                    sub_device.battery_event_update(pack)
                                    break
                else:
                    _LOGGER.info("Solar event receive on non storey master device")
                            
                asyncio.run_coroutine_threadsafe(
                    coordinator.async_request_refresh(), self._hass.loop
                ).result()
                break

    
    @callback
    def on_gridEvent_callback(self, data):
        """on gridEvent callback"""
        _LOGGER.info("On gridEvent received")


