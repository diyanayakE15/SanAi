# app/asr_transcriber.py
from faster_whisper import WhisperModel

# Load model once at startup (adjust model size if needed: tiny, base, small, medium, large-v2)
model = WhisperModel("base", compute_type="float32")  # Use "int8" or "float16" for GPU if available

def transcribe_audio(pcm_data: bytes, sample_rate: int = 16000):
    import numpy as np
    import io

    # Convert PCM16 bytes to float32 numpy array
    audio_np = np.frombuffer(pcm_data, np.int16).astype(np.float32) / 32768.0

    # Transcribe
    segments, info = model.transcribe(audio_np, language="en", beam_size=5, word_timestamps=True)

    full_text = ""
    words_info = []

    for segment in segments:
        full_text += segment.text + " "
        for word in segment.words:
            words_info.append({
                "word": word.word,
                "start": word.start,
                "end": word.end,
                "confidence": getattr(word, "confidence", None)
            })
    print(f"[ASR] Received {len(audio_np)} samples (~{len(audio_np) / 16000:.2f}s)")

    return {
        "text": full_text.strip(),
        "words": words_info
    }
