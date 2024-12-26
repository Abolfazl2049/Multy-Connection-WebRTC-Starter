<script setup lang="ts">
let localStream = ref();
let ws = ref();
let webrtc = ref();
let roomId = ref();
let userId = ref();

let initWebrtc = () => {
  webrtc.value = new RTCPeerConnection();
  webrtc.value.onicecandidate = (e: any) => {
    const message = {
      type: "candidate",
      data: {
        candidate: null
      }
    };
    if (e.candidate) {
      message.data.candidate = e.candidate.candidate;
      message.data.sdpMid = e.candidate.sdpMid;
      message.data.sdpMLineIndex = e.candidate.sdpMLineIndex;
    }
    ws.value.send(JSON.stringify(message));
  };
  webrtc.value.ontrack = (e: any) => console.log(e);
  localStream.value.getTracks().forEach((track: any) => webrtc.value.addTrack(track, localStream.value));
};
const handle = () => {
  const answer = async (userId: number) => {
    
    ws.value.send(JSON.stringify({type: "answer", data: {target: userId}}));
    await webrtc.value.setRemoteDescription(answer);
  };
  const offer = async (userId: number, sdp: string) => {
    
    ws.value.send(JSON.stringify({type: "offer", data: {target: userId}}));
    // initWebrtc();
    await webrtc.value.setRemoteDescription({type: "offer", sdp});
    console.log(`Sending answer to ${userId}`);
    const answer = await webrtc.value.createAnswer();
    ws.value.send({type: "answer", sdp: answer.sdp});
    await webrtc.value.setLocalDescription(answer);
  };
  const candidate = async (candidate: any) => {
    if (!candidate.candidate) {
      await webrtc.value.addIceCandidate(null);
    } else {
      await webrtc.value.addIceCandidate(candidate);
    }
  };

  const join = async (userId: number) => {
    initWebrtc();
    const offer = await webrtc.value.createOffer();
    ws.value.send(JSON.stringify({type: "offer", data: {sdp: offer.sdp, target: userId}}));
    await webrtc.value.setLocalDescription(offer);
  };
  return {
    answer,
    offer,
    candidate,
    join
  };
};

function join() {
  ws.value = new WebSocket(`ws://192.168.4.148:8000/ws/${roomId.value}/${Math.floor(Math.random() * (99 - 10) + 10)}`);
  ws.value.onopen = function (event: any) {
    ws.value.send(JSON.stringify({type: "join", data: {}}));
  };
  ws.value.onmessage = function (event: any) {
    let data = JSON.parse(event.data);
    let userId = data.data.user_id;
    switch (data.type) {
      case "join":
        console.log("New user join");
        handle().join(userId);
        break;
      case "offer":
        console.log(`New user offer`);
        handle().offer(userId, data.data.sdp);
        break;
      case "answer":
        handle().answer(userId);
        console.log(`New user answer from ${userId}`);
        break;
      case "candidate":
        handle().candidate(data);
    }
  };
}
navigator.mediaDevices.getUserMedia({video: true, audio: true}).then(stream => {
  localStream.value = stream;
});
</script>
<template>
  <h1>Meet</h1>
  <p>Enter room id</p>
  <input v-model="roomId" />
  <button @click="join">Join room</button>
  <p>You id:{{ userId }}</p>
  <hr />
  <video :srcObject="localStream" autoplay muted></video>
</template>
