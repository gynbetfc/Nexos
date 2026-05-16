from fastapi import FastAPI, WebSocket
import uvicorn
import json

app = FastAPI()

devices = {}

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):

    await ws.accept()

    try:

        while True:

            data = await ws.receive_text()
            msg = json.loads(data)

            if msg["type"] == "device":

                devices[msg["device_id"]] = ws

                print("[DEVICE ONLINE]", msg["device_id"])

            elif msg["type"] == "dashboard":

                if msg["device_id"] in devices:

                    await ws.send_text(json.dumps({
                        "status":"connected"
                    }))

                else:

                    await ws.send_text(json.dumps({
                        "status":"offline"
                    }))

    except:
        pass

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
