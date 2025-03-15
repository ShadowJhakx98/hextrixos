const pc = new RTCPeerConnection({
  iceServers: [{ urls: "stun:stun.l.google.com:19302" }]
});

// Add screen sharing stream
navigator.mediaDevices.getDisplayMedia().then(stream => {
  stream.getTracks().forEach(track => pc.addTrack(track));
});

// Handle media uploads
const uploadMedia = async (file) => {
  await fetch('/upload_media', {
    method: 'POST',
    body: file
  });
};
