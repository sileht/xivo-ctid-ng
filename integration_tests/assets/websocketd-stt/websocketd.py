import asyncio
import logging
import websockets

LOG = logging.getLogger(__name__)

async def echo(websocket, path):
    LOG.info("echo %s", path)
    if path == "/stream":
        try:
            # async for message in websocket:
            #    LOG.info("echo %s", path)
            with open("record.wav", "rb") as r:
                await websocket.send(r.read())
        except websockets.exceptions.ConnectionClosed:
            pass


asyncio.get_event_loop().run_until_complete(
    websockets.serve(echo, '0.0.0.0', 8765))
asyncio.get_event_loop().run_forever()
