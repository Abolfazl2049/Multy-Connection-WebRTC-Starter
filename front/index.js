

const servers = { iceServers: [{ urls: 'stun:stun.l.google.com:19302' }] };
const peerConnections = {};
let localStream;

const localVideo = document.getElementById('localVideo');
const remoteVideos = document.getElementById('remoteVideos');

function setLocalStream(){
    navigator.mediaDevices.getUserMedia({ video: true, audio: true }).then(stream => {
        localVideo.srcObject = stream;
        localStream = stream;
    });
}

function getRandomInt(min, max) {
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min) + min);
}

function join(){

    input = document.getElementById("roomInput").value
    random_number = getRandomInt(10,99)
    document.getElementById("user_id").innerText = random_number
    var ws = new WebSocket(`ws://localhost:8000/ws/${input}/${random_number}`);
    setLocalStream()

    ws.onopen = function(event){
        ws.send(JSON.stringify({"type":"join","data":{}}))
    }
    ws.onmessage = function(event) {
        data = JSON.parse(event.data)
        switch(data["type"]){
            case "join":
                // Let's send offer
                console.log("New user join")
            case "offer":
                // Let's answer
                console.log("New user join")
        }
        
    };

}