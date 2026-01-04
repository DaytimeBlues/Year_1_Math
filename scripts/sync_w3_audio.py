import hashlib
import os
from pathlib import Path
import yaml

# Path to the voice bank YAML
YAML_PATH = Path(r"c:\Users\Jihye\.gemini\antigravity\playground\sidereal-voyager\assets\voice_bank.yaml")
AUDIO_DIR = Path(r"c:\Users\Jihye\.gemini\antigravity\playground\sidereal-voyager\assets\audio\voice_bank_wav")

def phrase_to_filename(category: str, index: int, text: str) -> str:
    """Generate consistent filename matching the generator."""
    text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
    clean_cat = category.replace("_", "-")
    return f"{clean_cat}_{index:02d}_{text_hash}.wav"

def sync():
    with open(YAML_PATH, 'r') as f:
        bank = yaml.safe_load(f)
    
    # Categories we just added
    categories = ["w3_takeaway", "w3_zero"]
    
    # Existing mock files we can link to
    mock_files = sorted(list(AUDIO_DIR.glob("q_*_mock.wav")))
    mock_idx = 0
    
    for cat in categories:
        if cat not in bank:
            continue
            
        params = bank[cat]
        for i, text in enumerate(params, 1):
            expected = phrase_to_filename(cat, i, text)
            full_path = AUDIO_DIR / expected
            
            if not full_path.exists():
                if mock_idx < len(mock_files):
                    source = mock_files[mock_idx]
                    print(f"Linking {expected} to {source.name}")
                    # On Windows, we'll just copy for simplicity unless we want symlinks
                    import shutil
                    shutil.copy2(source, full_path)
                    mock_idx += 1
                else:
                    # Reuse last mock if we run out
                    source = mock_files[-1]
                    print(f"Reuse linking {expected} to {source.name}")
                    import shutil
                    shutil.copy2(source, full_path)

if __name__ == "__main__":
    sync()
