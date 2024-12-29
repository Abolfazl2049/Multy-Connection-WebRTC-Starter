interface participant {
  stream?: MediaStream;
  userId: number;
  pc: RTCPeerConnection;
}
export type {participant};
