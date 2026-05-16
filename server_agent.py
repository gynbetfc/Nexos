import asyncio
import json
import os
from aiohttp import web

PORT = 8080
ID_FILE = "/data/data/com.termux/files/home/.nexos/Nexos/device.id"

def get_device_id():
    if os.path.exists(ID_FILE):
        with open(ID_FILE) as f:
            return f.read().strip()
    return "NX-51830E60"

DEVICE_ID = get_device_id()

async def run_command(cmd, args, timeout=1.5):
    try:
        proc = await asyncio.create_subprocess_exec(
            cmd, *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        return stdout.decode().strip()
    except:
        return None

async def get_system_info():
    battery, storage_info, uptime_info = "N/A", "N/A", "N/A"
    lat, lon = None, None

    out_bat = await run_command("termux-battery-status", [])
    out_df = await run_command("df", ["-h", "/data/data/com.termux/files/home"])
    out_up = await run_command("uptime", [])
    out_loc = await run_command("termux-location", ["-p", "network", "-r", "once"])

    if out_bat:
        try: battery = str(json.loads(out_bat).get("percentage", "N/A"))
        except: pass
    if out_df:
        try:
            lines = out_df.split("\n")
            if len(lines) > 1:
                parts = [p for p in lines[1].split(" ") if p]
                if len(parts) >= 3: storage_info = f"{parts[3]} livres"
        except: pass
    if out_up:
        try: uptime_info = out_up.split(",")[0].replace("up", "").strip()
        except: pass
    if out_loc:
        try:
            loc_data = json.loads(out_loc)
            lat, lon = loc_data.get("latitude"), loc_data.get("longitude")
        except: pass

    return {
        "device_id": DEVICE_ID,
        "battery": battery,
        "android": "Android",
        "storage": storage_info,
        "uptime": uptime_info,
        "lat": lat,
        "lon": lon
    }

async def handle_index(request):
    url_id = request.match_info.get('id', '')
    if url_id != DEVICE_ID:
        return web.Response(text="Acesso Negado: ID Invalido.", status=403)
    
    html_content = f'''<!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <title>NEXOS DIRECT</title>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <style>
            * {{ box-sizing: border-box; margin: 0; padding: 0; }}
            body {{ background: #070f15; color: #e2e8f0; font-family: sans-serif; padding: 15px; }}
            .card {{ background: #0d1925; border: 1px solid #1e293b; border-radius: 12px; padding: 15px; margin-bottom: 12px; }}
            .card h2 {{ font-size: 13px; color: #38bdf8; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; border-bottom: 1px solid #1e293b; padding-bottom: 5px; }}
            .info-row {{ display: flex; justify-content: space-between; font-size: 14px; padding: 6px 0; border-bottom: 1px solid #0f172a; }}
            .info-row span {{ color: #64748b; }}
            .info-row strong {{ color: #f1f5f9; }}
            .map-container {{ width: 100%; height: 260px; border-radius: 8px; background: #040a0f; margin-top: 5px; }}
            #statusIndicator {{ font-size: 16px; font-weight: bold; color: #22c55e; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>System Status</h2>
            <div id="statusIndicator">● ONLINE (CONEXÃO DIRETA)</div>
        </div>
        <div class="card">
            <h2>Device Info</h2>
            <div class="info-row"><span>ID:</span><strong>{DEVICE_ID}</strong></div>
            <div class="info-row"><span>Bateria:</span><strong id="battery">---</strong></div>
            <div class="info-row"><span>Sistema:</span><strong>Android</strong></div>
            <div class="info-row"><span>Espaço:</span><strong id="storage">---</strong></div>
            <div class="info-row"><span>Uptime:</span><strong id="uptime">---</strong></div>
        </div>
        <div class="card">
            <h2>GPS Localization</h2>
            <div id="map" class="map-container"></div>
        </div>

        <script>
            let map = null; let marker = null;
            const wsProtocol = window.location.protocol === "https:" ? "wss://" : "ws://";
            const ws = new WebSocket(wsProtocol + window.location.host + "/ws");

            ws.onmessage = (e) => {{
                const d = JSON.parse(e.data);
                if(d.battery) document.getElementById("battery").innerText = d.battery + "%";
                if(d.storage) document.getElementById("storage").innerText = d.storage;
                if(d.uptime) document.getElementById("uptime").innerText = d.uptime;
                
                if (d.lat && d.lon) {{
                    const pos = [parseFloat(d.lat), parseFloat(d.lon)];
                    if (!map) {{
                        map = L.map('map', {{ zoomControl: false }}).setView(pos, 16);
                        L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png').addTo(map);
                        marker = L.marker(pos).addTo(map);
                    } else {{
                        marker.setLatLng(pos);
                        map.panTo(pos);
                    }}
                }}
            }};
            ws.onclose = () => {{ document.getElementById("statusIndicator").innerText = "● DESCONECTADO"; document.getElementById("statusIndicator").style.color = "#ef4444"; }};
        </script>
    </body>
    </html>
    '''
    return web.Response(text=html_content, content_type='text/html')

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    try:
        while True:
            payload = await get_system_info()
            await ws.send_str(json.dumps(payload))
            await asyncio.sleep(4)
    except: pass
    return ws

async def init_app():
    app = web.Application()
    app.router.add_get('/{id}', handle_index)
    app.router.add_get('/ws', websocket_handler)
    return app

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(init_app())
    print(f"🚀 Servidor Nexos ativo na porta {{PORT}}")
    web.run_app(app, port=PORT)
