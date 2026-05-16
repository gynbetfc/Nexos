const SERVER = "wss://nexos-t0to.onrender.com/ws";
let ws = null; // Guardará a conexão WebSocket globalmente

// Executa automaticamente assim que a página carrega
window.onload = () => {
    const savedId = localStorage.getItem("nexos_device_id");
    if (savedId) {
        document.getElementById("deviceId").value = savedId;
        connectDevice(); // Reconecta automaticamente se já existia um ID salvo
    }
};

function connectDevice() {
    const id = document.getElementById("deviceId").value.trim();
    
    if (!id) {
        alert("Por favor, insira um DEVICE ID válido.");
        return;
    }

    // Se já houver uma conexão ativa, fecha antes de abrir uma nova
    if (ws) {
        ws.close();
    }

    ws = new WebSocket(SERVER);

    ws.onopen = () => {
        // Salva o ID no navegador para não perder ao atualizar a página (F5)
        localStorage.setItem("nexos_device_id", id);

        ws.send(JSON.stringify({
            type: "dashboard",
            device_id: id
        }));
    };

    ws.onmessage = (e) => {
        const msg = jsonInterpret(e.data);

        if (msg && msg.status === "connected") {
            const d = msg.data;

            // 1. Atualiza a barra superior de conexão
            const statusBtn = document.getElementById("status");
            statusBtn.className = "status online";
            statusBtn.innerText = "DISCONNECT"; // Muda o texto para virar um botão de desconectar
            statusBtn.setAttribute("onclick", "disconnectDevice()"); // Atribui a função de desconexão

            // 2. Atualiza o card de status principal
            document.getElementById("statusIndicator").innerText = "● ONLINE";
            document.getElementById("statusIndicator").style.color = "#00ff88";

            // 3. Injeta os dados do Termux nos campos do Device Info
            document.getElementById("battery").innerText = d.battery ? d.battery + "%" : "---";
            document.getElementById("android").innerText = d.android || "---";
            document.getElementById("storage").innerText = d.storage || "---";
            document.getElementById("uptime").innerText = d.uptime || "---";
            document.getElementById("deviceInfo").innerText = d.device_id || "---";

        } else {
            setUiOffline();
        }
    };

    ws.onerror = (err) => {
        console.error("Erro no WebSocket:", err);
        setUiOffline();
    };

    ws.onclose = () => {
        console.log("Conexão WebSocket encerrada.");
    };
}

// Função para desconectar manualmente (só limpa se o usuário comandar)
function disconnectDevice() {
    // Remove o ID do armazenamento local para não reconectar no F5
    localStorage.removeItem("nexos_device_id");
    
    if (ws) {
        ws.close();
    }
    
    setUiOffline();
    document.getElementById("deviceId").value = ""; // Limpa o input
}

// Reseta a interface do painel para o estado Offline
function setUiOffline() {
    const statusBtn = document.getElementById("status");
    statusBtn.className = "status offline";
    statusBtn.innerText = "OFFLINE";
    statusBtn.setAttribute("onclick", "connectDevice()"); // Destina de volta para conectar

    document.getElementById("statusIndicator").innerText = "● AGUARDANDO CONEXÃO";
    document.getElementById("statusIndicator").style.color = "#4ade80";

    document.getElementById("battery").innerText = "---";
    document.getElementById("android").innerText = "---";
    document.getElementById("storage").innerText = "---";
    document.getElementById("uptime").innerText = "---";
    document.getElementById("deviceInfo").innerText = "---";
}

// Auxiliar seguro para parsear JSON sem estourar erro no console
function jsonInterpret(data) {
    try {
        return JSON.parse(data);
    } catch (e) {
        return null;
    }
}
