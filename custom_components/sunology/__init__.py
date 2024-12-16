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
    Gateway,
    SunologyAbstractDevice,
    SolarEventInterface
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
            ##await self.call_refresh_device() //All iss async, not needed
            #TODO: DELETE-Me mock
            await self._socket.mock_messages_one_shot()

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
            device = None
            match product_data['product_name']:
                case "PLAYMax":
                    device = PLAYMax(product_data)
                case "E-Hub":
                    device = Gateway(product_data)
                case _:
                    _LOGGER.warning("Unmanaged device receive on device_event")
                    device = SunologyAbstractDevice(product_data)
            self._sunology_devices.append(device)

            #asyncio.run_coroutine_threadsafe(
            device.register(self.hass, self._entry) #, self._hass.loop
            #).result()
            self.hass.add_job(
                self.hass.config_entries.async_forward_entry_setups, self._entry, ["sensor"]
            )
            #asyncio.run_coroutine_threadsafe(
            #self.hass.config_entries.async_forward_entry_setups(self._entry, ["sensor"])#, self._hass.loop
            #).result() 

            #device.register(self.hass, self._entry)
            coordinator = self.add_device_to_coordinator(device)


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
                else:
                    _LOGGER.info("Solar event receive on non solar device")

                event_data = {
                    "device_id": device.unique_id,
                    "device_name": device.name,
                }
                
                #asyncio.run_coroutine_threadsafe(
                #    self._hass.bus.async_fire(f"{DOMAIN}_solarEvent", event_data), self._hass.loop
                #).result()
                asyncio.run_coroutine_threadsafe(
                    coordinator.async_request_refresh(), self._hass.loop
                ).result()
                break
    
    @callback
    def on_batteryEvent_callback(self, data):
        """on batteryEvent callback"""
        _LOGGER.info("On batteryEvent received")

    
    @callback
    def on_gridEvent_callback(self, data):
        """on gridEvent callback"""
        _LOGGER.info("On gridEvent received")


