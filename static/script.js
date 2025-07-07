let mediaRecorder;
let audioStream; // To store the MediaStream so we can stop tracks
let ws;
const messagesDiv = document.getElementById('messages');
const startButton = document.getElementById('startRecording');
const stopButton = document.getElementById('stopRecording');

// --- Event Listeners for Buttons ---
startButton.onclick = () => startStreaming();
stopButton.onclick = () => stopStreaming();

function appendMessage(text, className = '') {
    const li = document.createElement('li');
    li.textContent = text;
    if (className) {
        li.classList.add(className);
    }
    messagesDiv.prepend(li); // Add to the top
    // Keep only a certain number of messages (e.g., 50)
    if (messagesDiv.children.length > 50) {
        messagesDiv.removeChild(messagesDiv.lastChild);
    }
}

async function startStreaming() {
    appendMessage("Attempting to start recording...", "status-message");
    startButton.disabled = true; // Disable start button
    stopButton.disabled = false; // Enable stop button

    try {
        // 1. Get access to the microphone
        audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        appendMessage("Microphone access granted.", "status-message");

        // 2. Create a MediaRecorder instance
        mediaRecorder = new MediaRecorder(audioStream);
        appendMessage("MediaRecorder initialized.", "status-message");

        // 3. Connect to your backend WebSocket
        // IMPORTANT: Replace with the actual URL of your backend's WebSocket endpoint
        ws = new WebSocket("ws://localhost:8000/ws/audio"); // Adjust if your backend is different

        ws.onopen = () => {
            console.log("WebSocket connection opened");
            appendMessage("WebSocket connected to backend.", "status-message");
            // 4. Start recording and sending data every 2 seconds
            mediaRecorder.start(2000); // Emit data every 2 seconds
            appendMessage("MediaRecorder started, sending WebM/Opus chunks every 2 seconds.", "status-message");
        };

        ws.onmessage = (event) => {
            console.log("Message from backend:", event.data);
            appendMessage(`Backend: ${event.data}`);
        };

        ws.onerror = (error) => {
            console.error("WebSocket error:", error);
            appendMessage(`WebSocket Error: ${error.message || 'Unknown error'}`, "error-message");
            stopStreaming(); // Attempt to stop on error
        };

        ws.onclose = (event) => {
            console.log("WebSocket connection closed:", event.code, event.reason);
            appendMessage(`WebSocket disconnected. Code: ${event.code}, Reason: ${event.reason || 'N/A'}`, "status-message");
            stopStreaming(); // Ensure buttons are reset if connection closes
        };

        // 5. Listen for dataavailable events from MediaRecorder
        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                console.log("Sending audio chunk of size:", event.data.size, "bytes. Type:", event.data.type);
                appendMessage(`Sending audio chunk (${event.data.size} bytes)...`);
                if (ws && ws.readyState === WebSocket.OPEN) {
                    ws.send(event.data);
                } else {
                    console.warn("WebSocket not open, cannot send audio chunk.");
                    appendMessage("WebSocket not open, cannot send audio.", "error-message");
                }
            } else {
                console.warn("Empty audio chunk received from MediaRecorder.");
            }
        };

        mediaRecorder.onstop = () => {
            console.log("MediaRecorder stopped.");
            appendMessage("MediaRecorder stopped.", "status-message");
            // Clean up stream tracks when recording stops
            if (audioStream) {
                audioStream.getTracks().forEach(track => track.stop());
                console.log("Microphone tracks stopped.");
                appendMessage("Microphone tracks released.", "status-message");
            }
        };

    } catch (err) {
        console.error("Error accessing microphone or starting stream:", err);
        appendMessage(`Error: ${err.message}. Please ensure microphone access is granted.`, "error-message");
        startButton.disabled = false; // Re-enable start if there's an initial error
        stopButton.disabled = true;
    }
}

function stopStreaming() {
    appendMessage("Stopping streaming...", "status-message");
    startButton.disabled = false; // Enable start button
    stopButton.disabled = true; // Disable stop button

    // Stop the MediaRecorder
    if (mediaRecorder && mediaRecorder.state === "recording") {
        mediaRecorder.stop();
    }

    // Close the WebSocket connection
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.close();
    } else if (ws && ws.readyState === WebSocket.CONNECTING) {
        // If it's still connecting, wait for it to open or fail and then close
        ws.onopen = () => ws.close();
    }

    // Clean up microphone stream if it's still active (important for releasing mic)
    if (audioStream) {
        audioStream.getTracks().forEach(track => track.stop());
        console.log("Microphone tracks explicitly stopped during stopStreaming.");
        appendMessage("Microphone tracks released.", "status-message");
    }
}

// Initial state of buttons when the script loads
startButton.disabled = false;
stopButton.disabled = true;