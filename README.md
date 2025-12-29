# Math Omni v2 🥚

A gamified math learning platform for young children (ages 4-6), inspired by Reading Eggs/Mathseeds.

## Features

- 🎮 **Tap-based gameplay** - Large 96px touch targets for small hands
- 🧠 **Adaptive difficulty** - Linear scaling from counting 1-3 to counting up to 20
- 🥚 **Egg economy** - Earn eggs for correct answers (persists via SQLite)
- 🔊 **Voice prompts** - Neural TTS with edge-tts (non-blocking)
- 🎨 **Accessibility-first** - Dyslexia-friendly fonts, high contrast, debounce protection

## Tech Stack

- **UI Framework:** PyQt6 + qasync
- **Database:** SQLite (aiosqlite)
- **Text-to-Speech:** edge-tts
- **Target Platform:** Windows

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/math-omni-v2.git
cd math-omni-v2
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Architecture

```
main.py → GameManager → MapView / ActivityView
    ↓
DatabaseService + AudioService + ProblemFactory
```

## License

MIT
