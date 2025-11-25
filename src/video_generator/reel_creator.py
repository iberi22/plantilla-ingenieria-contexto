"""
Reel Creator module.

Generates 20-second vertical videos (9:16) for social media reels.
"""

import logging
import os
from pathlib import Path
from typing import Dict, Optional, List, Any, Tuple
from moviepy import (
    VideoFileClip, ImageClip, TextClip, CompositeVideoClip,
    concatenate_videoclips, ColorClip, AudioFileClip, CompositeAudioClip
)
from moviepy.audio.fx import MultiplyVolume
from moviepy.video.fx import Resize, Crop, FadeIn, FadeOut

# Import YouTube Client
try:
    from uploader.youtube_api_client import YouTubeAPIClient
except ImportError:
    # Fallback if running as a module where uploader is a sibling
    try:
        from src.uploader.youtube_api_client import YouTubeAPIClient
    except ImportError:
        YouTubeAPIClient = None

class ReelCreator:
    """
    Creates vertical video reels from blog post content.
    """

    def __init__(self, output_dir: str = "blog/assets/videos", enable_upload: bool = False):
        """
        Initialize ReelCreator.

        Args:
            output_dir: Directory to save generated videos.
            enable_upload: Whether to automatically upload to YouTube.
        """
        self.enable_upload = enable_upload
        if enable_upload and YouTubeAPIClient:
            # In a real app, these paths should come from config/env
            self.uploader = YouTubeAPIClient(
                client_secret_file="client_secret.json",
                token_file="token.pickle"
            )
        else:
            self.uploader = None

        self.logger = logging.getLogger(__name__)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Video settings (Vertical 9:16)
        self.width = 1080
        self.height = 1920
        self.fps = 30

        # Colors
        self.bg_color = (31, 41, 55) # Dark gray/blue
        self.text_color = 'white'
        self.accent_color = '#2563eb' # Blue

    def create_reel(
        self,
        repo_name: str,
        script_data: Dict[str, Any],
        images: Dict[str, str],
        audio_path: Optional[str] = None,
        durations: Optional[Dict[str, float]] = None,
        background_music: Optional[str] = None
    ) -> Optional[str]:
        """
        Create a reel with dynamic durations, highlights, and music.

        Args:
            repo_name: Name of the repository/project.
            script_data: Dictionary containing text for sections and optional highlights.
                         e.g., {'hook': 'Text', 'hook_highlights': ['word'], 'solution': ...}
            images: Dictionary of image paths.
            audio_path: Path to narration audio.
            durations: Dictionary of section durations in seconds.
            background_music: Path to background music file.
        """
        self.logger.info(f"Creating reel for {repo_name}...")

        try:
            # Default durations
            section_durations = {
                'intro': 3,
                'problem': 5,
                'solution': 5,
                'architecture': 4,
                'outro': 3
            }
            if durations:
                section_durations.update(durations)

            clips = []

            # 1. Intro
            intro_clip = self._create_intro(repo_name, duration=section_durations['intro'])
            clips.append(intro_clip)

            # 2. Problem (Flow Diagram from Blog)
            problem_img = images.get('flow')
            problem_text = script_data.get('hook', 'Problem Analysis')
            problem_highlights = script_data.get('hook_highlights', [])
            problem_clip = self._create_section(
                "The Problem",
                problem_text,
                problem_img,
                duration=section_durations['problem'],
                highlights=problem_highlights
            )
            clips.append(problem_clip)

            # 3. Solution (Screenshot from Blog or Repo)
            solution_img = images.get('screenshot')
            solution_text = script_data.get('solution', 'The Solution')
            solution_highlights = script_data.get('solution_highlights', [])
            solution_clip = self._create_section(
                "The Solution",
                solution_text,
                solution_img,
                duration=section_durations['solution'],
                highlights=solution_highlights
            )
            clips.append(solution_clip)

            # 4. Architecture (Diagram from Blog)
            arch_img = images.get('architecture')
            arch_text = script_data.get('architecture', 'How it Works')
            arch_highlights = script_data.get('architecture_highlights', [])
            arch_clip = self._create_section(
                "Architecture",
                arch_text,
                arch_img,
                duration=section_durations['architecture'],
                highlights=arch_highlights
            )
            clips.append(arch_clip)

            # 5. Outro
            outro_clip = self._create_outro(duration=section_durations['outro'])
            clips.append(outro_clip)

            # Concatenate Video
            final_video = concatenate_videoclips(clips, method="compose")

            # --- Audio Mixing ---
            audio_tracks = []

            # 1. Narration
            if audio_path and os.path.exists(audio_path):
                narration = AudioFileClip(audio_path)
                # Adjust video duration to match narration if narration is longer than video
                # or cut narration if video is strictly defined by durations.
                # Usually narration drives the video.
                # For this implementation, we will trust the provided durations align with narration segments
                # or just overlay narration and let it cut off or silence video.
                # A better approach (future): Align sections to narration timestamps.

                # For now: simple overlay
                if narration.duration > final_video.duration:
                     final_video = final_video.with_duration(narration.duration) # Extend last frame if needed? No, that's hard with concatenate.
                     # Instead, we just take the min.
                     narration = narration.subclip(0, final_video.duration)

                audio_tracks.append(narration)

            # 2. Background Music
            if background_music and os.path.exists(background_music):
                bg_music = AudioFileClip(background_music)

                # Loop if needed
                if bg_music.duration < final_video.duration:
                     from moviepy.audio.fx import Loop
                     bg_music = bg_music.with_effects([Loop(duration=final_video.duration)])
                else:
                    bg_music = bg_music.subclip(0, final_video.duration)

                # Ducking: Lower volume when narration is present
                # Simple approach: Constant low volume
                bg_music = bg_music.with_effects([MultiplyVolume(0.15)])
                audio_tracks.append(bg_music)

            if audio_tracks:
                final_audio = CompositeAudioClip(audio_tracks)
                final_video = final_video.with_audio(final_audio)

            # Write file
            output_filename = f"{repo_name.lower().replace(' ', '-')}-reel.mp4"
            output_path = self.output_dir / output_filename

            final_video.write_videofile(
                str(output_path),
                fps=self.fps,
                codec='libx264',
                audio_codec='aac',
                threads=4,
                logger=None
            )

            self.logger.info(f"Reel created successfully: {output_path}")

            # Upload if enabled
            if self.enable_upload and self.uploader:
                self._handle_upload(str(output_path), repo_name, script_data)

            return str(output_path)

        except Exception as e:
            self.logger.error(f"Failed to create reel: {e}", exc_info=True)
            return None

    def _create_intro(self, title: str, duration: int) -> CompositeVideoClip:
        """Create intro section."""
        bg = ColorClip(size=(self.width, self.height), color=self.bg_color, duration=duration)
        try:
            txt_clip = TextClip(
                text=title,
                font_size=70,
                color=self.text_color,
                font='Arial-Bold',
                size=(self.width - 100, None),
                method='caption'
            ).with_position('center').with_duration(duration)
            return CompositeVideoClip([bg, txt_clip]).with_effects([FadeIn(0.5), FadeOut(0.5)])
        except Exception:
            return bg

    def _handle_upload(self, video_path: str, repo_name: str, script_data: Dict[str, Any]):
        """
        Handles the automatic upload of the video to YouTube.
        """
        self.logger.info("Starting automatic upload to YouTube...")

        # Generate Metadata
        title = f"{repo_name} - Project Overview 🚀"

        # Generate Description
        description = f"""
        Check out {repo_name}!

        {script_data.get('hook', '')}

        {script_data.get('solution', '')}

        🔗 Read the full blog post: https://your-blog.com/posts/{repo_name.lower().replace(' ', '-')}

        #opensource #coding #dev #tech #{repo_name.replace(' ', '')}
        """

        # Extract potential tags (simple heuristic)
        tags = ["opensource", "programming", "tech", repo_name.split()[0].lower()]
        if "python" in script_data.get('architecture', '').lower():
            tags.append("python")
        if "react" in script_data.get('architecture', '').lower():
            tags.append("react")

        try:
            video_id = self.uploader.upload_video(
                video_path=video_path,
                title=title,
                description=description,
                tags=tags,
                privacy_status="private" # Safety default
            )

            if video_id:
                self.logger.info(f"Successfully uploaded to YouTube! ID: {video_id}")
            else:
                self.logger.warning("Upload failed.")

        except Exception as e:
            self.logger.error(f"Error in upload process: {e}")

    def _create_section(
        self,
        header: str,
        body: str,
        image_path: Optional[str],
        duration: int,
        highlights: List[str] = []
    ) -> CompositeVideoClip:
        """
        Create a content section with image and text overlay.
        Includes optional text highlighting.
        """
        bg = ColorClip(size=(self.width, self.height), color=self.bg_color, duration=duration)
        layers = [bg]

        # Image
        if image_path and os.path.exists(image_path):
            img_clip = ImageClip(image_path).with_duration(duration)

            # Fit and Center
            img_ratio = img_clip.w / img_clip.h
            screen_ratio = self.width / self.height

            if img_ratio > screen_ratio:
                new_h = self.height
                new_w = int(new_h * img_ratio)
            else:
                new_w = self.width
                new_h = int(new_w / img_ratio)

            img_clip = img_clip.with_effects([Resize(height=new_h) if img_ratio > screen_ratio else Resize(width=new_w)])
            img_clip = img_clip.with_position('center')
            layers.append(img_clip)

        # Header (Top)
        try:
            header_bg = ColorClip(size=(self.width, 150), color='black', duration=duration).with_opacity(0.6).with_position(('center', 50))
            layers.append(header_bg)

            header_clip = TextClip(
                text=header,
                font_size=60,
                color=self.accent_color,
                font='Arial-Bold',
                size=(self.width - 40, None),
                method='caption'
            ).with_position(('center', 80)).with_duration(duration)
            layers.append(header_clip)

            # Body Text (Bottom Overlay)
            # Truncate if too long
            display_text = body[:150] + "..." if len(body) > 150 else body

            body_bg = ColorClip(size=(self.width, 400), color='black', duration=duration).with_opacity(0.7).with_position(('center', self.height - 450))
            layers.append(body_bg)

            # Highlight Logic
            # Check if any highlight word is present in the text
            has_highlight = any(h.lower() in display_text.lower() for h in highlights)

            text_color_to_use = self.text_color

            # If highlight found, use accent color for the whole block (MVP solution)
            # A better approach would be splitting strings, but standard TextClip doesn't support mixed format easily.
            if has_highlight:
                text_color_to_use = self.accent_color

            body_clip = TextClip(
                text=display_text,
                font_size=40,
                color=text_color_to_use,
                font='Arial',
                size=(self.width - 100, None),
                method='caption'
            ).with_position(('center', self.height - 400)).with_duration(duration)

            # If highlighted, maybe pulse opacity?
            if has_highlight:
                 # Simple pulse effect: 1.0 -> 0.7 -> 1.0
                 def pulse(t):
                     return 0.85 + 0.15 * ((t * 2) % 1) # Fluctuate between 0.85 and 1.0
                 # body_clip = body_clip.with_effects([Opacity(pulse)]) # Opacity effect needs checking import
                 pass

            layers.append(body_clip)

        except Exception:
            pass

        return CompositeVideoClip(layers).with_effects([FadeIn(0.5), FadeOut(0.5)])

    def _create_outro(self, duration: int) -> CompositeVideoClip:
        """Create outro section."""
        bg = ColorClip(size=(self.width, self.height), color=self.bg_color, duration=duration)
        try:
            txt_clip = TextClip(
                text="Link in Bio\nCheck the Blog!",
                font_size=80,
                color=self.text_color,
                font='Arial-Bold',
                size=(self.width - 100, None),
                method='caption'
            ).with_position('center').with_duration(duration)
            return CompositeVideoClip([bg, txt_clip]).with_effects([FadeIn(0.5), FadeOut(0.5)])
        except Exception:
            return bg
