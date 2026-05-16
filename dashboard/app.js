const SERVER = "wss://nexos-t0to.onrender.com/ws";
let ws = null;
let map = null;
let marker = null;

window.onload = () => {
    const savedId = localStorage.getItem("nexos_device_id");
    if (savedId) {
        document.getElementById("deviceId").value = savedId;
        connectDevice();
    }
};

function connectDevice() {
    const id = document.getElementById("deviceId").value.trim();
    if (!id) {
        alert("Por favor, insira um DEVICE ID válido.");
        return;
    }

    if (ws) ws.close();
    ws = new WebSocket(SERVER);

    ws.onopen = () => {
        localStorage.setItem("nexos_device_id", id);
        ws.send(JSON.stringify({ type: "dashboard", device_id: id }));
    };

    ws.onmessage = (e) => {
        const msg = jsonInterpret(e.data);

        if (msg && msg.status === "connected") {
            const d = msg.data;

            const statusBtn = document.getElementById("status");
            statusBtn.className = "status online";
            statusBtn.innerText = "DISCONNECT";
            statusBtn.setAttribute("onclick", "disconnectDevice()");

            document.getElementById("statusIndicatorCard").innerText = "● ONLINE";
            document.getElementById("statusIndicatorCard").style.color = "#00ff88";

            document.getElementById("battery").innerText = d.battery ? d.battery + "%" : "---";
            document.getElementById("android").innerText = d.android || "---";
            document.getElementById("storage").innerText = d.storage || "---";
            document.getElementById("uptime").innerText = d.uptime || "---";
            document.getElementById("deviceInfo").innerText = d.device_id || "---";

            if (d.lat && d.lon) {
                const position = [d.lat, d.lon];

                if (!map) {
                    map = L.map('map').setView(position, 16);
                    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
                        attribution: '© OpenStreetMap'
                    }).addTo(map);
                    
                    marker = L.marker(position).addTo(map);
                } else {
                    marker.setLatLng(position);
                    map.panTo(position);
                }

                const mapsBtn = document.getElementById("googleMapsBtn");
                mapsBtn.href = `https://www.google.com/maps?q=${d.lat},${d.lon}`;
                mapsBtn.style.display = "block";
            }

        } else {
            setUiOffline();
        }
    };

    ws.onerror = () => setUiOffline();
}

function disconnectDevice() {
    localStorage.removeItem("nexos_device_id");
    if (ws) ws.close();
    setUiOffline();
    document.getElementById("deviceId").value = "";
    
    if (map) {
        map.remove();
        map = null;
        marker = null;
    }
}

function setUiOffline() {
    const statusBtn = document.getElementById("status");
    statusBtn.className = "status offline";
    statusBtn.innerText = "OFFLINE";
    statusBtn.setAttribute("onclick", "connectDevice()");

    document.getElementById("statusIndicatorCard").innerText = "● AGUARDANDO CONEXÃO";
    document.getElementById("statusIndicatorCard").style.color = "#4ade80";

    document.getElementById("battery").innerText = "---";
    document.getElementById("android").innerText = "---";
    document.getElementById("storage").innerText = "---";
    document.getElementById("uptime").innerText = "---";
    document.getElementById("deviceInfo").innerText = "---";
    document.getElementById("googleMapsBtn").style.display = "none";
}

function jsonInterpret(data) {
    try { return JSON.parse(data); } catch (e) { return null; }
}
