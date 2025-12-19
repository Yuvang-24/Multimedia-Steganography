"""
Contains your original decode() logic extracted from decoder.py
"""

from .utils import samples_from_frames, extract_bits_from_samples
import struct
import wave

def xor_bytes(data: bytes, password: str):
    if not password:
        return data
    key = password.encode('utf-8')
    return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])

def decode_core(wav_in, bits_per_sample=1, password=None, out_file=None, progress_callback=None):
    with wave.open(wav_in, 'rb') as wf:
        params = wf.getparams()
        frames = wf.readframes(params.nframes)

    samples = samples_from_frames(frames, params.sampwidth, params.nchannels)
    flat = samples.flatten() if params.nchannels > 1 else samples

    header_bits = extract_bits_from_samples(flat, bits_per_sample, required_bits=32)
    header_bytes = bytearray()

    for i in range(0, 32, 8):
        byte = 0
        for b in header_bits[i:i+8]:
            byte = (byte << 1) | b
        header_bytes.append(byte)

    payload_len = struct.unpack('>I', header_bytes)[0]
    total_bits = payload_len * 8

    payload_bits = extract_bits_from_samples(flat, bits_per_sample, required_bits=32 + total_bits)[32:]
    data = bytearray()

    for i in range(0, len(payload_bits), 8):
        byte = 0
        for b in payload_bits[i:i+8]:
            byte = (byte << 1) | b
        data.append(byte)

    data = xor_bytes(data, password)

    if out_file:
        with open(out_file, "wb") as f:
            f.write(data)

    return data
