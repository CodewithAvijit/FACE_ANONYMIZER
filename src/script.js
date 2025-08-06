const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const resultImage = document.getElementById('resultImage');
const anonymizeSwitch = document.getElementById('anonymizeSwitch');
const toggleBtn = document.getElementById('toggleBtn');

let streamActive = false;
let intervalId = null;

// Access webcam
navigator.mediaDevices.getUserMedia({ video: true })
  .then(stream => {
    video.srcObject = stream;
  })
  .catch(err => {
    alert('Camera access denied.');
    console.error(err);
  });

async function sendFrameToBackend() {
  const context = canvas.getContext('2d');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  context.drawImage(video, 0, 0, canvas.width, canvas.height);

  canvas.toBlob(async (blob) => {
    const formData = new FormData();
    formData.append('file', blob, 'frame.jpg');
    formData.append('anonymize', anonymizeSwitch.checked);

    try {
      const res = await fetch('http://127.0.0.1:8000/anonymize', {
        method: 'POST',
        body: formData
      });

      if (!res.ok) throw new Error("Server error");

      const resultBlob = await res.blob();
      resultImage.src = URL.createObjectURL(resultBlob);
    } catch (err) {
      console.error('Error sending frame:', err);
    }
  }, 'image/jpeg');
}

// Start or stop real-time processing
toggleBtn.addEventListener('click', () => {
  if (streamActive) {
    clearInterval(intervalId);
    toggleBtn.textContent = "Start";
  } else {
    intervalId = setInterval(sendFrameToBackend, 100); // ~6-7 FPS
    toggleBtn.textContent = "Stop";
  }
  streamActive = !streamActive;
});
