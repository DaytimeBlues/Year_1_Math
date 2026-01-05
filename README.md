# Math Omni v2 🥚

A gamified math learning platform for young children (ages 4-6), inspired by Reading Eggs/Mathseeds.

## Features

- 🎮 **Tap-based gameplay** - Large 96px touch targets for small hands
- 🧠 **Adaptive difficulty** - Progressive scaling from counting 1-3 to operations up to 20
- 🥚 **Egg economy** - Earn eggs for correct answers (persists via SQLite)
- 🔊 **Offline Voice Prompts** - Pre-recorded voice bank (no internet required)
- 🎨 **Accessibility-first** - Dyslexia-friendly fonts, high contrast, debounce protection

## Tech Stack

- **UI Framework:** PyQt6 + qasync
- **Database:** SQLite (aiosqlite)
- **Audio:** Offline voice bank (WAV/MP3)
- **Target Platform:** Windows

## Installation

```bash
git clone https://github.com/DaytimeBlues/math-omni-gamified.git
cd math-omni-gamified
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
    ↓
VoiceBank (offline audio) + Director (state machine)
```

## Screenshots

<!-- TODO: Add screenshots of the application -->

## License

MIT - See [LICENSE](LICENSE) for details.
