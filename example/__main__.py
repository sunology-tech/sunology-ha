from .socket import SunologySocket
import asyncio
import threading
import logging

_LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
socket = None
def on_productInfo_callback(product_data):
    """on device callback"""
    print('device callback')



def on_solarEvent_callback(data):
    """on solarEvent callback"""
    print('solarEvent callback')

def on_batteryEvent_callback(data):
    """on batteryEvent callback"""
    print('batteryEvent callback')


def on_gridEvent_callback(data):
    """on gridEvent callback"""
    print('gridEvent callback')


async def main():
    _LOGGER.info("Hello")
    socket = SunologySocket()
    socket.subscribe_on_productInfo(on_productInfo_callback)
    socket.subscribe_on_solarEvent(on_solarEvent_callback)
    socket.subscribe_on_batteryEvent(on_batteryEvent_callback)
    socket.subscribe_on_gridEvent(on_gridEvent_callback)

    x = threading.Thread(target=asyncio.run, args=(socket.mock_messages_forever(),))
    x.start()
    await socket.connect(f"ws://Sun-48CA434B646C.local:20199/ws", None)
    ##x.join()

asyncio.run(main())
