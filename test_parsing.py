#!/usr/bin/env python3
"""
Tests for the Gemini response parser in wallpaper_generator.py.

This file used to hold a copy of parse_gemini_response and print what
the copy did with one sample. A green run proved the copy worked, not
the shipped function. It now imports the real function and asserts on
it. Run with: python3 -m unittest test_parsing -v
"""

import unittest

from wallpaper_generator import parse_gemini_response

# The sample response shape that made me write the parser: two options
# despite instructions to provide only one.
SAMPLE_RESPONSE = '''**Option 1 (Epic Fantasy):**

"A colossal, ethereal giant, sculpted from ancient granite and verdant moss, stands silhouetted against a dramatic, swirling twilight sky. Wisps of luminous fog curl around his colossal legs, obscuring the lower landscape. Emphasize a sense of overwhelming scale and ancient power. Lighting is key: rim light from the setting sun creates a vibrant halo around his form, highlighting the intricate textures of his earthen skin. Panoramic composition, ideal for widescreen desktop wallpaper. Fantasy art, digital painting, photorealistic detail. NO TEXT."

**Option 2 (Sci-Fi/Cyberpunk):**

"A monolithic cyborg, a bio-engineered giant, looms above a dystopian cityscape. Neon lights reflect off polished chrome and rain-slicked streets, creating a vibrant, cyberpunk aesthetic."'''


class ParseGeminiResponseTests(unittest.TestCase):
    def test_quoted_option_one_is_selected(self):
        result = parse_gemini_response(SAMPLE_RESPONSE)
        self.assertTrue(result.startswith("A colossal, ethereal giant"))
        self.assertNotIn("Option 2", result)
        self.assertNotIn("monolithic cyborg", result)
        self.assertEqual(len(result), 551)

    def test_single_response_passes_through_stripped(self):
        self.assertEqual(
            parse_gemini_response("  a quiet lake at dawn  "),
            "a quiet lake at dawn",
        )

    def test_unquoted_option_one_block_is_selected(self):
        response = "**Option 1 (Calm):**\nA still pond under pine trees, soft morning light.\n\n**Option 2 (Wild):**\nA storm over the ocean."
        result = parse_gemini_response(response)
        self.assertIn("still pond", result)
        self.assertNotIn("storm", result)


if __name__ == "__main__":
    unittest.main()
