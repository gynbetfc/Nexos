import asyncio
import websockets
import json
import uuid
import os
import subprocess

SERVER = "wss://nexos-t0to.onrender.com/ws"
# Definindo o caminho absoluto para nunca mais perder o arquivo de ID
ID_FILE = "/data/data/com.termux/files/home/.nexos/Nexos/agent/device.id"

def get_device_id():
    if os.path.exists(ID_FILE):
        with open(ID_FILE) as f:
            return f.read().strip()
    
    # Se não existir, garante que a pasta existe e cria o ID padrão estável
    os.makedirs(os.path.dirname(ID_FILE), exist_ok=True)
    device_id = "NX-51830E60"
    with open(ID_FILE, "w") as f:
        f.write(device_id)
    return device_id

DEVICE_ID = get_device_id()

def get_system_info():
    battery = "N/A"
    android_version = "Android"
    storage_info = "N/A"
    uptime_info = "N/A"
    lat = None
    lon = None

    try:
        res = subprocess.run(["termux-battery-status"], capture_output=True, text=True, timeout=2)
        if res.returncode == 0:
            data = json.loads(res.stdout)
            battery = str(data.get("percentage", "N/A"))
    except Exception:
        pass

    try:
        res = subprocess.run(["df", "-h", "/data/data/com.termux/files/home"], capture_output=True, text=True, timeout=2)
        if res.returncode == 0:
            lines = res.stdout.split("\n")
            if len(lines) > 1:
                parts = [p for p in lines[1].split(" ") if p]
                if len(parts) >= 3:
                    storage_info = f"{parts[3]} livres"
    except Exception:
        pass

    try:
        res = subprocess.run(["uptime"], capture_output=True, text=True, timeout=2)
        if res.returncode == 0:
            uptime_info = res.stdout.strip().split(",")[0].replace("up", "").strip()
    except Exception:
        pass

    try:
        res = subprocess.run(["termux-location", "-p", "network"], capture_output=True, text=True, timeout=3)
        if res.returncode == 0:
            loc_data = json.loads(res.stdout)
            lat = loc_data.get("latitude")
            lon = loc_data.get("longitude")
    except Exception:
        pass

    return {
        "type": "status",
        "device_id": DEVICE_ID,
        "battery": battery,
        "android": android_version,
        "storage": storage_info,
        "uptime": uptime_info,
        "lat": lat,
        "lon": lon
    }

async def connect():
    while True:
        try:
            async with websockets.connect(SERVER) as ws:
                print("CONECTADO:", DEVICE_ID)
                while True:
                    payload = get_system_info()
                    await ws.send(json.dumps(payload))
                    await asyncio.sleep(15)
        except Exception as e:
            print("ERRO DE CONEXÃO RECONECTANDO EM 5S:", e)
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(connect())
