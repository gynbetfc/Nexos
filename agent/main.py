import asyncio
import websockets
import json
import uuid
import os
import subprocess

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

def get_system_info():
    """Coleta dados reais do Android usando o Termux API"""
    # Valores padrão caso falte alguma permissão no Termux
    battery = "N/A"
    android_version = "Android"
    storage_info = "N/A"
    uptime_info = "N/A"

    try:
        # Coleta bateria
        res = subprocess.run(["termux-battery-status"], capture_output=True, text=True, timeout=2)
        if res.returncode == 0:
            data = json.loads(res.stdout)
            battery = str(data.get("percentage", "N/A"))
    except Exception:
        pass

    try:
        # Coleta armazenamento interno disponível na Home do Termux
        res = subprocess.run(["df", "-h", "/data/data/com.termux/files/home"], capture_output=True, text=True, timeout=2)
        if res.returncode == 0:
            lines = res.stdout.split("\n")
            if len(lines) > 1:
                parts = [p for p in lines[1].split(" ") if p]
                if len(parts) >= 3:
                    storage_info = f"{parts[3]} livres" # Espaço disponível
    except Exception:
        pass

    try:
        # Coleta Uptime do sistema
        res = subprocess.run(["uptime"], capture_output=True, text=True, timeout=2)
        if res.returncode == 0:
            uptime_info = res.stdout.strip().split(",")[0].replace("up", "").strip()
    except Exception:
        pass

    return {
        "type": "status",
        "device_id": DEVICE_ID,
        "battery": battery,
        "android": android_version,
        "storage": storage_info,
        "uptime": uptime_info
    }

async def connect():
    while True:
        try:
            print(f"Tentando conectar ao servidor: {SERVER}")
            async with websockets.connect(SERVER) as ws:
                print("CONECTADO:", DEVICE_ID)
                
                while True:
                    # Coleta as informações atualizadas do dispositivo
                    payload = get_system_info()
                    
                    # Envia os dados estruturados como 'status' para o servidor salvar
                    await ws.send(json.dumps(payload))
                    
                    # Intervalo de atualização (ajuste para não sobrecarregar)
                    await asyncio.sleep(15)
                    
        except Exception as e:
            print("ERRO DE CONEXÃO:", e)
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(connect())
