# comms_feedback_backend/server/socket_server.py

from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from app.audio_stream import audio_websocket_endpoint # Import the WebSocket handler

app = FastAPI(
    title="Comms Feedback Backend",
    description="Real-time communication feedback system.",
    version="0.1.0"
)

# Mount the static files directory
# This assumes your frontend HTML, CSS, JS are in a 'static' folder
# relative to where this server is run or where your 'run.py' is.
# Make sure your 'static' folder (containing index.html, style.css, script.js)
# is at the same level as the 'comms_feedback_backend' directory, OR
# adjust the 'directory' path if 'static' is inside 'comms_feedback_backend'.
# For the structure you provided, you'd place the 'static' folder outside 'comms_feedback_backend'
# or create a 'static' folder within 'server/' if that's where you want your frontend files.

# Assuming 'static' is a top-level folder alongside 'comms_feedback_backend'
# OR, if 'static' is INSIDE 'comms_feedback_backend', you might use:
# app.mount("/static", StaticFiles(directory="comms_feedback_backend/static"), name="static_files")
# And then your index.html would link to /static/style.css, /static/script.js

# For this example, let's assume 'static' is *sibling* to 'comms_feedback_backend'
# For the exact structure you provided, the 'static' folder for frontend files
# should be outside the 'comms_feedback_backend' folder, or you'll need a different path.
# Let's assume the frontend 'static' folder is at the root level where 'run.py' is.
app.mount("/static", StaticFiles(directory="static"), name="static_files")

# You can also make the root '/' serve your index.html
# Create a default route that points to your index.html within the 'static' folder
@app.get("/")
async def serve_index():
    from fastapi.responses import FileResponse
    # Adjust this path if your index.html is nested differently
    return FileResponse("static/index.html", media_type="text/html")


# Define the WebSocket endpoint using the imported handler
@app.websocket("/ws/audio")
async def ws_audio_route(websocket: WebSocket):
    await audio_websocket_endpoint(websocket)