import socketio
import time
import base64

sio = socketio.Client()

@sio.event
def connect():
    print("✅ Connected to backend")

@sio.event
def disconnect():
    print("❌ Disconnected from backend")

@sio.on("feedback")
def handle_feedback(data):
    print(f"🟡 Feedback Received for chunk {data['chunk_id']}: {data['message']} (Score: {data['score']})")

# Connect to the backend
sio.connect("http://localhost:5000")

# Simulate sending 5 fake audio chunks
for i in range(5):
    fake_audio = base64.b64encode(b"fake_audio_data_" + str(i).encode()).decode()
    sio.emit("audio_chunk", {
        "chunk_id": i,
        "data": fake_audio,
        "timestamp": time.time()
    })
    time.sleep(1)

print("✅ Waiting for any delayed feedback...")
time.sleep(5)

sio.disconnect()
