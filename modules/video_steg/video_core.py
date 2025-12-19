import os
import cv2
import json
import struct
import hashlib
import tempfile
import subprocess

# --------------------------------------------------
# Helper: convert bytes to bits
# --------------------------------------------------
def bytes_to_bits(data: bytes):
    for byte in data:
        for i in range(7, -1, -1):
            yield (byte >> i) & 1

# --------------------------------------------------
# Helper: convert bits to bytes
# --------------------------------------------------
def bits_to_bytes(bits):
    out = bytearray()
    for i in range(0, len(bits), 8):
        byte = 0
        for b in bits[i:i+8]:
            byte = (byte << 1) | b
        out.append(byte)
    return bytes(out)

# --------------------------------------------------
# Video Steganography Core Class
# --------------------------------------------------
class VideoSteganography:
    """
    LSB-based Video Steganography
    - Hides ANY file inside a video
    - Uses lossless video processing
    """

    def __init__(self, bits_per_channel=1):
        if bits_per_channel not in (1, 2):
            raise ValueError("bits_per_channel must be 1 or 2")
        self.bits = bits_per_channel

    # --------------------------------------------------
    # Embed file into video
    # --------------------------------------------------
    def embed_file_into_video(
        self,
        in_video: str,
        payload_path: str,
        out_video: str,
        password=None,
        compress=True,
        progress_cb=None
    ):
        if not os.path.exists(in_video):
            raise FileNotFoundError("Input video not found")
        if not os.path.exists(payload_path):
            raise FileNotFoundError("Payload file not found")

        # Read payload
        with open(payload_path, "rb") as f:
            payload = f.read()

        payload_size = len(payload)
        payload_hash = hashlib.md5(payload).hexdigest()

        # Build header
        header = {
            "filename": os.path.basename(payload_path),
            "size": payload_size,
            "md5": payload_hash
        }

        header_bytes = json.dumps(header).encode("utf-8")
        header_len = struct.pack(">I", len(header_bytes))

        final_payload = header_len + header_bytes + payload
        bits = list(bytes_to_bits(final_payload))

        cap = cv2.VideoCapture(in_video)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        capacity = frames * width * height * 3 * self.bits
        if len(bits) > capacity:
            raise ValueError("Payload too large for this video")

        # Prepare output video
        fourcc = cv2.VideoWriter_fourcc(*"FFV1")  # lossless
        writer = cv2.VideoWriter(out_video, fourcc, fps, (width, height))

        bit_index = 0
        total_bits = len(bits)
        payload_done = False

        while True:
          ret, frame = cap.read()

        # 🔴 HARD SAFETY CHECK (THIS FIXES YOUR ERROR)
          if not ret or frame is None:
            break

          if not payload_done:
           height, width, channels = frame.shape

           for y in range(height):
             for x in range(width):
                for c in range(channels):
                    if bit_index < total_bits:
                        frame[y, x, c] = (frame[y, x, c] & 0xFE) | bits[bit_index]
                        bit_index += 1
                    else:
                        payload_done = True
                        break
                if payload_done:
                    break
             if payload_done:
                break

          # ✅ ALWAYS write frame (even after payload is done)
          writer.write(frame)

          # ✅ CLEAN CLOSE (VERY IMPORTANT)
          cap.release()
          writer.release()


        

    # --------------------------------------------------
    # Extract file from video
    # --------------------------------------------------
    def extract_to_file(
        self,
        in_video: str,
        out_path: str,
        password=None,
        progress_cb=None
    ):
        cap = cv2.VideoCapture(in_video)
        bits = []

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            for y in range(frame.shape[0]):
                for x in range(frame.shape[1]):
                    for c in range(3):
                        bits.append(frame[y, x, c] & 1)

        cap.release()

        # Read header length
        if len(bits) < 32:
             raise ValueError("No hidden data found in video (header missing)")

        header_len_bytes = bits_to_bytes(bits[:32])
        if len(header_len_bytes) != 4:
             raise ValueError("Invalid or corrupted stego video (header length unreadable)")

        header_len = struct.unpack(">I", header_len_bytes)[0]

        header_bytes = bits_to_bytes(bits[32:32 + header_len * 8])

        header = json.loads(header_bytes.decode("utf-8"))

        payload_start = 32 + header_len * 8
        payload_end = payload_start + header["size"] * 8
        payload_bits = bits[payload_start:payload_end]

        payload = bits_to_bytes(payload_bits)

        # Save extracted file
        if os.path.isdir(out_path):
            out_file = os.path.join(out_path, header["filename"])
        else:
            out_file = out_path

        with open(out_file, "wb") as f:
            f.write(payload)

        return out_file
