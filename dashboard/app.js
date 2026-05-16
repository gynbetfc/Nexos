const SERVER = "wss://YOUR-RENDER.onrender.com/ws"

function connectDevice(){

    const id = document.getElementById("deviceId").value

    const ws = new WebSocket(SERVER)

    ws.onopen = () => {

        ws.send(JSON.stringify({
            type:"dashboard",
            device_id:id
        }))
    }

    ws.onmessage = (e) => {

        const msg = JSON.parse(e.data)

        if(msg.status === "connected"){

            alert("DEVICE ONLINE")

        }else{

            alert("DEVICE OFFLINE")
        }
    }
}
