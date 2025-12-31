"""
Convert raw PCM audio files to proper WAV format.

The Gemini TTS API returns raw PCM audio (24kHz, 16-bit, mono).
The original generator saved this as .mp3 without encoding.
This script adds proper WAV headers.
"""
import os
import struct
from pathlib import Path

VOICE_BANK_DIR = Path("assets/audio/voice_bank")
OUTPUT_DIR = Path("assets/audio/voice_bank_wav")

# Gemini TTS returns: 24kHz, 16-bit, mono PCM
SAMPLE_RATE = 24000
BITS_PER_SAMPLE = 16
NUM_CHANNELS = 1


def create_wav_header(data_size: int) -> bytes:
    """Create a WAV file header for raw PCM data."""
    byte_rate = SAMPLE_RATE * NUM_CHANNELS * (BITS_PER_SAMPLE // 8)
    block_align = NUM_CHANNELS * (BITS_PER_SAMPLE // 8)
    
    header = struct.pack(
        '<4sI4s4sIHHIIHH4sI',
        b'RIFF',                    # ChunkID
        data_size + 36,             # ChunkSize (file size - 8)
        b'WAVE',                    # Format
        b'fmt ',                    # Subchunk1ID
        16,                         # Subchunk1Size (PCM = 16)
        1,                          # AudioFormat (PCM = 1)
        NUM_CHANNELS,               # NumChannels
        SAMPLE_RATE,                # SampleRate
        byte_rate,                  # ByteRate
        block_align,                # BlockAlign
        BITS_PER_SAMPLE,            # BitsPerSample
        b'data',                    # Subchunk2ID
        data_size                   # Subchunk2Size
    )
    return header


def convert_pcm_to_wav(input_path: Path, output_path: Path) -> bool:
    """Convert a raw PCM file to WAV format."""
    try:
        # Read raw PCM data
        with open(input_path, 'rb') as f:
            pcm_data = f.read()
        
        # Skip leading zeros (padding)
        start = 0
        while start < len(pcm_data) and pcm_data[start] == 0:
            start += 1
        
        # If file is all zeros, skip it
        if start >= len(pcm_data) - 100:
            print(f"  SKIP (empty): {input_path.name}")
            return False
        
        # Find actual PCM start (align to 2 bytes for 16-bit)
        start = start & ~1
        pcm_data = pcm_data[start:]
        
        # Create WAV with header
        wav_header = create_wav_header(len(pcm_data))
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(wav_header)
            f.write(pcm_data)
        
        return True
        
    except Exception as e:
        print(f"  ERROR: {input_path.name} - {e}")
        return False


def main():
    if not VOICE_BANK_DIR.exists():
        print(f"Source directory not found: {VOICE_BANK_DIR}")
        return
    
    mp3_files = list(VOICE_BANK_DIR.glob("*.mp3"))
    print(f"Found {len(mp3_files)} .mp3 files to convert")
    
    success = 0
    failed = 0
    
    for mp3_path in mp3_files:
        # Change extension to .wav
        wav_name = mp3_path.stem + ".wav"
        wav_path = OUTPUT_DIR / wav_name
        
        if convert_pcm_to_wav(mp3_path, wav_path):
            success += 1
            print(f"  OK: {wav_name}")
        else:
            failed += 1
    
    print(f"\nConversion complete: {success} success, {failed} failed")
    print(f"Output directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
