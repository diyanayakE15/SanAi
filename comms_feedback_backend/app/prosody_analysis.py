
from pyAudioAnalysis import audioBasicIO, ShortTermFeatures
import numpy as np

def extract_prosody(wav_path: str):
    Fs, x = audioBasicIO.read_audio_file(wav_path)
    F, f_names = ShortTermFeatures.feature_extraction(
        x, Fs, 0.05*Fs, 0.025*Fs)
    return {
        "energy": np.mean(F[f_names.index("energy")]),
        "zero_crossing": np.mean(F[f_names.index("zcr")]),
        # Pitch requires more setup—optional
    }
