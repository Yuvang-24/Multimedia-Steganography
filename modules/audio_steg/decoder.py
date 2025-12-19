"""
Flask wrapper for Audio Steganography Decoding
Uses your original decode() function.
"""

import os
from .decoder_core import decode_core  # we will create decoder_core below

def decode(input_path, output_path, bits=1, password=None):
    if not os.path.exists(input_path):
        raise FileNotFoundError("Encoded WAV not found")

    # decode_core returns extracted bytes
    extracted_bytes = decode_core(
        wav_in=input_path,
        bits_per_sample=bits,
        password=password,
        out_file=output_path,   # web output path
        progress_callback=None
    )

    return output_path   # Flask will send this file to user
