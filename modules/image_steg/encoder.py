from stegano import lsb
import os

def encode(input_image_path, secret_text, output_image_path):
    if not secret_text:
        raise ValueError("Secret text cannot be empty")

    # stegano returns a PIL Image object
    stego_img = lsb.hide(input_image_path, secret_text)

    # Always save as PNG (lossless)
    stego_img.save(output_image_path)
