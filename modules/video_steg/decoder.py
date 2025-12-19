"""
Wrapper for extracting payload from a stego video for Flask integration.

Expected call:
    decode(stego_video_path: str, output_path: str, password: str|None = None)

- stego_video_path: path to uploaded stego video
- output_path: desired path (or directory) where extracted file will be saved
- password: password if the payload was encrypted
Returns:
- absolute path to the extracted file (string)
"""
import os
from .video_core import VideoSteganography

def decode(stego_video_path, output_path, password=None, bits=1):
    if not os.path.exists(stego_video_path):
        raise FileNotFoundError(f"Input stego video not found: {stego_video_path}")

    if bits not in (1,2):
        raise ValueError("bits must be 1 or 2")

    vs = VideoSteganography(bits_per_channel=bits)
    saved_path = vs.extract_to_file(in_video=stego_video_path, out_path=output_path, password=password or None, progress_cb=None)
    return saved_path
