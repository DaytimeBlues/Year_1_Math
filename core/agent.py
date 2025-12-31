"""
Pedagogical Agent - Text-to-Speech + Growth Mindset Feedback
Combines audio output with educational feedback logic.

VOICE OPTIONS:
- edge-tts: Microsoft Neural voices (natural, requires internet)
- pyttsx3: Windows SAPI voices (robotic, works offline)

PEDAGOGICAL FOUNDATION:
Based on Carol Dweck's Growth Mindset research (Stanford University):
- Praise EFFORT, not intelligence
- View mistakes as learning opportunities
- Encourage process over outcome

Also implements Vygotsky's Zone of Proximal Development:
- Scaffolding: Provide just enough support for success
- Gradually release responsibility as competence grows
"""

import random
import asyncio
import tempfile
import os
import subprocess
from threading import Thread
from config import FEEDBACK, MAX_ATTEMPTS_BEFORE_SCAFFOLDING, VOICE_TYPE, VOICE_NAME

# Conditional imports based on voice type
EDGE_TTS_AVAILABLE = False
if VOICE_TYPE == 'edge-tts':
    try:
        import edge_tts
        EDGE_TTS_AVAILABLE = True
    except ImportError:
        print("[Agent] edge-tts not installed, falling back to pyttsx3")

if not EDGE_TTS_AVAILABLE:
    import pyttsx3


class PedagogicalAgent:
    """
    The pedagogical agent that provides supportive, growth-oriented feedback
    with voice output.
    
    PERSONALITY DESIGN:
    Warm, patient, and encouraging. Never expresses disappointment or
    frustration. Celebrates effort and reframes mistakes as discoveries.
    Think of a kind, enthusiastic kindergarten teacher.
    """
    
    def __init__(self):
        self.attempt_count = 0
        self.consecutive_errors = 0
        
        # Initialize TTS engine based on config
        if EDGE_TTS_AVAILABLE:
            self.voice_type = 'edge-tts'
            self.voice_name = VOICE_NAME
            self._temp_audio_file = os.path.join(tempfile.gettempdir(), "math_omni_speech.mp3")
        else:
            self.voice_type = 'pyttsx3'
            self.engine = pyttsx3.init()
            self._configure_pyttsx3_voice()
    
    def _configure_pyttsx3_voice(self):
        """
        Configure pyttsx3 voice for optimal child engagement.
        Fallback when edge-tts is unavailable.
        """
        # Reduce speech rate (150 wpm for clarity)
        self.engine.setProperty('rate', 150)
        
        # Try to select a friendly voice
        voices = self.engine.getProperty('voices')
        for voice in voices:
            # Prefer female voices (Zira on Windows)
            if 'zira' in voice.name.lower() or 'female' in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break
    
    def speak(self, text: str, block: bool = False):
        """
        Speak the given text.
        
        Args:
            text: The message to speak
            block: If True, wait for speech to complete
        """
        if block:
            self._speak_sync(text)
        else:
            # Run in background thread to keep UI responsive
            thread = Thread(target=self._speak_sync, args=(text,))
            thread.daemon = True
            thread.start()
    
    def _speak_sync(self, text: str):
        """Internal synchronous speech method."""
        if self.voice_type == 'edge-tts':
            self._speak_edge_tts(text)
        else:
            self.engine.say(text)
            self.engine.runAndWait()
    
    def _speak_edge_tts(self, text: str):
        """Generate and play speech using edge-tts."""
        async def generate_audio():
            communicate = edge_tts.Communicate(text, self.voice_name)
            await communicate.save(self._temp_audio_file)
        
        # Generate the audio file
        try:
            asyncio.run(generate_audio())
            
            # Play using Windows Media Player (works without external dependencies)
            # Use powershell to play the mp3 file
            subprocess.run(
                ['powershell', '-c', 
                 f'(New-Object Media.SoundPlayer "{self._temp_audio_file}").PlaySync()'],
                capture_output=True,
                timeout=30
            )
        except Exception as e:
            print(f"[Agent] edge-tts playback error: {e}")
            # Try alternative: use Windows Media.MediaPlayer for mp3
            try:
                subprocess.run(
                    ['powershell', '-c', 
                     f'Add-Type -AssemblyName presentationCore; ' +
                     f'$player = New-Object System.Windows.Media.MediaPlayer; ' +
                     f'$player.Open("{self._temp_audio_file}"); ' +
                     f'$player.Play(); Start-Sleep -Seconds 5'],
                    capture_output=True,
                    timeout=30
                )
            except Exception as e2:
                print(f"[Agent] Fallback playback also failed: {e2}")
        
        # Cleanup temp file
        if self._temp_audio_file and os.path.exists(self._temp_audio_file):
            try:
                os.remove(self._temp_audio_file)
            except OSError:
                pass  # OS still has a handle on it, just ignore
    
    def stop(self):
        """Stop any currently playing speech."""
        if self.voice_type != 'edge-tts':
            self.engine.stop()
    
    def reset_for_new_problem(self):
        """
        Reset tracking for a new problem.
        
        Each problem is a fresh start—we don't carry over "failure" state.
        """
        self.attempt_count = 0
        self.consecutive_errors = 0
    
    def get_effort_feedback(self) -> str:
        """Return feedback acknowledging the child's effort."""
        return random.choice(FEEDBACK['effort_acknowledged'])
    
    def get_success_feedback(self) -> str:
        """Return celebration feedback for correct answer."""
        self.consecutive_errors = 0
        return random.choice(FEEDBACK['success_specific'])
    
    def get_gentle_redirect(self) -> str:
        """Return feedback for incorrect answer that encourages retry."""
        self.attempt_count += 1
        self.consecutive_errors += 1
        return random.choice(FEEDBACK['gentle_redirect'])
    
    def should_offer_scaffolding(self) -> bool:
        """Determine if we should offer additional support."""
        return self.consecutive_errors >= MAX_ATTEMPTS_BEFORE_SCAFFOLDING
    
    def get_scaffolding_offer(self) -> str:
        """Return an offer to help."""
        return random.choice(FEEDBACK['scaffolding_offer'])
    
    def get_idle_prompt(self) -> str:
        """Return a gentle prompt for an inactive child."""
        prompts = [
            "I'm here whenever you're ready!",
            "I wonder what you're thinking about?",
            "Take your time! There's no rush.",
            "Would you like to try drawing something?",
            "I can help if you'd like!",
        ]
        return random.choice(prompts)
    
    def evaluate_answer(self, expected: int, drawn: int) -> tuple:
        """
        Evaluate the child's drawn answer.
        
        Args:
            expected: The correct numerical answer
            drawn: The quantity from the child's drawing
        
        Returns:
            Tuple of (is_correct, feedback_message)
        
        GENEROSITY IN INTERPRETATION:
        Being off by 1 might mean they miscounted (understandable at 5)
        rather than lacking conceptual understanding.
        """
        if drawn == expected:
            return (True, self.get_success_feedback())
        
        # Close enough (off by 1)
        elif abs(drawn - expected) == 1:
            self.attempt_count += 1
            self.consecutive_errors += 1
            return (False, f"So close! You drew {drawn} and we needed {expected}. Let's try once more!")
        
        # More than needed
        elif drawn > expected:
            self.attempt_count += 1
            self.consecutive_errors += 1
            return (False, f"Wow, you drew {drawn}! That's more than {expected}. Can you try with fewer?")
        
        # Fewer than needed
        else:
            self.attempt_count += 1
            self.consecutive_errors += 1
            return (False, f"I see {drawn} things. We need {expected}. Keep going, you can add more!")
