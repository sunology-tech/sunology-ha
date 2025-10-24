""" sunology custom conpennt """
from collections import defaultdict

import asyncio
import logging
from typing import Any, Mapping
from datetime import timedelta
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
from homeassistant.exceptions import HomeAssistantError
from homeassistant.setup import async_when_setup
from homeassistant.const import Platform
from homeassistant.components import zeroconf
from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

import threading
type SunologyConfigEntry = ConfigEntry[SunologyContext]

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

PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass, entry: SunologyConfigEntry):
    """Set up Sunology entry."""
    gateway_host = entry.data[CONF_GATEWAY_HOST] if CONF_GATEWAY_HOST in entry.data.keys() else None
    gateway_port = entry.data[CONF_GATEWAY_PORT] if CONF_GATEWAY_PORT in entry.data.keys() else None
    context = SunologyContext(
        hass,
        entry,
        gateway_host,
        gateway_port
    )

    _LOGGER.info("Context-setup and start the thread")
    _LOGGER.info("Thread started")
    entry.runtime_data = context

    # We add device to the context
    await context.init_context(hass)

    await hass.config_entries.async_forward_entry_setups(entry,PLATFORMS)
    return True


async def async_unload_entry(hass, entry: SunologyConfigEntry):
    """Unload an Sunology config entry."""
    unload_ok = True
    # unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    context =  entry.runtime_data
    await context.socket.disconnect() # Disconnect only if all devices is disabled
    context.unload()
    return unload_ok


