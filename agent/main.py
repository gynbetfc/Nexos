import asyncio
import websockets
import json
import os
import subprocess

SERVER = "wss://nexos-t0to.onrender.com/ws"
ID_FILE = "/data/data/com.termux/files/home/.nexos/Nexos/agent/device.id"

def get_device_id():
    if os.path.exists(ID_FILE):
        with open(ID_FILE) as f:
            return f.read().strip()
    return "NX-51830E60"

DEVICE_ID = get_device_id()

def get_system_info():
    battery, storage_info, uptime_info = "N/A", "N/A", "N/A"
    lat, lon = None, None

    try:
        res = subprocess.run(["termux-battery-status"], capture_output=True, text=True, timeout=2)
        if res.returncode == 0:
            battery = str(json.loads(res.stdout).get("percentage", "N/A"))
    except: pass

    try:
        res = subprocess.run(["df", "-h", "/data/data/com.termux/files/home"], capture_output=True, text=True, timeout=2)
        if res.returncode == 0:
            lines = res.stdout.split("\n")
            if len(lines) > 1:
                parts = [p for p in lines[1].split(" ") if p]
                if len(parts) >= 3: storage_info = f"{parts[3]} livres"
    except: pass

    try:
        res = subprocess.run(["uptime"], capture_output=True, text=True, timeout=2)
        if res.returncode == 0:
            uptime_info = res.stdout.strip().split(",")[0].replace("up", "").strip()
    except: pass

    try:
        res = subprocess.run(["termux-location", "-p", "network", "-r", "once"], capture_output=True, text=True, timeout=2)
        if res.returncode == 0:
            loc_data = json.loads(res.stdout)
            lat, lon = loc_data.get("latitude"), loc_data.get("longitude")
    except: pass

    return {"type": "status", "device_id": DEVICE_ID, "battery": battery, "android": "Android", "storage": storage_info, "uptime": uptime_info, "lat": lat, "lon": lon}

async def connect():
    while True:
        try:
            # ping_interval=5 força o servidor a manter a conexão real e fechar se houver F5
            async with websockets.connect(SERVER, ping_interval=5, ping_timeout=5) as ws:
                while True:
                    payload = get_system_info()
                    await ws.send(json.dumps(payload))
                    await asyncio.sleep(4) # Envia dados mais rápido (a cada 4s) para preencher a tela pós-F5
        except:
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(connect())
