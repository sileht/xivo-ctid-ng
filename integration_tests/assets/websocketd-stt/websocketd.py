import asyncio
import websockets


async def echo(websocket, path):
    if path == "/stream":
        try:
            async for message in websocket:
                with open("record.wav", "rb") as r:
                    await websocket.send(r.read())
        except websockets.exceptions.ConnectionClosed:
            pass


asyncio.get_event_loop().run_until_complete(
    websockets.serve(echo, '0.0.0.0', 8765))
asyncio.get_event_loop().run_forever()
