"""
Wrapper for embedding a file into a video for Flask integration.

Expected call:
    encode(input_video_path: str, secret: str|path, output_video_path: str, password: str|None = None, bits: int = 1)

- input_video_path: existing video path (carrier)
- secret: path to payload file to embed (server will read it). For security, prefer file path only.
- output_video_path: where to save the stego video (full path)
- password: optional password string to encrypt payload (AES-GCM)
- bits: 1 or 2 bits per channel (default 1)
Returns: None (raises on error)
"""
import os
from .video_core import VideoSteganography  # see note: we will create a tiny shim to import class

def encode(input_video_path, secret, output_video_path, password=None, bits=1):
    if not os.path.exists(input_video_path):
        raise FileNotFoundError(f"Input video not found: {input_video_path}")
    if not os.path.exists(secret):
        raise FileNotFoundError(f"Payload file not found: {secret}")

    if bits not in (1, 2):
        raise ValueError("bits must be 1 or 2")

    vs = VideoSteganography(bits_per_channel=bits)
    # Use compress=True by default for smaller payloads; change if you want raw
    vs.embed_file_into_video(in_video=input_video_path,
                             payload_path=secret,
                             out_video=output_video_path,
                             password=password or None,
                             compress=True,
                             progress_cb=None)
    return None
