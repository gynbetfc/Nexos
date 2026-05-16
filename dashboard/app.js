const SERVER = "wss://nexos-t0to.onrender.com/ws"

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

            const d = msg.data

            document.getElementById("status")
            .className = "status online"

            document.getElementById("status")
            .innerText = "ONLINE"

            document.getElementById("battery")
            .innerText = d.battery + "%"

            document.getElementById("android")
            .innerText = d.android

            document.getElementById("storage")
            .innerText = d.storage

            document.getElementById("uptime")
            .innerText = d.uptime

            document.getElementById("deviceInfo")
            .innerText = d.device_id

        }else{

            document.getElementById("status")
            .innerText = "OFFLINE"
        }
    }
}
