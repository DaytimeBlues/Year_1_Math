---
description: how to format artifacts for technical review by other LLMs
---

When generating artifacts (implementation plans, walkthroughs, code audits) for Math Omni v2, follow these "LLM-Optimized" standards:

1. **Context Headers**: Include project-wide context summaries (Tech stack: PyQt6, qasync, edge-tts).
2. **Explicit Code Artifacts**: Use full code blocks or detailed diffs for all proposed/modified logic.
3. **Strict Schema**: Use consistent Markdown headers for easy parsing (e.g., `## Proposed Changes`, `## Technical Rationale`, `## Verification Logs`).
4. **Dependency Graphs**: If changing core logic, briefly explain the dependency flow (e.g., `GameManager` -> `AudioService`).
5. **JSON/Structured Metadata**: Where helpful, include small JSON blocks describing the impact (e.g., files changed, complexity estimation).
6. **No Ambiguity**: Avoid "we will update X". Use "Modify `core/audio_service.py:L140` to include error retry logic".

// turbo-all
