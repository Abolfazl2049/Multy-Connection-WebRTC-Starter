<script setup lang="ts">
let localStream = ref();
let ws = ref<WebSocket>();
let participants = ref<{pc: RTCPeerConnection; userId: number; stream?: MediaStream}[]>([]);
let roomId = ref("s");

let initWebrtc = async (userId: number) => {
  participants.value.push({pc: new RTCPeerConnection(), userId: userId});
  let participant = participants.value[participants.value.length - 1];
  participant.pc.onicecandidate = (e: any) => {
    let candidateData:
      | {
          candidate: any;
          sdpMid: any;
          sdpMLineIndex: any;
        }
      | undefined = undefined;
    if (e.candidate)
      candidateData = {
        candidate: e.candidate.candidate,
        sdpMid: e.candidate.sdpMid,
        sdpMLineIndex: e.candidate.sdpMLineIndex
      };

    ws.value?.send(
      JSON.stringify({
        type: "candidate",
        data: {
          candidate: candidateData,
          target: userId
        }
      })
    );
  };
  participant.pc.ontrack = (e: any) => (participant.stream = e?.streams[0]);
  await localStream.value.getTracks().forEach((track: any) => participant.pc?.addTrack(track, localStream.value));
};
const handle = () => {
  const answer = async (data: any) => {
    let participant = participants.value.find(el => el.userId === data.user_id);
    await participant?.pc?.setRemoteDescription({type: "answer", sdp: data.sdp});
  };
  const offer = async (data: any) => {
    await initWebrtc(data.user_id);
    let participant = participants.value.find(el => el.userId === data.user_id);
    await participant?.pc?.setRemoteDescription({type: "offer", sdp: data.sdp});
    const answer = await participant?.pc?.createAnswer();
    ws.value?.send(JSON.stringify({type: "answer", data: {sdp: answer?.sdp, target: data.user_id}}));
    await participant?.pc?.setLocalDescription(answer);
  };
  const candidate = async (data: any) => {
    console.log("candidate");
    let participant = participants.value.find(el => el.userId === data.user_id);
    await participant?.pc?.addIceCandidate(data.candidate);
  };

  const join = async (data: any) => {
    await initWebrtc(data.user_id);
    let participant = participants.value.find(el => el.userId === data.user_id);
    const offer = await participant?.pc?.createOffer();
    ws.value?.send(JSON.stringify({type: "offer", data: {sdp: offer?.sdp, target: data.user_id}}));
    await participant?.pc?.setLocalDescription(offer);
  };
  const left = (data: any) => {
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

function join() {
  for (let i of participants.value) i.pc.close();
  participants.value = [];
  ws.value?.close();
  ws.value = new WebSocket(`ws://192.168.4.148:8000/ws/${roomId.value}/${Math.floor(Math.random() * (99 - 10) + 10)}`);
  ws.value.onopen = function () {
    ws.value?.send(JSON.stringify({type: "join", data: {}}));
  };
  ws.value.onmessage = function (event: any) {
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
}
navigator.mediaDevices.getUserMedia({video: true, audio: true}).then(stream => {
  localStream.value = stream;
});
</script>
<template>
  <div class="flex p-2 gap-2 border-b">
    <input v-model="roomId" class="border-2 p-1" />
    <button @click="join" class="bg-red-600 text-white p-2">Join room</button>
  </div>
  <div class="p-5 flex flex-wrap gap-5">
    <video :srcObject="localStream" autoplay muted />
    <video v-for="i in participants" :srcObject="i.stream" autoplay />
  </div>
</template>
<style>
video {
  @apply -scale-x-100 size-[200px];
}
</style>
