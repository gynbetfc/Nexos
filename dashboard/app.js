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

            document.getElementById("status")
            .className = "status online"

            document.getElementById("status")
            .innerText = "ONLINE"

            document.getElementById("deviceInfo")
            .innerText = id

        }else{

            document.getElementById("status")
            .className = "status offline"

            document.getElementById("status")
            .innerText = "OFFLINE"
        }
    }
}
