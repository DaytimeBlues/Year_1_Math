"""Pytest configuration to ensure project root is importable."""
from __future__ import annotations

import sys
from pathlib import Path

# Guarantee the repository root is on sys.path so imports like `import core` work
# even when pytest is invoked via the console script entrypoint.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
