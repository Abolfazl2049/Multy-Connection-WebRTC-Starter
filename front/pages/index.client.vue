<script setup lang="ts">
import type {participant} from "~/types";
let localStream = ref();
let ws = ref<WebSocket>();
let participants = ref<participant[]>([]);
let roomId = ref();

let initPC = (userId: number) => {
  // initialize peer connection

  participants.value.push({pc: new RTCPeerConnection(), userId: userId});
  let participant = participants.value.at(-1) as participant;
  participant.pc.onicecandidate = (e: any) => {
    if (e.candidate)
      ws.value?.send(
        JSON.stringify({
          type: "candidate",
          data: {
            candidate: {
              candidate: e.candidate.candidate,
              sdpMid: e.candidate.sdpMid,
              sdpMLineIndex: e.candidate.sdpMLineIndex
            },
            target: userId
          }
        })
      );
  };
  participant.pc.ontrack = e => (participant.stream = new MediaStream(e.streams[0]));
  localStream.value.getTracks().forEach((track: any) => participant.pc?.addTrack(track, localStream.value));
};

const handle = () => {
  const answer = async (data: any) => {
    // set answer as remote description to the target peerConnection

    let participant = participants.value.find(el => el.userId === data.user_id);
    await participant?.pc?.setRemoteDescription({type: "answer", sdp: data.sdp});
  };

  const offer = async (data: any) => {
    // initialize a peer connection with the target user that sent offer

    initPC(data.user_id);
    let participant = participants.value.find(el => el.userId === data.user_id);
    await participant?.pc?.setRemoteDescription({type: "offer", sdp: data.sdp});
    const answer = await participant?.pc?.createAnswer();
    ws.value?.send(JSON.stringify({type: "answer", data: {sdp: answer?.sdp, target: data.user_id}}));
    await participant?.pc?.setLocalDescription(answer);
  };

  const candidate = async (data: any) => {
    // add candidate to the target peer connection

    let participant = participants.value.find(el => el.userId === data.user_id);
    await participant?.pc?.addIceCandidate(data.candidate);
  };

  const join = async (data: any) => {
    // sent an offer to the joined-user

    initPC(data.user_id);
    let participant = participants.value.find(el => el.userId === data.user_id);
    const offer = await participant?.pc?.createOffer();
    ws.value?.send(JSON.stringify({type: "offer", data: {sdp: offer?.sdp, target: data.user_id}}));
    await participant?.pc?.setLocalDescription(offer);
  };

  const left = (data: any) => {
    // close peer connection with the target-user and remove it from participants

    let participant = participants.value.find(el => el.userId === data.target);
    if (participant) {
      participant.pc?.close();
      participants.value.splice(participants.value.indexOf(participant), 1);
    }
  };
  return {
    answer,
    offer,
    candidate,
    join,
    left
  };
};

let joinRoom = () => {
  // join the target room and listen to socket messages
  let baseURL = "wss://webrtc.moderndata.ir";
  ws.value = new WebSocket(`${baseURL}/ws/${roomId.value}/${Math.floor(Math.random() * (99 - 10) + 10)}`);
  ws.value.onopen = () => ws.value?.send(JSON.stringify({type: "join", data: {}}));
  ws.value.onmessage = (event: any) => {
    let data = JSON.parse(event.data);
    switch (data.type) {
      case "join":
        handle().join(data.data);
        break;
      case "offer":
        handle().offer(data.data);
        break;
      case "answer":
        handle().answer(data.data);
        break;
      case "candidate":
        handle().candidate(data.data);
        break;
      case "left":
        handle().left(data.data);
        break;
    }
  };
};

let leaveRoom = () => {
  // gracefully disconnecting

  ws.value?.close();
  ws.value = undefined;
  for (let i of participants.value) i.pc.close();
  participants.value = [];
};

await navigator.mediaDevices.getUserMedia({video: true, audio: true}).then(stream => {
  localStream.value = stream;
});
</script>
<template>
  <div class="flex p-2 gap-2 border-b">
    <input v-model="roomId" :disabled="ws ? true : false" class="border-2 p-1" placeholder="Room id" />
    <button @click="ws ? leaveRoom() : joinRoom()" class="bg-red-600 text-white p-2">{{ ws ? "Leave Room" : "Join Room" }}</button>
  </div>
  <div class="m-5 *:bg-red-600 space-x-3 *:p-2 text-white">
    <button @click="localStream.getAudioTracks()[0].enabled = !localStream.getAudioTracks()[0].enabled">mute audio</button>
    <button @click="localStream.getVideoTracks()[0].enabled = !localStream.getVideoTracks()[0].enabled">mute video</button>
  </div>
  <div class="p-5 flex flex-wrap gap-5 border">
    <video :srcObject="localStream" autoplay playsinline />
    <video v-for="i in participants" :srcObject="i.stream" autoplay />
  </div>
  <div>
    Note : Enter the same Room id to connect to each other <br />
    And Be patient !
  </div>
</template>
<style>
video {
  @apply -scale-x-100 size-[200px];
}
</style>
