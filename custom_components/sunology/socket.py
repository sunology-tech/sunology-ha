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



def on_connect():
    """ event: connected """
    _LOGGER.debug('Sunology socket connected')
def on_disconnect():
    """ event: disconnected """
    _LOGGER.debug('Sunology socket disconnected')


class SunologySocket():
    """docstring for SunologySocket"""
    def __init__(self):
        self._on_productInfo_callback = None
        self._on_solarEvent_callback = None
        self._on_batteryEvent_callback = None
        self._on_gridEvent_callback = None
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

    async def connect(self, lan_host, auth_token):
        """ connect to the sunology socket"""
        _LOGGER.debug('Socket connection call %s', lan_host)
        if auth_token is not None:
            _LOGGER.debug('Auth connection')
            async for self._socket in connect(lan_host, additional_headers={'token': auth_token}):
                try:
                    on_connect()
                    self._connected = True
                    async for message in self._socket:
                        self.process(message)
                except ConnectionClosed:
                    self._connected = False
                    on_disconnect()
                    
        else:
            _LOGGER.debug('Unauth connection')
            async for self._socket in connect(lan_host):
                try:
                    on_connect()
                    self._connected = True
                    async for message in self._socket:
                        self.process(message)
                except ConnectionClosed:
                    self._connected = False
                    on_disconnect()

        #sio.wait()
    
    #TODO: DELETE-ME Mock
    async def mock_messages_forever(self):
        while not self._connected:
            #time.sleep(1)
            await asyncio.sleep(1)
        with open('custom_components/sunology/mock_messages.json') as mock_messages_f:
            mock_messages = json.load(mock_messages_f)
            while self._connected:
                msg_idx = random.randrange(0, len(mock_messages), 1)
                message_to_send = mock_messages[msg_idx]
                await self._socket.send(json.dumps(message_to_send))
                # time.sleep(1)
                await asyncio.sleep(1)

    #TODO: DELETE-ME Mock
    async def mock_messages_one_shot(self):
        _LOGGER.info('Mock one shot')
        while not self._connected:
            #time.sleep(1)
            _LOGGER.debug('Socket not opened')
            await asyncio.sleep(1)
        with open('/config/custom_components/sunology/mock_messages.json') as mock_messages_f:
            _LOGGER.debug('File opened')
            mock_messages = json.load(mock_messages_f)
            msg_idx = random.randrange(0, len(mock_messages), 1)
            message_to_send = mock_messages[msg_idx]
            await self._socket.send(json.dumps(message_to_send))

        
    def disconnect(self):
        """disconnect from the sunology socket"""
        #sio.disconnect()
