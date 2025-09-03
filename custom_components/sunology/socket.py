""" Sunology socket-io implementation """
import logging

import asyncio
from websockets.asyncio.client import connect
from websockets.exceptions import ConnectionClosed
from homeassistant.exceptions import HomeAssistantError

import time
import random
import json
from .const import PACKAGE_NAME


_LOGGER = logging.getLogger(PACKAGE_NAME)
class SunologySocket():
    """docstring for SunologySocket"""
    def __init__(self):
        self._on_productInfo_callback = None
        self._on_solarEvent_callback = None
        self._on_batteryEvent_callback = None
        self._on_gridEvent_callback = None
        self._on_connect_callback = None
        self._on_disconnect_callback = None

        self._initialised = False
        self._socket = None
        self._connected = False


    def subscribe_on_productInfo(self, callback_function):
        """event: tells you authentication informations."""
        self._on_productInfo_callback = callback_function

    def subscribe_on_solarEvent(self, callback_function):
        """event: tells you authentication informations."""
        self._on_solarEvent_callback = callback_function

    def subscribe_on_batteryEvent(self, callback_function):
        """event: tells you when a device is added to the gateway."""
        self._on_batteryEvent_callback = callback_function

    def subscribe_on_gridEvent(self, callback_function):
        """event: tells you when a device trigger an alarm."""
        self._on_gridEvent_callback = callback_function
    
    def subscribe_on_connect(self, callback_function):
        """event: tells you when you are connected to the socket."""
        self._on_connect_callback = callback_function
    
    def subscribe_on_diconnect(self, callback_function):
        """event: tells you when you are have lost connection of the socket."""
        self._on_disconnect_callback = callback_function

    def _execute_callback_function_safe(self, function_name, function, data):
        """ execute_function """
        if function is not None:
            _LOGGER.debug('Execute function %s with data %s', function_name, json.dumps(data))
            try:
                function(data)
            except HomeAssistantError:
                pass
            except Exception as e:
                _LOGGER.exception('Error while executing function %s:', function_name)
        else:
            _LOGGER.debug('No function to execute for %s', function_name)

    def on_productInfo(self, data):
        """ on_productInfo """
        _LOGGER.debug('ProductInfo received: %s', data)
        self._execute_callback_function_safe('on_productInfo', self._on_productInfo_callback, data)
    
    def on_solarEvent(self, data):
        """ on_solarEvente """
        _LOGGER.debug('SolarEvent received: %s', data)
        self._execute_callback_function_safe('on_solarEvent', self._on_solarEvent_callback, data)
    
    def on_batteryEvent(self, data):
        """ on_batteryEvent """
        _LOGGER.debug('Battery event received: %s', data)
        self._execute_callback_function_safe('on_batteryEvent', self._on_batteryEvent_callback, data)
    
    def on_gridEvent(self, data):
        """ on_gridEvent """
        _LOGGER.debug('Grid event received: %s', data)
        self._execute_callback_function_safe('on_gridEvent', self._on_gridEvent_callback, data)
    
    def on_connect(self):
        """ event: connected """
        _LOGGER.debug('Sunology socket connected')
        if self._on_connect_callback is not None:
            self._on_connect_callback()

    @property
    def is_connected(self):
        return self._connected

    def on_disconnect(self):
        """ event: disconnected """
        _LOGGER.debug('Sunology socket disconnected')
        if self._on_disconnect_callback is not None:
            self._on_disconnect_callback()

    def process(self, raw_message):
        """ process the received messages """
        try:
            message = json.loads(raw_message)
            if 'event' in message:
                match message['event']:
                    case "productInfo":
                        self.on_productInfo(message['data'])
                    case "solarEvent":
                        self.on_solarEvent(message['data'])
                    case "batteryEvent":
                        self.on_batteryEvent(message['data'])
                    case "gridEvent":
                        self.on_gridEvent(message['data'])
                    case _:
                        _LOGGER.warning('Unmanaged event received: %s', message['event'])
            else:
                _LOGGER.warning('Invalid event received: %s', message)
        except json.JSONDecodeError as err :
            _LOGGER.warning(f"Non json event received: {message}, {err=}, {type(err)=}")
        except UnicodeDecodeError as err :
            _LOGGER.warning(f"Non json event received: {message}, {err=}, {type(err)=}")

    async def connect(self, lan_host_ip, lan_port, auth_token, basepath="ws"):
        """ connect to the sunology socket"""
        _LOGGER.debug('Socket connection call %s', lan_host_ip)
        if self._connected:
            _LOGGER.warn('Socket already connected')
        else:
            _LOGGER.debug('Socket not connected')
            if auth_token is not None:
                _LOGGER.debug('Auth connection')
                async with connect(f"ws://{lan_host_ip}:{lan_port}/{basepath}", additional_headers={'token': auth_token}) as websocket:
                    try:
                        self._socket = websocket
                        self._connected = True
                        self.on_connect()
                        async for message in self._socket:
                            self.process(message)
                    except ConnectionClosed:
                        self._connected = False
                        self.on_disconnect()
                        
            else:
                _LOGGER.debug('Unauth connection')
                async with connect(f"ws://{lan_host_ip}:{lan_port}/{basepath}") as websocket :
                    try:
                        self._socket = websocket
                        self._connected = True
                        self.on_connect()
                        async for message in self._socket:
                            self.process(message)
                    except ConnectionClosed:
                        self._connected = False
                        self.on_disconnect()

        
    async def disconnect(self):
        """disconnect from the sunology socket"""
        if self._socket is not None:
            await self._socket.close()
        self._connected = False
        self.on_disconnect()
