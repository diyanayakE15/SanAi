
import webrtcvad
import numpy as np
import noisereduce as nr

vad = webrtcvad.Vad(1)

def is_speech(frame: bytes) -> bool:
    return vad.is_speech(frame, sample_rate=16000)

def denoise(audio: np.ndarray) -> np.ndarray:
    return nr.reduce_noise(y=audio, sr=16000)
