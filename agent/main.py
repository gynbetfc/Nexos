import asyncio
import websockets
import json
import uuid
import os

SERVER = "wss://nexos-t0to.onrender.com/ws"

ID_FILE = "device.id"

def get_device_id():

    if os.path.exists(ID_FILE):

        with open(ID_FILE) as f:
            return f.read().strip()

    device_id = "NX-" + str(uuid.uuid4())[:8].upper()

    with open(ID_FILE, "w") as f:
        f.write(device_id)

    return device_id

DEVICE_ID = get_device_id()

async def connect():

    while True:

        try:

            async with websockets.connect(SERVER) as ws:

                await ws.send(json.dumps({
                    "type":"device",
                    "device_id":DEVICE_ID
                }))

                print("CONNECTED:", DEVICE_ID)

                while True:

                    await asyncio.sleep(15)

                    await ws.send(json.dumps({
                        "type":"heartbeat"
                    }))

        except Exception as e:

            print("ERROR:", e)

            await asyncio.sleep(5)

asyncio.run(connect())
