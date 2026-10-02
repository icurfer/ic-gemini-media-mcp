"""Exercise the paid-job boundary without making paid API requests."""

from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

from gemini_media_mcp import server


class FakeClient:
    def __init__(self, operation):
        self.operation = operation
        self.generated = None
        self.downloaded = None
        self.models = SimpleNamespace(generate_videos=self.generate_videos)
        self.operations = SimpleNamespace(get=self.get)
        self.files = SimpleNamespace(download=self.download)

    def generate_videos(self, **kwargs):
        self.generated = kwargs
        return self.operation

    def get(self, operation):
        assert operation.name == self.operation.name
        return self.operation

    def download(self, *, file):
        self.downloaded = file
        return b"video-data"

    def close(self):
        pass


class VideoToolsTest(TestCase):
    def test_start_and_download_survive_server_restart(self):
        video = SimpleNamespace(video="google-video-reference")
        response = SimpleNamespace(generated_videos=[video])
        pending = SimpleNamespace(name="models/veo/operations/job-1", done=False, error=None, response=None, result=None)
        finished = SimpleNamespace(name=pending.name, done=True, error=None, response=response, result=None)
        first_client = FakeClient(pending)
        second_client = FakeClient(finished)
        with TemporaryDirectory() as directory, patch.object(server, "_client", side_effect=[first_client, second_client, second_client]):
            started = server.start_video(prompt="A knight walks in place", duration_seconds=8)
            self.assertEqual(started["operation_name"], pending.name)
            self.assertFalse(started["done"])
            self.assertEqual(first_client.generated["model"], "veo-3.1-fast-generate-preview")
            self.assertEqual(server.check_video(pending.name)["video_count"], 1)
            target = Path(directory) / "knight.mp4"
            downloaded = server.download_video(pending.name, str(target))
            self.assertTrue(downloaded["saved"])
            self.assertEqual(target.read_bytes(), b"video-data")
            self.assertEqual(second_client.downloaded, "google-video-reference")
            with self.assertRaises(FileExistsError):
                server.download_video(pending.name, str(target))

    def test_rejects_invalid_job_before_api_call(self):
        with patch.object(server, "_client") as client:
            for kwargs in (
                {"prompt": ""},
                {"prompt": "walk", "duration_seconds": 5},
                {"prompt": "walk", "reference_image_paths": ["a.png"], "image_path": "b.png"},
                {"prompt": "walk", "last_frame_path": "b.png"},
                {"prompt": "walk", "model": "veo-3.1-lite-generate-preview", "resolution": "4k"},
            ):
                with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                    server.start_video(**kwargs)
            client.assert_not_called()

    def test_key_status_never_returns_key(self):
        with patch.object(server, "_api_key", return_value="private-secret"):
            self.assertNotIn("private-secret", str(server.key_status()))
