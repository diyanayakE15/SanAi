# comms_feedback_backend/run.py

import uvicorn
from server.socket_server import app # Import your FastAPI app instance

if __name__ == "__main__":
    # Ensure this script is run from the project root
    # e.g., 'python run.py' from 'comms_feedback_backend/' parent directory
    uvicorn.run(app, host="0.0.0.0", port=8000)