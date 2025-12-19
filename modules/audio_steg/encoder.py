"""
Flask wrapper for Audio Steganography Encoding
Uses your original embed_payload() function.
"""

import os
from .utils import samples_from_frames, frames_from_samples
from .encoder_core import embed_payload, estimate_capacity  # we will create encoder_core below

def encode(input_path, secret, output_path, bits=1, password=None):
    if not os.path.exists(input_path):
        raise FileNotFoundError("Input WAV file not found.")

    # Secret may be file path OR text string
    if isinstance(secret, str) and os.path.exists(secret):
        # secret is a file path
        payload = open(secret, 'rb').read()
    else:
        payload = str(secret).encode("utf-8")

    # Capacity check
    capacity_bits = estimate_capacity(input_path, bits_per_sample=bits)
    if len(payload) * 8 > capacity_bits:
        raise ValueError(
            f"Payload too large. Max capacity = {capacity_bits//8} bytes."
        )

    # Perform embedding
    embed_payload(
        wav_in=input_path,
        wav_out=output_path,
        payload=payload,
        bits_per_sample=bits,
        encrypt_password=password,
        progress_callback=None   # web mode → no progress bar
    )

    return output_path
