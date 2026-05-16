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
    if (!id) return;

    if (ws) ws.close();
    ws = new WebSocket(SERVER);

    ws.onopen = () => {
        localStorage.setItem("nexos_device_id", id);
        ws.send(JSON.stringify({ type: "dashboard", device_id: id }));
    };

    ws.onmessage = (e) => {
        try {
            const msg = JSON.parse(e.data);
            if (msg && msg.status === "connected") {
                const d = msg.data;

                const btn = document.getElementById("status");
                btn.innerText = "DISCONNECT";
                btn.style.background = "#ef4444";
                btn.style.color = "#fff";
                btn.setAttribute("onclick", "disconnectDevice()");

                document.getElementById("statusIndicatorCard").innerText = "● ONLINE";
                document.getElementById("statusIndicatorCard").style.color = "#22c55e";

                document.getElementById("deviceInfo").innerText = d.device_id || "---";
                document.getElementById("battery").innerText = d.battery ? d.battery + "%" : "---";
                document.getElementById("android").innerText = d.android || "---";
                document.getElementById("storage").innerText = d.storage || "---";
                document.getElementById("uptime").innerText = d.uptime || "---";

                if (d.lat && d.lon) {
                    const position = [d.lat, d.lon];
                    if (!map) {
                        map = L.map('map', { zoomControl: false }).setView(position, 15);
                        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png').addTo(map);
                        marker = L.marker(position).addTo(map);
                    } else {
                        marker.setLatLng(position);
                        map.panTo(position);
                    }
                    const mapsBtn = document.getElementById("googleMapsBtn");
                    mapsBtn.href = `https://www.google.com/maps/search/?api=1&query=${d.lat},${d.lon}`;
                    mapsBtn.style.display = "block";
                }
            }
        } catch(err) {
            console.log(err);
        }
    };
    ws.onerror = () => setUiOffline();
    ws.onclose = () => setUiOffline();
}

function disconnectDevice() {
    if (ws) ws.close();
    setUiOffline();
}

function setUiOffline() {
    const btn = document.getElementById("status");
    btn.innerText = "CONNECT";
    btn.style.background = "#22c55e";
    btn.style.color = "#022c22";
    btn.setAttribute("onclick", "connectDevice()");
    document.getElementById("statusIndicatorCard").innerText = "● DESCONECTADO";
    document.getElementById("statusIndicatorCard").style.color = "#ef4444";
    document.getElementById("googleMapsBtn").style.display = "none";
}
