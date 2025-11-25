"""
Unit tests for Image Generator module.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from src.image_gen.image_generator import ImageGenerator


@pytest.fixture
def mock_manager():
    """Create a mock FoundryLocalManager for dependency injection."""
    mock = MagicMock()
    mock.endpoint = "http://localhost:8000"
    mock.api_key = "test-key"

    mock_model_info = MagicMock()
    mock_model_info.id = "nano-banana-2"
    mock.get_model_info.return_value = mock_model_info

    return mock


@pytest.fixture
def image_generator(mock_manager, tmp_path):
    """Create ImageGenerator instance with mocked Foundry using dependency injection."""
    generator = ImageGenerator(
        model_name="nano-banana-2",
        output_dir=str(tmp_path / "images"),
        manager=mock_manager  # Inject mock manager
    )
    return generator


class TestImageGenerator:
    """Test suite for ImageGenerator class."""

    def test_initialization(self, tmp_path, mock_manager):
        """Test ImageGenerator initialization with dependency injection."""
        generator = ImageGenerator(
            output_dir=str(tmp_path / "images"),
            manager=mock_manager
        )

        assert generator.model_name == "nano-banana-2"
        assert generator.output_dir.exists()
        assert generator.manager is mock_manager

    def test_initialization_creates_output_dir(self, tmp_path, mock_manager):
        """Test that initialization creates output directory."""
        output_dir = tmp_path / "test_images"

        generator = ImageGenerator(
            output_dir=str(output_dir),
            manager=mock_manager
        )

        assert output_dir.exists()

    def test_initialization_without_manager_requires_foundry(self, tmp_path):
        """Test that manager parameter allows bypassing Foundry SDK requirement."""
        # When manager is provided, no Foundry SDK needed
        mock = MagicMock()
        generator = ImageGenerator(output_dir=str(tmp_path), manager=mock)
        assert generator.manager is mock

        # Without manager and without foundry_local, would fail (tested by integration)

    def test_generate_architecture_diagram(self, image_generator):
        """Test architecture diagram generation."""
        repo_data = {
            "name": "test-repo",
            "description": "A test repository"
        }

        with patch.object(image_generator, '_generate_image', return_value="/path/to/image.png") as mock_gen:
            result = image_generator.generate_architecture_diagram(repo_data)

            assert result == "/path/to/image.png"
            mock_gen.assert_called_once()

            # Verify prompt contains repo info
            call_args = mock_gen.call_args
            assert "test-repo" in call_args[1]['prompt']
            assert "A test repository" in call_args[1]['prompt']

    def test_generate_problem_solution_flow(self, image_generator):
        """Test problem-solution flow diagram generation."""
        repo_data = {"name": "test-repo"}
        script_data = {
            "hook": "Developers struggle with deployment",
            "solution": "Automated CI/CD pipeline"
        }

        with patch.object(image_generator, '_generate_image', return_value="/path/to/flow.png") as mock_gen:
            result = image_generator.generate_problem_solution_flow(repo_data, script_data)

            assert result == "/path/to/flow.png"

    def test_build_architecture_prompt_basic(self, image_generator):
        """Test architecture prompt building without script data."""
        prompt = image_generator._build_architecture_prompt(
            "test-repo",
            "A test repository",
            None
        )

        assert "test-repo" in prompt
        assert "A test repository" in prompt
        assert "architecture diagram" in prompt.lower()
