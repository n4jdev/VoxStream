from pydub import AudioSegment
import io
import numpy as np
from scipy import signal

def apply_audio_effects(audio_data):
    # Load audio data
    audio = AudioSegment.from_mp3(io.BytesIO(audio_data))
    
    # Convert to numpy array
    samples = np.array(audio.get_array_of_samples())
    
    # Apply compression
    threshold = 0.5
    ratio = 4.0
    samples_compressed = np.where(
        np.abs(samples) > threshold,
        threshold + (np.abs(samples) - threshold) / ratio * np.sign(samples),
        samples
    )
    
    # Apply subtle distortion
    distortion_factor = 1.2
    samples_distorted = np.tanh(distortion_factor * samples_compressed) * (1 / np.tanh(distortion_factor))
    
    # Apply subtle EQ (boost low-mids, cut highs slightly)
    b, a = signal.butter(4, 1000 / (audio.frame_rate / 2), btype='lowpass')
    samples_eq = signal.lfilter(b, a, samples_distorted)
    
    # Add subtle noise
    noise = np.random.normal(0, 0.001, len(samples_eq))
    samples_with_noise = samples_eq + noise
    
    # Normalize
    samples_normalized = np.int16(samples_with_noise / np.max(np.abs(samples_with_noise)) * 32767)
    
    # Create new AudioSegment
    processed_audio = AudioSegment(
        samples_normalized.tobytes(),
        frame_rate=audio.frame_rate,
        sample_width=2,
        channels=audio.channels
    )
    
    # Export to mp3
    buffer = io.BytesIO()
    processed_audio.export(buffer, format="mp3")
    return buffer.getvalue()
