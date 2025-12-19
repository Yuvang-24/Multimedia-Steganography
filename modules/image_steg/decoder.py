from stegano import lsb

def decode(stego_image_path):
    secret = lsb.reveal(stego_image_path)

    if secret is None:
        raise ValueError("No hidden text found")

    return secret
