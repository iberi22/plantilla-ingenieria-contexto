import os
import logging
import pickle
import time
import random
from typing import Optional, List, Dict, Any
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# Scopes required for uploading and managing videos
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly"
]

class YouTubeAPIClient:
    """
    A robust client for the YouTube Data API v3, focused on video uploads.
    Includes retry logic, metadata management, and proper OAuth handling.
    """

    def __init__(self, client_secret_file: str, token_file: str = "token.pickle"):
        self.client_secret_file = client_secret_file
        self.token_file = token_file
        self.service = None
        self.logger = logging.getLogger(__name__)

    def authenticate(self) -> bool:
        """
        Authenticates the user and sets up the YouTube service.
        Handles token loading, refreshing, and initial authorization.
        """
        credentials = None

        # Load existing credentials
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, "rb") as token:
                    credentials = pickle.load(token)
            except Exception as e:
                self.logger.error(f"Failed to load token file: {e}")

        # Refresh or create new credentials
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                self.logger.info("Refreshing access token...")
                try:
                    credentials.refresh(Request())
                except Exception as e:
                    self.logger.error(f"Failed to refresh token: {e}")
                    credentials = None # Force re-auth

            if not credentials:
                self.logger.info("Fetching new tokens (User Interaction Required)...")
                if not os.path.exists(self.client_secret_file):
                     self.logger.error(f"Client secret file not found at {self.client_secret_file}")
                     return False

                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.client_secret_file, SCOPES
                    )
                    credentials = flow.run_local_server(port=0)
                except Exception as e:
                    self.logger.error(f"Failed to run auth flow: {e}")
                    return False

            # Save credentials for next run
            with open(self.token_file, "wb") as token:
                pickle.dump(credentials, token)

        try:
            self.service = build("youtube", "v3", credentials=credentials)
            return True
        except Exception as e:
            self.logger.error(f"Failed to build YouTube service: {e}")
            return False

    def upload_video(self,
                     video_path: str,
                     title: str,
                     description: str,
                     tags: List[str] = None,
                     category_id: str = "28",
                     privacy_status: str = "private",
                     thumbnail_path: str = None) -> Optional[str]:
        """
        Uploads a video to YouTube with retry logic.

        Returns:
            str: The Video ID if successful, None otherwise.
        """
        if not self.service:
            if not self.authenticate():
                return None

        if not os.path.exists(video_path):
            self.logger.error(f"Video file not found: {video_path}")
            return None

        if tags is None:
            tags = []

        body = {
            "snippet": {
                "title": title[:100], # YouTube max title length
                "description": description[:5000], # YouTube max description length
                "tags": tags,
                "categoryId": category_id
            },
            "status": {
                "privacyStatus": privacy_status,
                "selfDeclaredMadeForKids": False
            }
        }

        media = MediaFileUpload(video_path, chunksize=1024*1024, resumable=True)

        request = self.service.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )

        return self._execute_upload_with_retry(request, video_path, thumbnail_path)

    def _execute_upload_with_retry(self, request, video_path: str, thumbnail_path: str = None) -> Optional[str]:
        response = None
        error = None
        retry_count = 0
        max_retries = 5

        while response is None:
            try:
                status, response = request.next_chunk()
                if status:
                    self.logger.info(f"Uploaded {int(status.progress() * 100)}%")

                if response:
                    video_id = response.get('id')
                    self.logger.info(f"Upload Complete! Video ID: {video_id}")

                    if thumbnail_path and os.path.exists(thumbnail_path):
                        self._upload_thumbnail(video_id, thumbnail_path)

                    return video_id

            except HttpError as e:
                if e.resp.status in [500, 502, 503, 504]:
                    error = e
                    retry_count += 1
                    if retry_count > max_retries:
                        self.logger.error(f"Max retries reached. Upload failed: {e}")
                        return None

                    sleep_time = (2 ** retry_count) + random.random()
                    self.logger.warning(f"Upload failed (status {e.resp.status}). Retrying in {sleep_time:.2f}s...")
                    time.sleep(sleep_time)
                    continue
                else:
                    self.logger.error(f"Non-retriable upload error: {e}")
                    return None
            except Exception as e:
                self.logger.error(f"Unexpected error during upload: {e}")
                return None

        return None

    def _upload_thumbnail(self, video_id: str, thumbnail_path: str):
        """Uploads a custom thumbnail for the video."""
        self.logger.info(f"Uploading thumbnail for video {video_id}...")
        try:
            self.service.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path)
            ).execute()
            self.logger.info("Thumbnail uploaded successfully.")
        except Exception as e:
            self.logger.error(f"Failed to upload thumbnail: {e}")