async def async_remove_config_entry_device(hass, config_entry: SunologyConfigEntry, device_entry) -> bool:
    """Remove a config entry from a device."""
    return not any(
        identifier
        for identifier in device_entry.identifiers
        if identifier[0] == DOMAIN
        and identifier[1] in [sunology_device.device_id for sunology_device in config_entry.runtime.sunology_devices]
    )



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
        self._coroutines_future = []

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
    
    def unload(self):
        """ hass """
        for future in self._coroutines_future:
            future.cancel()
        self._coroutines_future = []


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

        self._coroutines_future.append(asyncio.run_coroutine_threadsafe(
            self._async_connect(socket, self.gateway_host, self.gateway_port, None), self._hass.loop
        ))

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
        _LOGGER.debug("Device added to coordinator %s, %s", device.model_name, device.device_id)
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
            self._coroutines_future.append(asyncio.run_coroutine_threadsafe(
                self._async_connect(self.socket, self.gateway_host, self.gateway_port, None), self._hass.loop
            ))
            self._connection_atempt+=1

        if epoch_min != self._previous_refresh:
            self._previous_refresh =  epoch_min
            for device_coordoned in self._sunology_devices_coordoned:
                if device_coordoned['device'].device_entry_id is None:
                    device_entry = await device_coordoned['device'].register(self.hass, self._entry) # Look to be the source of my issue
                    device_coordoned['device'].device_entry_id =  device_entry.id
    
    async def _register_new_devices(self, new_devices):
        """ reload platforms """
        for device_coordoned in self._sunology_devices_coordoned:
            for device in new_devices:
                if device['device'].unique_id == device_coordoned['device'].unique_id:
                    if device_coordoned['device'].device_entry_id is None:
                        device_entry = await device_coordoned['device'].register(self.hass, self._entry) # Look to be the source of my issue
                        device_coordoned['device'].device_entry_id = device_entry.id
        await self._reload_platforms()
    
    async def _reload_platforms(self, epoch_min = math.floor(time.time()/60)):
        self._previous_refresh =  epoch_min
        if self._entry.state == ConfigEntryState.LOADED:
            await self.hass.config_entries.async_unload_platforms(self._entry, PLATFORMS)
            await self.hass.config_entries.async_forward_entry_setups(self._entry, PLATFORMS)
        # else:
        #     await self.hass.config_entries.async_forward_entry_setups(self._entry, PLATFORMS)

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


    def process_new_device(self, product_data, sub_loop=False):
        new_devices = []
        found = False
        for coordoned_device in self._sunology_devices_coordoned:
            if 'device' not in coordoned_device.keys():
                device = coordoned_device['device']
                if device.device_id == product_data['id']:
                    device.update_product(product_data)
                    found = True
                    if product_data['productName'] == "STREAM_CONNECT" and "devices" in product_data.keys():
                        for sub_device in product_data['devices']:
                            new_devices.extend(self.process_new_device(sub_device, True))
                    elif product_data['productName'] == "STOREY":
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
                        self.add_devices_to_coordinator(new_packs)
                    break
        if not found:
            match product_data['productName']:
                case "PLAY_MAX":
                    new_devices.append(PLAYMax(product_data))
                case "PLAY":
                    new_devices.append(PLAY(product_data))
                case "STREAM_CONNECT":
                    new_devices.append(Gateway(product_data))
                    if "devices" in product_data.keys():
                        for hub_device in product_data['devices']:
                            new_devices.extend(self.process_new_device(hub_device, True))
                case "STOREY":
                    master = StoreyMaster(product_data)
                    products_valid=True
                    if 'battery' not in product_data.keys():
                        _LOGGER.warning("No battery data found for Storey %s", product_data['id'])
                        #raise HomeAssistantError(f"No battery data found for Storey {product_data['id']}")
                        products_valid=False
                    else:
                        master.capacity = product_data['battery']['capacity']
                        master.maxInput = product_data['battery']['maxCons']
                        master.maxOutput = product_data['battery']['maxProd']
                    if 'packs' not in product_data.keys():
                        _LOGGER.warning("No packs data found for Storey %s", product_data['id'])
                        products_valid=False
                        #raise HomeAssistantError(f"No packs data found for Storey {product_data['id']}")
                    else:
                        for pack in product_data['packs']:
                            st_pack = StoreyPack(product_data, pack['packIndex'])
                            st_pack.capacity = pack['capacity']
                            st_pack.maxInput = pack['maxCons']
                            st_pack.maxOutput = pack['maxProd']
                            new_devices.append(st_pack)
                    if products_valid:
                        new_devices.append(master)
                case "STREAM_METER":
                    new_devices.append(SmartMeter_3P(product_data))
                case "ERL_GEN2":
                    new_devices.append(LinkyTransmitter(product_data))
                case _:
                    _LOGGER.warning("Unmanaged device receive on device_event")
                    new_devices.append(SunologyAbstractDevice(product_data))
        return new_devices
    
    @callback
    def on_productInfo_callback(self, product_data):
        """on device callback"""
        _LOGGER.info("On device received '%s'", product_data['productName'])
        new_devices = self.process_new_device(product_data)
        for device in new_devices:
            _LOGGER.info("New devices found %s", device)
            self._sunology_devices.append(device)
            self.add_device_to_coordinator(device)
        if len(new_devices) > 0:
            asyncio.run_coroutine_threadsafe(
                self._register_new_devices(new_devices), self._hass.loop
            )


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
                    if 'device_entities' in coordoned_device.keys():
                        for entity in coordoned_device['device_entities']:
                            _LOGGER.debug('Update entity %s', entity.entity_id)
                            entity.schedule_update_ha_state(force_refresh=False)

                    for pack in data['packs']:
                            for sub_coordoned_device in self._sunology_devices_coordoned:
                                sub_device = sub_coordoned_device['device']
                                if sub_device.device_id == f"{data['id']}#{pack['packIndex'] }":
                                    sub_device.battery_event_update(pack)
                                    if 'device_entities' in sub_coordoned_device.keys():

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
                    if 'device_entities' in coordoned_device.keys():
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
        self._coroutines_future.append(asyncio.run_coroutine_threadsafe(
            self._async_connect(self.socket, self.gateway_host, self.gateway_port, None), self._hass.loop
        ))
        self._connection_atempt+=1




