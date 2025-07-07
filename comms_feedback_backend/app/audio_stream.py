# comms_feedback_backend/app/audio_stream.py
from app.asr_transcriber import transcribe_audio
from fastapi import WebSocket, WebSocketDisconnect
import asyncio
import subprocess
import os
import io

# This function defines your WebSocket endpoint logic
async def audio_websocket_endpoint(websocket: WebSocket):
    """
    Handles the WebSocket connection for audio streaming.
    Receives WebM/Opus chunks, decodes them to PCM16 using FFmpeg,
    and sends acknowledgements back.
    """
    await websocket.accept()
    print("WebSocket accepted from client.")

    ffmpeg_process = None

    try:
        # Initialize ffmpeg process to decode WebM/Opus to PCM16
        # Important: These parameters are crucial for real-time streaming:
        # -i pipe:0: Read input from stdin
        # -f s16le: Output format is raw signed 16-bit little-endian PCM
        # -acodec pcm_s16le: Output codec
        # -ar 16000: Output sample rate (Hz)
        # -ac 1: Number of audio channels (1 for mono)
        # -loglevel warning: Suppress verbose output
        # pipe:1: Write output to stdout
        ffmpeg_cmd = [
            "ffmpeg",
            "-i", "pipe:0",
            "-f", "s16le",
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            "-ac", "1",
            "-loglevel", "warning",
            "pipe:1"
        ]

        # Use asyncio.create_subprocess_exec for async process management
        ffmpeg_process = await asyncio.create_subprocess_exec(
            *ffmpeg_cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE # Capture stderr for debugging ffmpeg errors
        )
        print("FFmpeg process started.")

        # Read stderr of ffmpeg to catch any errors during initialization or processing
        async def log_ffmpeg_errors(stderr_reader):
            while True:
                line = await stderr_reader.readline()
                if not line:
                    break
                print(f"FFmpeg stderr: {line.decode().strip()}")

        asyncio.create_task(log_ffmpeg_errors(ffmpeg_process.stderr))


        while True:
            try:
                # Receive binary data (WebM/Opus audio chunk)
                audio_chunk_webm = await websocket.receive_bytes()
                print(f"Received WebM/Opus chunk of size: {len(audio_chunk_webm)} bytes")

                # Write the WebM chunk to ffmpeg's stdin
                ffmpeg_process.stdin.write(audio_chunk_webm)
                await ffmpeg_process.stdin.drain() # Ensure data is truly written

                # Read the decoded PCM data from ffmpeg's stdout
                pcm_data = await ffmpeg_process.stdout.read(32000) # Read a chunk of decoded PCM

                if pcm_data:
                    print(f"Decoded PCM chunk size: {len(pcm_data)} bytes")
                    
                    # 🔍 Transcribe the PCM chunk
                    transcript_result = transcribe_audio(pcm_data)

                    # Send transcript back to frontend
                    await websocket.send_json({
                        "type": "transcript",
                        "text": transcript_result["text"],
                        "words": transcript_result["words"]
                    })

                    # --- Process the PCM16 audio_chunk here ---
                    # This `pcm_data` is now raw 16-bit signed little-endian PCM.
                    # You would integrate your ASR, NLP, Prosody, Scoring, Feedback here.
                    # Example: Send a simple acknowledgement back to frontend
                    await websocket.send_text(f"PCM chunk received! Size: {len(pcm_data)} bytes (from {len(audio_chunk_webm)}B WebM)")
                else:
                    print("No PCM data received from FFmpeg (possibly end of stream or error).")

            except asyncio.TimeoutError:
                print("WebSocket receive timed out. Client might have stopped sending data.")
                break # Exit loop if no data for a while
            except Exception as e:
                print(f"Error during audio processing: {e}")
                # Send an error back to the frontend
                await websocket.send_text(f"Backend processing error: {e}")
                break # Exit loop on unhandled error

    except WebSocketDisconnect:
        print("Client disconnected.")
    except Exception as e:
        print(f"An error occurred during WebSocket connection: {e}")
    finally:
        # Ensure ffmpeg process is terminated
        if ffmpeg_process:
            print("Terminating FFmpeg process...")
            ffmpeg_process.stdin.close() # Close stdin to signal EOF to ffmpeg
            try:
                # Give ffmpeg a moment to clean up, then terminate forcefully if needed
                await asyncio.wait_for(ffmpeg_process.wait(), timeout=5)
                print("FFmpeg process gracefully terminated.")
            except asyncio.TimeoutError:
                print("FFmpeg process did not terminate gracefully, killing it.")
                ffmpeg_process.kill()
            except Exception as e:
                print(f"Error while waiting for ffmpeg process to terminate: {e}")
        print("WebSocket endpoint closed.")