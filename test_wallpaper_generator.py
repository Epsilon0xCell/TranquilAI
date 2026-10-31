#!/usr/bin/env python3
"""
Tests for wallpaper_generator.py. Run with: python3 -m unittest -v

No test here touches the network. The Pollinations download is tested
with a stubbed requests.get, Gemini with a stubbed client, and wallpaper
setting with a stubbed run_command. The Gemini package is not installed
in every environment (it is not in mine), so the key selection test
stubs the module global instead of importing the real package.
"""

import io
import os
import sys
import tempfile
import types
import unittest
from unittest import mock

import wallpaper_generator as wg


def make_jpeg_bytes():
    from PIL import Image
    buffer = io.BytesIO()
    Image.new("RGB", (16, 16), (40, 80, 120)).save(buffer, "JPEG")
    return buffer.getvalue()


class FakeResponse:
    def __init__(self, content):
        self.content = content

    def raise_for_status(self):
        pass


class NoTextInstructionTests(unittest.TestCase):
    def test_instruction_is_appended_when_missing(self):
        result = wg.add_no_text_instruction("a quiet lake")
        self.assertTrue(result.endswith(", no text, no letters, no words, no captions"))

    def test_instruction_is_not_duplicated(self):
        prompt = "a quiet lake, no text"
        self.assertEqual(wg.add_no_text_instruction(prompt), prompt)


class GeminiKeyTests(unittest.TestCase):
    def test_fallback_when_gemini_unavailable(self):
        with mock.patch.object(wg, "GEMINI_AVAILABLE", False):
            result = wg.enhance_prompt_with_gemini("a quiet lake")
        self.assertTrue(result.startswith("a quiet lake"))
        self.assertIn("no text", result)

    def test_gemini_api_key_name_is_accepted_on_its_own(self):
        captured = {}

        def fake_client(api_key=None):
            captured["api_key"] = api_key
            models = types.SimpleNamespace(
                generate_content=lambda model, contents: types.SimpleNamespace(text="A detailed quiet lake")
            )
            return types.SimpleNamespace(models=models)

        fake_genai = types.SimpleNamespace(Client=fake_client)
        env = {k: v for k, v in os.environ.items() if k not in ("GOOGLE_API_KEY", "GEMINI_API_KEY")}
        env["GEMINI_API_KEY"] = "GEMKEY-TEST"
        with mock.patch.object(wg, "GEMINI_AVAILABLE", True), \
             mock.patch.object(wg, "genai", fake_genai, create=True), \
             mock.patch.dict(os.environ, env, clear=True):
            result = wg.enhance_prompt_with_gemini("a quiet lake")
        self.assertEqual(captured["api_key"], "GEMKEY-TEST")
        self.assertTrue(result.startswith("A detailed quiet lake"))

    def test_no_key_falls_back_to_original_prompt(self):
        env = {k: v for k, v in os.environ.items() if k not in ("GOOGLE_API_KEY", "GEMINI_API_KEY")}
        with mock.patch.object(wg, "GEMINI_AVAILABLE", True), \
             mock.patch.object(wg, "genai", types.SimpleNamespace(Client=lambda **kw: None), create=True), \
             mock.patch.dict(os.environ, env, clear=True):
            result = wg.enhance_prompt_with_gemini("a quiet lake")
        self.assertTrue(result.startswith("a quiet lake"))


class DownloadTests(unittest.TestCase):
    def test_real_image_bytes_are_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "wallpaper.jpg")
            with mock.patch.object(wg.requests, "get", return_value=FakeResponse(make_jpeg_bytes())):
                self.assertTrue(wg.download_image_from_pollinations("prompt", 64, 64, 1, "flux", out, private=True))
            self.assertTrue(os.path.exists(out))

    def test_non_image_bytes_are_rejected_and_removed(self):
        if not wg.IMAGE_PROCESSING_AVAILABLE:
            self.skipTest("PIL not available, image verification is skipped by the code too")
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "wallpaper.jpg")
            with mock.patch.object(wg.requests, "get", return_value=FakeResponse(b"<html>error page</html>")):
                self.assertFalse(wg.download_image_from_pollinations("prompt", 64, 64, 1, "flux", out, private=True))
            self.assertFalse(os.path.exists(out))

    def test_network_error_returns_false(self):
        def boom(*args, **kwargs):
            raise wg.requests.exceptions.RequestException("no route")

        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "wallpaper.jpg")
            with mock.patch.object(wg.requests, "get", side_effect=boom):
                self.assertFalse(wg.download_image_from_pollinations("prompt", 64, 64, 1, "flux", out, private=True))


