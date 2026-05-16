from fastapi import FastAPI, WebSocket
import uvicorn
import json

app = FastAPI()

devices = {}

@app.websocket("/ws")
async def websocket(ws: WebSocket):

    await ws.accept()

    try:

        while True:

            data = await ws.receive_text()

            msg = json.loads(data)

            # DEVICE STATUS UPDATE
            if msg["type"] == "status":

                devices[msg["device_id"]] = msg

                print("STATUS:", msg["device_id"])

            # DASHBOARD REQUEST
            elif msg["type"] == "dashboard":

                device_id = msg["device_id"]

                if device_id in devices:

                    await ws.send_text(json.dumps({
                        "status":"connected",
                        "data":devices[device_id]
                    }))

                else:

                    await ws.send_text(json.dumps({
                        "status":"offline"
                    }))

    except Exception as e:

        print(e)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
