""" Sunology socket-io implementation """
import logging

import asyncio
from websockets.asyncio.client import connect
from websockets.exceptions import ConnectionClosed

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

    def on_productInfo(self, data):
        """ on_productInfo """
        _LOGGER.debug('ProductInfo received: %s', data)
        if self._on_productInfo_callback is not None:
            self._on_productInfo_callback(data)
    
    def on_solarEvent(self, data):
        """ on_solarEvente """
        _LOGGER.debug('SolarEvent received: %s', data)
        if self._on_solarEvent_callback is not None:
            self._on_solarEvent_callback(data)
    
    def on_batteryEvent(self, data):
        """ on_batteryEvent """
        _LOGGER.debug('Battery event received: %s', data)
        if self._on_batteryEvent_callback is not None:
            self._on_batteryEvent_callback(data)
    
    def on_gridEvent(self, data):
        """ on_gridEvent """
        _LOGGER.debug('Grid event received: %s', data)
        if self._on_gridEvent_callback is not None:
            self._on_gridEvent_callback(data)
    
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
        except Exception as err :
            _LOGGER.warning(f"Non json event received: {message}, {err=}, {type(err)=}")

    async def connect(self, lan_host_ip, lan_port, auth_token, basepath="ws"):
        """ connect to the sunology socket"""
        _LOGGER.debug('Socket connection call %s', lan_host_ip)
        if not self._connected:
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
        else:
            _LOGGER.warn('Socket already connected')

        #sio.wait()

        
    def disconnect(self):
        """disconnect from the sunology socket"""
        #sio.disconnect()