class GenerateWallpaperTests(unittest.TestCase):
    def test_private_mode_skips_gemini_and_reports_download_success(self):
        with mock.patch.object(wg, "download_image_from_pollinations", return_value=True) as download, \
             mock.patch.object(wg, "enhance_prompt_with_gemini") as gemini, \
             mock.patch.object(wg, "enhance_image_quality", return_value="/tmp/x.jpg"):
            self.assertTrue(wg.generate_wallpaper("a lake", 64, 64, 7, "/tmp/x.jpg", private=True))
        gemini.assert_not_called()
        sent_prompt = download.call_args[0][0]
        self.assertIn("no text", sent_prompt)

    def test_failed_post_processing_still_reports_generation_success(self):
        with mock.patch.object(wg, "download_image_from_pollinations", return_value=True), \
             mock.patch.object(wg, "enhance_image_quality", return_value=None):
            self.assertTrue(wg.generate_wallpaper("a lake", 64, 64, 7, "/tmp/x.jpg", private=True))

    def test_failed_download_reports_failure(self):
        with mock.patch.object(wg, "download_image_from_pollinations", return_value=False):
            self.assertFalse(wg.generate_wallpaper("a lake", 64, 64, 7, "/tmp/x.jpg", private=True))


@unittest.skipUnless(wg.IMAGE_PROCESSING_AVAILABLE, "PIL not available")
class EnhanceImageQualityTests(unittest.TestCase):
    def test_valid_image_returns_output_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "in.jpg")
            with open(path, "wb") as f:
                f.write(make_jpeg_bytes())
            self.assertEqual(wg.enhance_image_quality(path), path)

    def test_corrupt_image_returns_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad.jpg")
            with open(path, "wb") as f:
                f.write(b"not an image")
            self.assertIsNone(wg.enhance_image_quality(path))


class WallpaperToolTests(unittest.TestCase):
    def test_applescript_check_matches_platform(self):
        expected = sys.platform == "darwin"
        self.assertEqual(wg.check_wallpaper_tool("applescript"), expected)

    def test_unknown_tool_is_unavailable(self):
        self.assertFalse(wg.check_wallpaper_tool("no-such-tool"))

    def test_applescript_escapes_quotes_in_path(self):
        captured = {}

        def fake_run(cmd, **kwargs):
            captured["script"] = cmd[2]
            return types.SimpleNamespace(returncode=0, stdout="")

        with mock.patch.object(wg, "run_command", side_effect=fake_run):
            self.assertTrue(wg.set_wallpaper_applescript('/tmp/quo"te/pic.jpg', None))
        self.assertIn('quo\\"te', captured["script"])

    def test_set_wallpaper_missing_file_returns_false(self):
        self.assertFalse(wg.set_wallpaper("/tmp/definitely-not-here-tranquil.jpg"))


class MainValidationTests(unittest.TestCase):
    def run_main(self, argv):
        with mock.patch.object(sys, "argv", argv), \
             mock.patch.object(wg, "generate_wallpaper", side_effect=AssertionError("generation must not run")):
            with self.assertRaises(SystemExit) as ctx:
                wg.main()
        return ctx.exception.code

    def test_zero_displays_is_rejected(self):
        self.assertEqual(self.run_main(["wallpaper_generator.py", "a lake", "--displays", "0"]), 1)

    def test_negative_displays_is_rejected(self):
        self.assertEqual(self.run_main(["wallpaper_generator.py", "a lake", "--displays", "-2"]), 1)

    def test_blank_prompt_is_rejected(self):
        self.assertEqual(self.run_main(["wallpaper_generator.py", "   "]), 1)

    def test_zero_resolution_is_rejected(self):
        self.assertEqual(self.run_main(["wallpaper_generator.py", "a lake", "--resolution", "0x1080"]), 1)

    def test_malformed_resolution_is_rejected(self):
        self.assertEqual(self.run_main(["wallpaper_generator.py", "a lake", "--resolution", "big"]), 1)


if __name__ == "__main__":
    unittest.main()
