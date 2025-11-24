"""
Narration Generator module.

Generates audio narration using Edge TTS for video reels.
"""

import logging
import asyncio
from pathlib import Path
from typing import Optional
import edge_tts

class NarrationGenerator:
    """
    Generates audio narration using Edge TTS.
    """

    def __init__(self, output_dir: str = "blog/assets/audio"):
        """
        Initialize NarrationGenerator.

        Args:
            output_dir: Directory to save audio files.
        """
        self.logger = logging.getLogger(__name__)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Default voice (can be customized)
        self.voice = "en-US-ChristopherNeural"  # Professional male voice
        # Alternative: "en-US-AriaNeural" for female voice

    async def generate_narration(
        self,
        text: str,
        output_filename: str,
        rate: str = "+0%",
        volume: str = "+0%"
    ) -> Optional[str]:
        """
        Generate audio narration from text.

        Args:
            text: Text to narrate.
            output_filename: Name for the output audio file.
            rate: Speech rate adjustment (e.g., "+10%" for faster, "-10%" for slower).
            volume: Volume adjustment (e.g., "+20%" for louder).

        Returns:
            Path to the generated audio file, or None if failed.
        """
        try:
            self.logger.info(f"Generating narration for: {output_filename}")

            output_path = self.output_dir / output_filename

            # Create TTS communication
            communicate = edge_tts.Communicate(
                text=text,
                voice=self.voice,
                rate=rate,
                volume=volume
            )

            # Save audio
            await communicate.save(str(output_path))

            self.logger.info(f"Narration saved to {output_path}")
            return str(output_path)

        except Exception as e:
            self.logger.error(f"Failed to generate narration: {e}", exc_info=True)
            return None

    async def generate_20s_narration(
        self,
        text: str,
        repo_name: str
    ) -> Optional[str]:
        """
        Generate a 20-second narration optimized for reels.

        Automatically adjusts speech rate to fit approximately 20 seconds.

        Args:
            text: Text to narrate (should be condensed for 20s).
            repo_name: Repository name for filename.

        Returns:
            Path to the generated audio file, or None if failed.
        """
        # Estimate: ~150 words per minute at normal speed
        # For 20 seconds: ~50 words max
        # If text is longer, speed up slightly

        word_count = len(text.split())

        # Adjust rate based on word count
        if word_count > 60:
            rate = "+20%"  # Speed up
        elif word_count > 50:
            rate = "+10%"
        else:
            rate = "+0%"

        safe_name = repo_name.lower().replace(" ", "-").replace("/", "-")
        output_filename = f"{safe_name}-narration.mp3"

        return await self.generate_narration(
            text=text,
            output_filename=output_filename,
            rate=rate,
            volume="+10%"  # Slightly louder for video
        )

    def list_available_voices(self) -> list:
        """
        List available Edge TTS voices.

        Returns:
            List of available voice names.
        """
        # This is a synchronous wrapper for the async function
        return asyncio.run(self._list_voices_async())

    async def _list_voices_async(self) -> list:
        """Async helper to list voices."""
        voices = await edge_tts.list_voices()
        return [v["Name"] for v in voices if v["Locale"].startswith("en-")]
