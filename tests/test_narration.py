import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from pathlib import Path
from src.video_generator.narration_generator import NarrationGenerator

@pytest.mark.asyncio
async def test_generate_narration():
    """Test basic narration generation."""
    generator = NarrationGenerator(output_dir="tests/output/audio")

    with patch('edge_tts.Communicate') as mock_communicate:
        mock_comm_instance = AsyncMock()
        mock_communicate.return_value = mock_comm_instance

        result = await generator.generate_narration(
            text="This is a test narration",
            output_filename="test.mp3"
        )

        assert result is not None
        assert "test.mp3" in result
        assert mock_communicate.called
        assert mock_comm_instance.save.called

@pytest.mark.asyncio
async def test_generate_20s_narration():
    """Test 20-second narration generation with rate adjustment."""
    generator = NarrationGenerator(output_dir="tests/output/audio")

    with patch('edge_tts.Communicate') as mock_communicate:
        mock_comm_instance = AsyncMock()
        mock_communicate.return_value = mock_comm_instance

        # Test with short text (should use normal rate)
        short_text = "Short narration text"
        result = await generator.generate_20s_narration(short_text, "test-repo")

        assert result is not None
        assert "test-repo-narration.mp3" in result

        # Verify rate was set to +0% for short text
        call_args = mock_communicate.call_args
        assert call_args.kwargs['rate'] == "+0%"

@pytest.mark.asyncio
async def test_generate_20s_narration_long_text():
    """Test 20-second narration with long text (should speed up)."""
    generator = NarrationGenerator(output_dir="tests/output/audio")

    with patch('edge_tts.Communicate') as mock_communicate:
        mock_comm_instance = AsyncMock()
        mock_communicate.return_value = mock_comm_instance

        # Test with long text (should speed up)
        long_text = " ".join(["word"] * 70)  # 70 words
        result = await generator.generate_20s_narration(long_text, "test-repo")

        assert result is not None

        # Verify rate was increased for long text
        call_args = mock_communicate.call_args
        assert call_args.kwargs['rate'] in ["+10%", "+20%"]

def test_narration_generator_init():
    """Test NarrationGenerator initialization."""
    generator = NarrationGenerator(output_dir="tests/output/audio")

    assert generator.output_dir.exists()
    assert generator.voice == "en-US-ChristopherNeural"
