

const servers = { iceServers: [{ urls: 'stun:stun.l.google.com:19302' }] };
const peerConnections = {};
let localStream;
let ws; 
let room_id;

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

function sendAnswer(user_id,data){
    console.log(`Sending answer to ${user_id}`)
    offer = data["offer"]
    pc.setRemoteDescription(new RTCSessionDescription(offer));
    const answer = pc.createAnswer();
    pc.setLocalDescription(answer);

    ws.send(JSON.stringify({"type":"answer","data":{"target":user_id,"answer":answer}}))

}

function sendOffer(user_id){
    console.log(`Sending offer to ${user_id}`)

    const offer = pc.createOffer();
    pc.setLocalDescription(offer);

    ws.send(JSON.stringify({"type":"offer","data":{"target":user_id,"offer":offer}}))
}

function connectToAnswerer(user_id,data){

    answer = data["answer"]
    // const pc = peerConnections[userId];
    pc.setRemoteDescription(new RTCSessionDescription(answer));

    
}

function join(){

    input = document.getElementById("roomInput").value
    random_number = getRandomInt(10,99)
    document.getElementById("user_id").innerText = random_number
    ws = new WebSocket(`ws://localhost:8000/ws/${input}/${random_number}`);
    setLocalStream()
    room_id = input

    ws.onopen = function(event){
        ws.send(JSON.stringify({"type":"join","data":{}}))
    }
    ws.onmessage = function(event) {
        data = JSON.parse(event.data)
        console.log(data)
        switch(data["type"]){
            case "join":
                // Let's send offer
                console.log("New user join")
                sendOffer(data["data"]["user_id"])
                break
            case "offer":
                // Let's answer
                console.log(`New user offer`)
                sendAnswer(data["data"]["user_id"],data)
                break
            case "answer":
                // Answer Receive
                user_id = data["data"]["user_id"]
                console.log(`New user answer from ${user_id}`)
                connectToAnswerer(user_id,data)
                break
        }
        
    };

}