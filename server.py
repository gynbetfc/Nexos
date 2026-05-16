from fastapi import FastAPI, WebSocket
import uvicorn
import json

app = FastAPI()

# Armazena os status mais recentes de cada dispositivo
devices = {}
# Armazena as conexões ativas dos dashboards para transmissão em tempo real
active_dashboards = {}

@app.websocket("/ws")
async def websocket(ws: WebSocket):
    await ws.accept()
    current_device_id = None
    connection_type = None

    try:
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)
            
            # 1. PROCESSA DADOS VINDOS DO AGENTE (CELULAR)
            if msg.get("type") == "status":
                device_id = msg.get("device_id")
                current_device_id = device_id
                connection_type = "device"
                
                # Salva no cache do servidor
                devices[device_id] = msg
                print(f"Status recebido do dispositivo: {device_id}")
                
                # Se houver um dashboard escutando esse dispositivo, envia os dados na hora
                if device_id in active_dashboards:
                    dash_ws = active_dashboards[device_id]
                    try:
                        await dash_ws.send_text(json.dumps({
                            "status": "connected",
                            "data": msg
                        }))
                    except Exception:
                        # Se o dashboard desconectou, remove da lista
                        active_dashboards.pop(device_id, None)

            # 2. PROCESSA REQUISIÇÃO VINDA DO DASHBOARD (WEB)
            elif msg.get("type") == "dashboard":
                device_id = msg.get("device_id")
                current_device_id = device_id
                connection_type = "dashboard"
                
                # Registra esse websocket como o painel ativo para este dispositivo
                active_dashboards[device_id] = ws
                print(f"Dashboard conectado para monitorar: {device_id}")

                # Se já tivermos dados desse aparelho salvos, envia imediatamente
                if device_id in devices:
                    await ws.send_text(json.dumps({
                        "status": "connected",
                        "data": devices[device_id]
                    }))
                else:
                    await ws.send_text(json.dumps({
                        "status": "offline"
                    }))

    except Exception as e:
        print(f"Conexão encerrada. Tipo: {connection_type} | ID: {current_device_id} | Erro: {e}")
    finally:
        # Limpeza básica se a conexão cair
        if connection_type == "dashboard" and current_device_id in active_dashboards:
            active_dashboards.pop(current_device_id, None)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)
