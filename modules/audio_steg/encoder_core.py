"""
Contains your original embed_payload and estimate_capacity functions.
Copied directly from your encoder.py.
"""
import struct
from .utils import samples_from_frames, frames_from_samples
import wave

def xor_bytes(data: bytes, password: str):
    if not password:
        return data
    key = password.encode('utf-8')
    return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])

def estimate_capacity(wav_file, bits_per_sample=1):
    with wave.open(wav_file, 'rb') as wf:
        nframes = wf.getnframes()
        nchannels = wf.getnchannels()
        return nframes * nchannels * bits_per_sample

def embed_payload(wav_in, wav_out, payload, bits_per_sample=1, encrypt_password=None, progress_callback=None):
    payload = xor_bytes(payload, encrypt_password)
    payload_len = len(payload)
    payload = struct.pack('>I', payload_len) + payload

    with wave.open(wav_in, 'rb') as wf:
        params = wf.getparams()
        frames = wf.readframes(params.nframes)

    samples = samples_from_frames(frames, params.sampwidth, params.nchannels)
    flat = samples.flatten() if params.nchannels > 1 else samples

    bits = []
    for byte in payload:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)

    mask = (1 << bits_per_sample) - 1
    total_samples = len(flat)

    for i, s in enumerate(flat):
        if i * bits_per_sample >= len(bits):
            break
        value = 0
        for j in range(bits_per_sample):
            if i * bits_per_sample + j < len(bits):
                value = (value << 1) | bits[i * bits_per_sample + j]
        flat[i] = (s & (~mask)) | value

    if params.nchannels > 1:
        samples = flat.reshape(-1, params.nchannels)
    else:
        samples = flat

    new_frames = frames_from_samples(samples, params.sampwidth)

    with wave.open(wav_out, 'wb') as wf:
        wf.setparams(params)
        wf.writeframes(new_frames)
