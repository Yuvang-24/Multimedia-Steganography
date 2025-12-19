import numpy as np

# --------------------------------------------------
# Convert raw WAV frames → numpy samples
# --------------------------------------------------
def samples_from_frames(frames, sampwidth, nchannels):
    """
    Convert byte frames from wave file into numpy array samples.
    
    frames     : raw bytes from wave.readframes()
    sampwidth  : sample width in bytes (1 or 2)
    nchannels  : number of audio channels
    
    returns    : numpy array of samples
    """
    if sampwidth == 1:
        dtype = np.uint8
    elif sampwidth == 2:
        dtype = np.int16
    else:
        raise ValueError("Unsupported sample width")

    samples = np.frombuffer(frames, dtype=dtype)

    if nchannels > 1:
        samples = samples.reshape(-1, nchannels)

    return samples


# --------------------------------------------------
# Convert numpy samples → raw WAV frames
# --------------------------------------------------
def frames_from_samples(samples, sampwidth):
    """
    Convert numpy array samples back to raw byte frames.
    
    samples   : numpy array
    sampwidth : sample width in bytes (1 or 2)
    
    returns   : byte frames for wave.writeframes()
    """
    if sampwidth == 1:
        return samples.astype(np.uint8).tobytes()
    elif sampwidth == 2:
        return samples.astype(np.int16).tobytes()
    else:
        raise ValueError("Unsupported sample width")


# --------------------------------------------------
# Extract LSB bits from samples
# --------------------------------------------------
def extract_bits_from_samples(samples, bits_per_sample, required_bits):
    """
    Extract bits from audio samples using LSB technique.
    
    samples          : numpy array of samples
    bits_per_sample  : number of LSBs used (1 or 2)
    required_bits    : how many bits to extract
    
    returns          : list of extracted bits (0/1)
    """
    flat_samples = samples.flatten() if samples.ndim > 1 else samples
    bits = []

    mask = (1 << bits_per_sample) - 1

    for s in flat_samples:
        for i in reversed(range(bits_per_sample)):
            bits.append((s >> i) & 1)
            if len(bits) >= required_bits:
                return bits

    return bits
