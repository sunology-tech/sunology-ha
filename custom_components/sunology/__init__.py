""" sunology custom conpennt """
from collections import defaultdict

import asyncio
import logging
from typing import Any, Mapping
from datetime import timedelta
from homeassistant.components import zeroconf
from zeroconf import AddressResolver, IPVersion, Zeroconf
from zeroconf.asyncio import AsyncZeroconf
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
    BatteryEventInterface,
    SmartMeter_3P,
    LinkyTransmitter
)

from .const import (
    CONF_GATEWAY_HOST,
    CONF_GATEWAY_PORT,
    MIN_UNTIL_REFRESH,
    DOMAIN,
    PACKAGE_NAME
)

_LOGGER = logging.getLogger(PACKAGE_NAME)

CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(DOMAIN, default={}): {
            vol.Optional(CONF_GATEWAY_HOST): vol.All(str, vol.Length(min=3)),
            vol.Optional(CONF_GATEWAY_PORT): vol.All(int, vol.Range(min=1, max=65535))
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
    gateway_host = config.get(CONF_GATEWAY_HOST) or entry.data[CONF_GATEWAY_HOST] if CONF_GATEWAY_HOST in entry.data.keys() else None
    gateway_port = config.get(CONF_GATEWAY_PORT) or entry.data[CONF_GATEWAY_PORT] if CONF_GATEWAY_PORT in entry.data.keys() else None
    context = SunologyContext(
        hass,
        entry,
        gateway_host,
        gateway_port
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

    def __init__(self, hass, entry, gateway_host, gateway_port):
        """Initialize an Sunology context."""
        self._hass = hass
        self._entry = entry
        self._gateway_host = gateway_host
        self._gateway_port = gateway_port

        self._sunology_devices = []
        self._sunology_devices_coordoned = []
        self._socket = None
        self._thread_started = False
        self._socket_thread = None
        self._connection_atempt = 0
        self._previous_refresh = math.floor(time.time()/60)
    @property
    def hass(self):
        """ hass """
        return self._hass

    @property
    def gateway_host(self):
        """ current gateway_host """
        return self._gateway_host
    
    @property
    def gateway_port(self):
        """ current gateway_port """
        return self._gateway_port

    @property
    def sunology_devices(self):
        """ Sunology devices list """
        return self._sunology_devices

    @sunology_devices.setter
    def sunology_devices(self, devices):
        """ Sunology devices list """
        self._sunology_devices = devices

    async def _async_connect(self, socket, host, port, token):
        """connect to Sunology socket"""
        _LOGGER.info("Sunology socket connection")
        host_ip = host
        if host.endswith('.local') or host.endswith('.local.'):
            _LOGGER.debug(f"Resolve {host}")
            zc = await zeroconf.async_get_instance(self._hass)
            await zc.async_wait_for_start()
            resolver = AddressResolver(host)
            if await resolver.async_request(zc, 3000):
                host_ip_obj = resolver.ip_addresses_by_version(IPVersion.All)
                host_ip = str(host_ip_obj[0])
                _LOGGER.debug(f"{host} IP addresses: {host_ip}")
            else:
                _LOGGER.error(f"Name {host} not resolved")
        await socket.connect(host_ip, port, None)
        

    def connect_socket(self):
        """subscribe to Sunology socket"""
        _LOGGER.info("Sunology socket creation")
        socket = SunologySocket()
        socket.subscribe_on_productInfo(self.on_productInfo_callback)
        socket.subscribe_on_solarEvent(self.on_solarEvent_callback)
        socket.subscribe_on_batteryEvent(self.on_batteryEvent_callback)
        socket.subscribe_on_gridEvent(self.on_gridEvent_callback)

        socket.subscribe_on_connect(self.on_connect_callback)
        socket.subscribe_on_diconnect(self.on_disconnect_callback)

        self._socket = socket

        asyncio.run_coroutine_threadsafe(
            self._async_connect(socket, self.gateway_host, self.gateway_port, None), self._hass.loop
        )

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
    
    def remove_devices_from_coordinator(self, device: SunologyAbstractDevice):
        for coordoned_device in self._sunology_devices_coordoned:
            if device['device'].unique_id == coordoned_device['device'].unique_id:
                self._sunology_devices_coordoned.pop(coordoned_device)

    async def refresh_devices(self):
        """ here we return last device by id"""
        _LOGGER.debug("Call refresh devices")
        epoch_min = math.floor(time.time()/60)
        if not self.socket.is_connected:
            _LOGGER.info("Socket not connected detected, atempt: %s", self._connection_atempt)
            asyncio.run_coroutine_threadsafe(
                self._async_connect(self.socket, self.gateway_host, self.gateway_port, None), self._hass.loop
            )
            self._connection_atempt+=1

        if epoch_min != self._previous_refresh:
            self._previous_refresh = epoch_min
            entities = []
            for device_coordoned in self._sunology_devices_coordoned:
                device_entry = device_coordoned['device'].register(self.hass, self._entry)
                device_coordoned['device'].device_entry_id =  device_entry.id

            for entity in entities:
                entity.register(self.hass, self._entry)

            await self.hass.config_entries.async_forward_entry_unload(self._entry, "sensor")
            await self.hass.config_entries.async_forward_entry_setups(self._entry, ["sensor"])#, self._hass.loop

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
        _LOGGER.info("On device received '%s'", product_data['productName'])
        found = False
        for coordoned_device in self._sunology_devices_coordoned:
            if 'device' not in coordoned_device.keys():
                device = coordoned_device['device']
                if device.device_id == product_data['id']:
                    device.update_product(product_data)
                    found = True
                    if product_data['productName'] == "STOREY":
                        new_packs = []
                        for sub_device in self._sunology_devices:
                            if isinstance(sub_device, StoreyPack) and sub_device.device_id.split("#")[0] == device.device_id:
                                pack_index = int(device_id.split("#")[1])
                                if pack_index + 1 > product_data['packsCount']:
                                    self._sunology_devices.pop(sub_device)
                                    self.remove_devices_from_coordinator(sub_device)
                        
                        for pack in product_data['packs']:
                            pack_found = False
                            for sub_device in self._sunology_devices:
                                if sub_device.device_id == f"{product_data['id']}#{pack['packIndex']}":
                                    pack_found = True
                                    sub_device.update_product(product_data)
                                    break
                            if not pack_found:
                                st_pack = StoreyPack(product_data, pack['packIndex'])
                                st_pack.capacity = pack['capacity']
                                st_pack.maxInput = pack['maxCons']
                                st_pack.maxOutput = pack['maxProd']
                                new_packs.append(st_pack)
                        self._sunology_devices.extend(new_packs)
                        coordinator = self.add_devices_to_coordinator(new_packs)
                    break
        if not found:
            devices = []
            match product_data['productName']:
                case "PLAY_MAX":
                    devices.append(PLAYMax(product_data))
                case "PLAY":
                    devices.append(PLAY(product_data))
                case "STREAM_CONNECT":
                    devices.append(Gateway(product_data))
                    if "devices" in product_data.keys():
                        for hub_device in product_data['devices']:
                            self.on_productInfo_callback(hub_device)
                case "STOREY":
                    master = StoreyMaster(product_data)

                    master.capacity = product_data['battery']['capacity']
                    master.maxInput = product_data['battery']['maxCons']
                    master.maxOutput = product_data['battery']['maxProd']
                    for pack in product_data['packs']:
                        # if pack['packIndex'] == 1:
                        #     master.capacity = pack['capacity']
                        #     master.maxInput = pack['maxCons']
                        #     master.maxOutput = pack['maxProd']
                        # else:
                            st_pack = StoreyPack(product_data, pack['packIndex'])
                            st_pack.capacity = pack['capacity']
                            st_pack.maxInput = pack['maxCons']
                            st_pack.maxOutput = pack['maxProd']
                            devices.append(st_pack)
                    devices.append(master)
                case "STREAM_METER":
                    devices.append(SmartMeter_3P(product_data))
                case "ERL_GEN2":
                    devices.append(LinkyTransmitter(product_data))
                    
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
                else:
                    _LOGGER.info("Solar event receive on non solar device")
                
                if isinstance(device, BatteryEventInterface):
                    device.battery_event_update(data)
                

                event_data = {
                    "device_id": device.unique_id,
                    "device_name": device.name,
                }
                if 'device_entities' in coordoned_device.keys():
                    for entity in coordoned_device['device_entities']:
                        _LOGGER.debug('Update entity %s', entity.entity_id)
                        entity.schedule_update_ha_state(force_refresh=False)
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
                    device.status = data['status']
                    device.acVoltage = data['acVoltage']
                    device.battery_event_update(data['battery'])
                    
                    for entity in coordoned_device['device_entities']:
                        _LOGGER.debug('Update entity %s', entity.entity_id)
                        entity.schedule_update_ha_state(force_refresh=False)

                    for pack in data['packs']:
                            for sub_coordoned_device in self._sunology_devices_coordoned:
                                sub_device = sub_coordoned_device['device']
                                if sub_device.device_id == f"{data['id']}#{pack['packIndex'] }":
                                    sub_device.battery_event_update(pack)
                                    for entity in sub_coordoned_device['device_entities']:
                                        _LOGGER.debug('Update entity %s', entity.entity_id)
                                        entity.schedule_update_ha_state(force_refresh=False)
                                    break
                else:
                    _LOGGER.info("Solar event receive on non storey master device")
                break

    
    @callback
    def on_gridEvent_callback(self, data):
        """on gridEvent callback"""
        _LOGGER.info("On gridEvent received")
        for coordoned_device in self._sunology_devices_coordoned:
            device = coordoned_device['device']
            coordinator = coordoned_device['coordinator']
            if device.device_id == data['id']:
                if isinstance(device, (SmartMeter_3P, LinkyTransmitter)):
                    device.update_gridevent(data)
                    for entity in coordoned_device['device_entities']:
                        _LOGGER.debug('Update entity %s', entity.entity_id)
                        entity.schedule_update_ha_state(force_refresh=False)
                else:
                    _LOGGER.info("Grid event receive on non grid meter device")
                event_data = {
                    "device_id": device.unique_id,
                    "device_name": device.name,
                }
                break
    @callback
    def on_connect_callback(self):
        """on gridEvent callback"""
        _LOGGER.info("On connect received")
        self._connection_atempt=0
    
    @callback
    def on_disconnect_callback(self):
        """on gridEvent callback"""
        _LOGGER.info("On disconnect received %s", self._connection_atempt)
        asyncio.run_coroutine_threadsafe(
            self._async_connect(self.socket, self.gateway_host, self.gateway_port, None), self._hass.loop
        )
        self._connection_atempt+=1




