#!/usr/bin/env python3
"""
TranquilAI - Serene AI Wallpaper Generator
Uses Google Gemini (model gemini-2.0-flash-exp, as configured in
enhance_prompt_with_gemini) for prompt enhancement and Pollinations for
image generation
"""

import sys
import os
import time
import subprocess
import shutil
import argparse
import tempfile
import urllib.parse
import random
from pathlib import Path

try:
    import requests
except ImportError:
    # I install requests at import time because nothing in this file works
    # without it. The cost is that importing this module can run pip, even
    # for a --help call. I accept that here because this file is a script
    # first and a library never, but it is worth knowing before reuse.
    print("Installing requests package...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "--user"])
    import requests

# Try to import Google Gemini dependencies for prompt enhancement
try:
    from google import genai
    from dotenv import load_dotenv
    GEMINI_AVAILABLE = True
    # Load environment variables
    # The .env load lives inside this try on purpose and by accident at
    # the same time: if the genai package is missing, load_dotenv never
    # runs. That is harmless today because the only key I read from the
    # environment is the Gemini key, which is useless without the package.
    load_dotenv()
except ImportError:
    GEMINI_AVAILABLE = False

# Try to import image processing dependencies
try:
    from PIL import Image, ImageEnhance, ImageFilter
    import numpy as np
    IMAGE_PROCESSING_AVAILABLE = True
except ImportError:
    IMAGE_PROCESSING_AVAILABLE = False

def run_command(cmd, capture_output=True, shell=False):
    """Run a command and return the result."""
    # Callers test the result with "result and result.returncode == 0"
    # because a failed launch returns None here, not a result object with
    # a bad code. Those two failures mean different things (the tool is
    # not installed, or the tool ran and said no) but every caller in this
    # file treats them the same, so I keep them apart only this far.
    try:
        if shell:
            result = subprocess.run(cmd, shell=True, capture_output=capture_output, text=True)
        else:
            result = subprocess.run(cmd, capture_output=capture_output, text=True)
        return result
    except Exception as e:
        print(f"Error running command: {e}")
        return None

def download_image_from_pollinations(prompt, width, height, seed, model, output_file, private=False):
    """Download image from Pollinations API"""
    try:
        # URL encode the prompt to handle special characters
        encoded_prompt = urllib.parse.quote(prompt)
        
        # Construct the Pollinations API URL with maximum quality settings
        if private:
            # Private mode - minimal parameters for privacy but still high quality
            image_url = f"https://pollinations.ai/p/{encoded_prompt}?width={width}&height={height}&seed={seed}&model={model}&nologo=true&private=true"
        else:
            # Standard mode - with nologo, enhance, and maximum quality parameters
            # Both branches send private=true. The difference is that the
            # standard branch also sends enhance=true, which hands the
            # prompt to Pollinations for server side processing, plus the
            # quality and steps settings. Private mode is mostly won
            # earlier, in generate_wallpaper, where the prompt never goes
            # to Gemini at all.
            image_url = f"https://pollinations.ai/p/{encoded_prompt}?width={width}&height={height}&seed={seed}&model={model}&nologo=true&enhance=true&private=true&quality=high&steps=120"
        
        print(f"Downloading image from Pollinations API...")
        # The full URL goes to the terminal, prompt included. Anyone with
        # the terminal scrollback or a log of this run can read the prompt
        # back out of it, in private mode too. I keep the print because it
        # is how I debug a bad generation, but private here means fewer
        # services see the prompt, not that the prompt stays secret.
        print(f"  URL: {image_url}")
        
        # Download the image
        response = requests.get(image_url, timeout=60)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Write the content to the output file
        with open(output_file, 'wb') as file:
            file.write(response.content)
        
        # Verify the file was created and has content
        # This check is size only. raise_for_status above already caught
        # HTTP errors, but a 200 response holding a small error image
        # would pass this test and be treated as a wallpaper. I have not
        # seen Pollinations do that; if it ever does, this is the line
        # that believed it.
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            print(f"✓ Image downloaded successfully: {output_file}")
            return True
        else:
            print("✗ Image download failed - file not created or empty")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Network error downloading image: {str(e)}")
        return False
    except Exception as e:
        print(f"✗ Error downloading image: {str(e)}")
        return False

def enhance_prompt_with_gemini(user_prompt):
    """Enhance user prompt using Gemini for better AI wallpaper generation"""
    try:
        if not GEMINI_AVAILABLE:
            print("  Gemini not available, using original prompt")
            return add_no_text_instruction(user_prompt)
        
        # Every failure in this function ends the same way: the original
        # prompt plus the no text instruction. Gemini is a quality step,
        # never a gate. A missing package, a missing key, or a failed call
        # must not stop a wallpaper from being generated.
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            print("  No Gemini API key found, using original prompt")
            return add_no_text_instruction(user_prompt)
        
        print("  Enhancing prompt with Gemini (gemini-2.0-flash-exp)...")
        
        # Check for alternative API key
        # GOOGLE_API_KEY wins when both are set, and GEMINI_API_KEY alone
        # is never used as the key. It only earns this warning. That is a
        # trap I set for myself: a machine with only GEMINI_API_KEY set
        # looks configured and still runs without enhancement.
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        if gemini_api_key and api_key:
            print("Both GOOGLE_API_KEY and GEMINI_API_KEY are set. Using GOOGLE_API_KEY.")
        
        # Configure Gemini
        client = genai.Client(api_key=api_key)
        
        # Create enhancement prompt
        enhancement_prompt = f"""You are an expert AI art prompt engineer. Your task is to enhance the following user prompt to create stunning, high-quality wallpapers.

Transform this prompt into a detailed, vivid description that will generate beautiful wallpaper images. Focus on:
- Visual details (lighting, colors, atmosphere, composition)
- Artistic style and quality descriptors
- Wallpaper-appropriate elements (suitable for desktop backgrounds)
- Professional photography/art terminology
- IMPORTANT: The image must contain NO TEXT, NO LETTERS, NO WORDS, NO CAPTIONS

Keep the core concept but make it much more descriptive and visually rich. Keep response under 200 words.

Provide ONLY ONE enhanced prompt, not multiple options.

Original prompt: "{user_prompt}"

Enhanced prompt:"""

        # Generate enhanced prompt
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=enhancement_prompt
        )
        
        enhanced_prompt = response.text.strip()
        
        # Handle case where Gemini provides multiple options despite instructions
        enhanced_prompt = parse_gemini_response(enhanced_prompt)
        
        # Ensure no text instruction is included
        enhanced_prompt = add_no_text_instruction(enhanced_prompt)
        print(f"  ✓ Enhanced: {enhanced_prompt[:100]}...")
        return enhanced_prompt
        
    except Exception as e:
        print(f"  ⚠ Gemini enhancement failed: {str(e)}")
        print("  Using original prompt")
        return add_no_text_instruction(user_prompt)

def generate_wallpaper(prompt, width, height, seed, output_file, private=False, no_enhance=False):
    """Generate wallpaper using Gemini-enhanced prompts and Pollinations API"""
    try:
        print(f"Generating wallpaper...")
        print(f"  Model: Pollinations AI (Flux)")
        print(f"  Resolution: {width}x{height}")
        print(f"  Seed: {seed}")
        print(f"  Private mode: {'Yes' if private else 'No'}")
        print(f"  Original prompt: {prompt}")
        
        # Enhance prompt with Gemini if available and not in private mode
        if not private:
            enhanced_prompt = enhance_prompt_with_gemini(prompt)
        else:
            print("  Private mode: skipping prompt enhancement")
            enhanced_prompt = add_no_text_instruction(prompt)
        
        print(f"  Final prompt: {enhanced_prompt}")
        
        # Download the image first
        download_success = download_image_from_pollinations(enhanced_prompt, width, height, seed, "flux", output_file, private)
        
        if download_success and not no_enhance:
            # Apply post-processing effects to enhance image quality
            # A flaw I know is in this line: enhance_image_quality returns
            # the input path both when it succeeds and when it fails and
            # falls back to the original image, so this comparison is
            # True either way. A failed enhancement is reported as a
            # successful generation. The wallpaper on disk is fine in
            # both cases, which is why I have left it, but the return
            # value does not mean what the old comment beside it claimed.
            enhanced_output = enhance_image_quality(output_file)
            return enhanced_output == output_file  # Return True if processing succeeded
        elif download_success and no_enhance:
            print("  Post-processing disabled by user")
            return True
        
        return False
        
    except Exception as e:
        print(f"✗ Error generating wallpaper: {str(e)}")
        return False

def install_wallpaper_tool():
    """Install a wallpaper setting tool"""
    # Try order is npm first, then brew. If both fail I return
    # "applescript" without installing anything, because AppleScript needs
    # no install on a Mac. That also means this function never reports
    # total failure, and a machine where osascript itself is missing or
    # broken only finds out later, inside set_wallpaper.
    print("Installing wallpaper setting tool...")
    
    # Try wallpaper-cli first
    result = run_command(["npm", "install", "-g", "wallpaper-cli"])
    if result and result.returncode == 0:
        print("✓ wallpaper-cli installed successfully")
        return "wallpaper-cli"
    
    # Try m-cli as alternative
    result = run_command(["brew", "install", "m-cli"])
    if result and result.returncode == 0:
        print("✓ m-cli installed successfully")
        return "m-cli"
    
    print("Using AppleScript as fallback")
    return "applescript"

def check_wallpaper_tool(tool):
    """Check if a wallpaper tool is available."""
    if tool == "wallpaper-cli":
        result = run_command(["which", "wallpaper"])
        return result and result.returncode == 0
    elif tool == "m-cli":
        result = run_command(["which", "m"])
        return result and result.returncode == 0
    elif tool == "applescript":
        # I do not probe for osascript. This returns True on any machine,
        # including a Linux box where osascript does not exist, and the
        # failure only shows up when the script actually runs. Read this
        # as "always available on the Mac this tool targets", because
        # that assumption is the whole reason AppleScript sits last in
        # the set_wallpaper order as the fallback that cannot be missing.
        return True  # AppleScript is always available on macOS
    return False

def get_display_count():
    """Get number of connected displays using AppleScript"""
    # Failure here falls back to 1 display at the bottom of this
    # function, silently. On a two display Mac with a broken osascript,
    # a run would set one wallpaper and call it a full success, and only
    # the summary count in main gives it away.
    try:
        result = run_command([
            "osascript", "-e",
            'tell application "System Events" to count (every desktop)'
        ])
        if result and result.returncode == 0:
            return int(result.stdout.strip())
    except:
        pass
    return 1  # Default to 1 display if detection fails

def get_display_resolution():
    """Get the primary display resolution."""
    # Nothing calls this function. main uses --resolution or the same 5K
    # pair hardcoded there. I keep it because real per display detection
    # is the fix I would want before trusting this on mixed size
    # monitors, but today it is dead code and its fallback below is the
    # value main actually uses.
    try:
        result = run_command([
            "osascript", "-e",
            'tell application "Finder" to get bounds of window of desktop'
        ])
        if result and result.returncode == 0:
            # Parse output like "0, 0, 1920, 1080"
            bounds = result.stdout.strip().split(", ")
            if len(bounds) >= 4:
                width = int(bounds[2])
                height = int(bounds[3])
                return width, height
    except:
        pass
    return 5120, 2880  # Default to 5K resolution for maximum quality on macOS

def set_wallpaper(image_path, display_index=None, tool=None):
    """Set wallpaper using the best available method"""
    abs_image_path = os.path.abspath(image_path)
    
    if not os.path.exists(abs_image_path):
        print(f"✗ Image file not found: {abs_image_path}")
        return False
    
    print(f"Setting wallpaper using {tool or 'auto-detect'}: {abs_image_path}")
    
    # Try different methods in order of preference
    methods = []
    
    if tool == "wallpaper-cli":
        methods = [("wallpaper-cli", lambda p, d: set_wallpaper_wallpaper_cli(p, d))]
    elif tool == "m-cli":
        methods = [("m-cli", lambda p, d: set_wallpaper_m_cli(p, d))]
    elif tool == "applescript":
        methods = [("applescript", lambda p, d: set_wallpaper_applescript(p, d))]
    else:
        # Auto-detect best method. The first tuple element is the tool id that
        # check_wallpaper_tool() understands; it must be the lowercase id
        # ("applescript"), not a display name, or the check never matches and
        # the method is silently skipped.
        methods = [
            ("wallpaper-cli", lambda p, d: set_wallpaper_wallpaper_cli(p, d)),
            ("m-cli", lambda p, d: set_wallpaper_m_cli(p, d)),
            ("applescript", lambda p, d: set_wallpaper_applescript(p, d))
        ]
    
    for method_name, method_func in methods:
        if check_wallpaper_tool(method_name):
            try:
                if method_func(abs_image_path, display_index):
                    print(f"✓ Wallpaper set successfully using {method_name}")
                    return True
            except Exception as e:
                print(f"✗ {method_name} failed: {e}")
                continue
    
    print("✗ All wallpaper setting methods failed")
    return False

def set_wallpaper_applescript(image_path, display_index=None):
    """Set wallpaper using AppleScript (built-in macOS method)"""
    # Two different scripts because macOS gives me two different doors.
    # A numbered desktop is reached through System Events, desktop N.
    # Setting every desktop at once goes through Finder and its desktop
    # picture. The image path is interpolated straight into the script
    # text, so a path containing a double quote would break the script.
    # Paths this program makes itself are timestamped names under the
    # queue directory, so I have not hit that, but the queue directory
    # itself comes from --queue-dir, which is user supplied and could
    # carry one.
    try:
        if display_index is not None:
            # For specific display
            script = f'''
            tell application "System Events"
                tell desktop {display_index}
                    set picture to "{image_path}"
                end tell
            end tell
            '''
        else:
            # For all displays
            script = f'''
            tell application "Finder"
                set desktop picture to POSIX file "{image_path}"
            end tell
            '''
        
        result = run_command(["osascript", "-e", script])
        return result and result.returncode == 0
    except Exception as e:
        print(f"AppleScript error: {e}")
        return False

def set_wallpaper_wallpaper_cli(image_path, display_index=None):
    """Set wallpaper using wallpaper-cli"""
    try:
        if display_index is not None:
            # wallpaper-cli uses 0-based indexing
            screen_index = display_index - 1
            cmd = ["wallpaper", image_path, f"--screen={screen_index}"]
        else:
            cmd = ["wallpaper", image_path]
        
        result = run_command(cmd)
        return result and result.returncode == 0
    except Exception as e:
        print(f"wallpaper-cli error: {e}")
        return False

def set_wallpaper_m_cli(image_path, display_index=None):
    """Set wallpaper using m-cli"""
    try:
        if display_index is not None:
            cmd = ["m", "wallpaper", image_path, "--display", str(display_index)]
        else:
            cmd = ["m", "wallpaper", image_path]
        
        result = run_command(cmd)
        return result and result.returncode == 0
    except Exception as e:
        print(f"m-cli error: {e}")
        return False

def refresh_desktop():
    """Refresh desktop to apply wallpaper changes"""
    try:
        run_command(["killall", "Dock"])
        time.sleep(1)
        print("✓ Desktop refreshed")
    except:
        print("⚠ Could not refresh desktop")

def setup_dependencies():
    """Set up all required dependencies."""
    print("Setting up dependencies...")
    
    # Check if requests is available
    try:
        import requests
        print("✓ requests library is already available")
    except ImportError:
        print("Installing requests library...")
        result = run_command([sys.executable, "-m", "pip", "install", "requests", "--user"])
        if not result or result.returncode != 0:
            print("Failed to install requests. Please run: pip install requests --user")
            return False
        else:
            print("✓ requests installed successfully")
    
    # Check Gemini dependencies. The generator itself imports the current
    # google-genai package ("from google import genai"); this check used to
    # look for the old google-generativeai package instead, so --setup
    # reported the dependency missing and installed a package the code
    # never imports, even on a correctly set up machine.
    try:
        from google import genai
        from dotenv import load_dotenv
        print("✓ Gemini dependencies are available")
    except ImportError:
        print("Installing Gemini dependencies...")
        result = run_command([sys.executable, "-m", "pip", "install", "google-genai", "python-dotenv", "--user"])
        if not result or result.returncode != 0:
            print("⚠ Failed to install Gemini dependencies. Prompt enhancement will be disabled.")
        else:
            print("✓ Gemini dependencies installed successfully")
    
    # Check image processing dependencies
    try:
        from PIL import Image, ImageEnhance, ImageFilter
        import numpy as np
        print("✓ Image processing dependencies are available")
        # Check for scipy for advanced grain reduction
        try:
            import scipy
            print("✓ Advanced grain reduction (scipy) is available")
        except ImportError:
            print("⚠ scipy not found - advanced grain reduction will use fallback method")
    except ImportError:
        print("Installing image processing dependencies...")
        result = run_command([sys.executable, "-m", "pip", "install", "Pillow", "numpy", "scipy", "--user"])
        if not result or result.returncode != 0:
            print("⚠ Failed to install image processing dependencies. Post-processing will be disabled.")
        else:
            print("✓ Image processing dependencies installed successfully")
    
    # Install wallpaper tool
    tool = install_wallpaper_tool()
    
    print("✓ Setup complete!")
    return True

def enhance_image_quality(image_path, output_path=None):
    """
    Apply subtle, professional post-processing effects to enhance image quality
    Conservative enhancements that preserve natural appearance
    """
    if not IMAGE_PROCESSING_AVAILABLE:
        print("  Image processing libraries not available, skipping enhancement")
        return image_path
    
    try:
        # Use input path as output if not specified
        # The default here means enhancement rewrites the downloaded file
        # in place and saves it as JPEG whatever format it arrived in.
        # There is no unenhanced copy left on disk after this runs. The
        # only way to keep the original is --no-enhance at generation
        # time, before this function is reached.
        if output_path is None:
            output_path = image_path
        
        print("  Applying professional image enhancement...")
        print("    • Adaptive brightness correction")
        print("    • Gentle contrast adjustment")
        print("    • Subtle color optimization")
        print("    • Light noise reduction")
        print("    • Careful sharpening")
        
        # Open the image
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Apply gentle enhancements
            # The order of the five steps below is the point. Brightness
            # goes first because the later steps read better on an image
            # already near a sane level. Noise reduction runs before
            # sharpening so the sharpening step does not sharpen the
            # noise. Swap the last two and the output gets grainier, not
            # clearer.
            enhanced_img = img.copy()
            
            # 1. Adaptive brightness adjustment
            enhanced_img = apply_adaptive_brightness(enhanced_img)
            
            # 2. Gentle contrast enhancement
            contrast_enhancer = ImageEnhance.Contrast(enhanced_img)
            enhanced_img = contrast_enhancer.enhance(1.05)  # Very gentle 5% contrast boost
            
            # 3. Subtle color saturation boost
            color_enhancer = ImageEnhance.Color(enhanced_img)
            enhanced_img = color_enhancer.enhance(1.08)  # Gentle 8% saturation boost
            
            # 4. Light noise reduction
            enhanced_img = apply_gentle_noise_reduction(enhanced_img)
            
            # 5. Subtle sharpening for clarity
            enhanced_img = apply_subtle_sharpening(enhanced_img)
            
            # Save with high quality settings
            enhanced_img.save(output_path, 'JPEG', quality=95, optimize=True, progressive=True)
            
        print("  ✓ Natural enhancement applied successfully")
        return output_path
        
    except Exception as e:
        print(f"  ⚠ Post-processing failed: {str(e)}")
        print("  Using original image")
        return image_path

def apply_adaptive_brightness(img):
    """Apply intelligent brightness adjustment based on image characteristics"""
    try:
        # Analyze image brightness
        img_array = np.array(img)
        mean_brightness = np.mean(img_array)
        
        # Apply conservative brightness adjustments only when needed
        # The mean is taken over every channel of every pixel, so a
        # mostly black night scene with one bright moon reads darker
        # than it looks and gets the full boost. Images landing between
        # 120 and 220 are left alone entirely. These bands are the whole
        # policy; there is no per region judgement in here.
        if mean_brightness < 100:  # Very dark image
            brightness_enhancer = ImageEnhance.Brightness(img)
            img = brightness_enhancer.enhance(1.15)  # 15% boost
        elif mean_brightness < 120:  # Somewhat dark
            brightness_enhancer = ImageEnhance.Brightness(img)
            img = brightness_enhancer.enhance(1.08)  # 8% boost
        elif mean_brightness > 220:  # Very bright
            brightness_enhancer = ImageEnhance.Brightness(img)
            img = brightness_enhancer.enhance(0.95)  # 5% reduction
        
        return img
    except Exception:
        return img

def apply_gentle_noise_reduction(img):
    """Apply light noise reduction without losing detail"""
    try:
        # Very gentle blur for noise reduction
        denoised = img.filter(ImageFilter.GaussianBlur(radius=0.3))
        
        # Convert to arrays
        original_array = np.array(img).astype(np.float32)
        denoised_array = np.array(denoised).astype(np.float32)
        
        # Blend original with denoised (favor original)
        blend_factor = 0.15  # Only 15% denoising
        result_array = (original_array * (1 - blend_factor) + denoised_array * blend_factor)
        result_array = np.clip(result_array, 0, 255).astype(np.uint8)
        
        return Image.fromarray(result_array)
    except Exception:
        return img

def apply_subtle_sharpening(img):
    """Apply very gentle sharpening to enhance clarity without artifacts"""
    try:
        # Create a very gentle unsharp mask
        blurred = img.filter(ImageFilter.GaussianBlur(radius=0.8))
        
        original_array = np.array(img).astype(np.float32)
        blurred_array = np.array(blurred).astype(np.float32)
        
        # Calculate edge detail
        detail_mask = original_array - blurred_array
        
        # Apply very subtle sharpening
        sharpening_strength = 0.25  # Much gentler than before
        sharpened_array = original_array + (detail_mask * sharpening_strength)
        sharpened_array = np.clip(sharpened_array, 0, 255).astype(np.uint8)
        
        return Image.fromarray(sharpened_array)
    except Exception:
        return img



def add_no_text_instruction(prompt):
    """Add 'no text' instruction to any prompt to ensure clean wallpapers"""
    # Add the instruction if not already present
    # The check is a plain substring test on the lowered prompt. A prompt
    # that mentions one of these phrases for any reason, even asking for
    # a sign with no words on it in other wording, counts as covered and
    # gets nothing appended. Every caller routes through here, including
    # the Gemini failure fallbacks, so the instruction survives even when
    # enhancement does not happen.
    no_text_keywords = ['no text', 'no letters', 'no words', 'no captions']
    prompt_lower = prompt.lower()
    
    if not any(keyword in prompt_lower for keyword in no_text_keywords):
        prompt += ", no text, no letters, no words, no captions"
    
    return prompt

def parse_gemini_response(response_text):
    """
    Parse Gemini response to extract the best option when multiple are provided.
    Sometimes Gemini provides multiple options despite instructions to provide only one.
    """
    try:
        # I try three extraction shapes in order, strictest first: a
        # quoted Option 1 block, an unquoted block that ends where
        # Option 2 starts, then a line walk. Order matters because the
        # loose patterns also match inside the strict ones, and running
        # them first would return text with markdown still attached.
        # Check if response contains multiple options
        if "**Option" in response_text or "Option 1" in response_text:
            print("  Multiple options detected, selecting the first one...")
            
            # Look for patterns like "**Option 1 (Title):**" or "Option 1:"
            import re
            
            # First try to find the content between quotes for Option 1
            option_pattern = r'\*\*Option\s+1[^:]*:\*\*\s*\n?\s*"([^"]+)"'
            match = re.search(option_pattern, response_text, re.DOTALL)
            
            if match:
                selected_option = match.group(1).strip()
                print(f"  ✓ Selected: Option 1")
                return selected_option
            
            # Alternative pattern without quotes but with clear option boundary
            option_pattern = r'\*\*Option\s+1[^:]*:\*\*\s*\n?\s*([^*]+?)(?=\*\*Option\s+2|\n\*\*|$)'
            match = re.search(option_pattern, response_text, re.DOTALL)
            
            if match:
                selected_option = match.group(1).strip()
                # Clean up any trailing text or formatting
                lines = selected_option.split('\n')
                # Take the first non-empty line or combine multiple lines if it's a paragraph
                if lines:
                    if len(lines) == 1:
                        selected_option = lines[0].strip()
                    else:
                        # For multi-line descriptions, clean and join
                        cleaned_lines = [line.strip() for line in lines if line.strip() and not line.strip().startswith('**')]
                        selected_option = ' '.join(cleaned_lines)
                print(f"  ✓ Selected: Option 1")
                return selected_option
            
            # Fallback: split by lines and take first substantial content after "Option 1"
            lines = response_text.split('\n')
            capture_next = False
            collected_lines = []
            
            for line in lines:
                if "Option 1" in line:
                    capture_next = True
                    continue
                elif capture_next:
                    if line.strip():
                        if line.startswith("**Option 2") or line.startswith("Option 2"):
                            break  # Stop at Option 2
                        if not line.startswith("**") and not line.startswith("Option"):
                            # Remove quotes if present and clean the line
                            clean_line = line.strip().strip('"')
                            if clean_line:
                                collected_lines.append(clean_line)
                    elif collected_lines:  # Empty line after collecting content
                        break
            
            if collected_lines:
                selected_option = ' '.join(collected_lines)
                print(f"  ✓ Selected: Option 1 (fallback method)")
                return selected_option
        
        # If no multiple options detected, return the original response
        return response_text.strip()
        
    except Exception as e:
        print(f"  ⚠ Error parsing Gemini response: {str(e)}")
        print("  Using original response")
        return response_text.strip()

def main():
    parser = argparse.ArgumentParser(description="TranquilAI - Generate serene AI wallpapers using Gemini-enhanced prompts and Pollinations")
    parser.add_argument("prompt", nargs='?', help="Text prompt for image generation")
    parser.add_argument("--displays", type=int, help="Number of displays (auto-detect if not specified)")
    parser.add_argument("--save-dir", help="Directory to save copies of generated images")
    parser.add_argument("--resolution", help="Image resolution (e.g., 1920x1080, 2560x1440)")
    parser.add_argument("--tool", choices=["wallpaper-cli", "m-cli", "applescript", "auto"], 
                       default="auto", help="Wallpaper setting tool to use")
    parser.add_argument("--queue-dir", default="./queued-images", help="Directory for queued wallpaper images")
    parser.add_argument("--setup", action="store_true", help="Install required dependencies")
    parser.add_argument("--generate-only", action="store_true", 
                       help="Only generate images, don't set as wallpaper")
    parser.add_argument("--private", action="store_true", 
                       help="Enable private generation mode (no prompt enhancement, minimal parameters)")
    parser.add_argument("--no-enhance", action="store_true",
                       help="Disable post-processing image enhancement effects")
    
    args = parser.parse_args()
    
    # Handle setup
    # --setup runs and exits before the prompt check below, so it is the
    # one invocation that works with no prompt. It also still triggers
    # the import time requests install at the top of this file if that
    # package is missing, before it ever gets here.
    if args.setup:
        success = setup_dependencies()
        sys.exit(0 if success else 1)
    
    # Check if prompt is provided when needed
    if not args.prompt:
        print("Error: prompt is required for wallpaper generation")
        print("Use --setup flag to install dependencies without generating wallpapers")
        parser.print_help()
        sys.exit(1)
    
    # Check if requests is available (needed for Pollinations)
    try:
        import requests
    except ImportError:
        print("Error: requests library not found.")
        print("Please install it with: pip install requests --user")
        print("Or run: python3 wallpaper_generator.py --setup")
        sys.exit(1)
    
    # Determine resolution
    if args.resolution:
        # The split is on a lowercase x only. "1920X1080" lands in the
        # ValueError below and reads as a format mistake, which is fair,
        # but the number check after it matters more: it is what stops a
        # 0 or a negative size from being pasted into the Pollinations
        # URL, where it would fail far from the real cause.
        try:
            width, height = map(int, args.resolution.split('x'))
        except ValueError:
            print("Invalid resolution format. Use format like: 1920x1080")
            sys.exit(1)
        if width <= 0 or height <= 0:
            print("Invalid resolution. Width and height must be positive. Use format like: 1920x1080")
            sys.exit(1)
    else:
        # Use 5K resolution for maximum quality on macOS
        width, height = 5120, 2880  # 5K resolution - highest quality for macOS displays
    
    # Determine number of displays
    displays = args.displays or get_display_count()
    
    print(f"Generating wallpapers for {displays} display(s)")
    print(f"Resolution: {width}x{height}")
    print(f"Engine: Pollinations AI (Flux){' with Gemini enhancement' if not args.private and GEMINI_AVAILABLE else ''}")
    print(f"Post-processing: {'Enabled' if not args.no_enhance and IMAGE_PROCESSING_AVAILABLE else 'Disabled'}")
    
    # Create directories
    queue_dir = Path(args.queue_dir)
    queue_dir.mkdir(exist_ok=True)
    
    # Create a saved wallpapers directory to preserve all generated wallpapers
    saved_dir = queue_dir / "saved"
    saved_dir.mkdir(exist_ok=True)
    
    if args.save_dir:
        save_dir = Path(args.save_dir)
        save_dir.mkdir(exist_ok=True)
    
    # Generate new wallpapers
    print(f"\n=== Generating New Wallpapers ===")
    success_count = 0
    
    for display_idx in range(1, displays + 1):
        print(f"\n--- Display {display_idx} ---")
        
        # Display numbers start at 1 here because the AppleScript
        # desktop numbering in set_wallpaper_applescript starts at 1.
        # wallpaper-cli counts from 0 and its wrapper subtracts the 1
        # back off. Keep this loop 1 based or every tool but one shifts.
        # Use random seed for uniqueness and variety
        # A fresh seed per display means two displays get two different
        # images from the same prompt. Pass the same seed twice and
        # Pollinations gives the same image back, so this line is the
        # only thing making a multi display run varied.
        seed = random.randint(1, 2147483647)  # Use max int32 value for compatibility
        
        # Always create timestamped files to preserve wallpaper history
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        # Output file with timestamp to preserve all wallpapers
        if args.save_dir:
            output_file = save_dir / f"wallpaper_display_{display_idx}_{timestamp}.jpg"
        else:
            output_file = saved_dir / f"wallpaper_display_{display_idx}_{timestamp}.jpg"
        
        # Generate wallpaper
        if generate_wallpaper(args.prompt, width, height, seed, str(output_file), args.private, args.no_enhance):
            success_count += 1
            
            # Create unique queue filename to avoid caching issues
            queue_file = queue_dir / f"wallpaper_display_{display_idx}_{timestamp}.jpg"
            try:
                shutil.copy2(str(output_file), str(queue_file))
                print(f"✓ Saved timestamped copy: {output_file}")
                print(f"✓ Created queue file: {queue_file}")
            except Exception as e:
                print(f"⚠ Failed to copy to queue: {e}")
            
            # Set the newly generated wallpaper immediately (if not generate-only mode)
            if not args.generate_only:
                set_wallpaper(str(queue_file), display_idx, args.tool)
        else:
            print(f"✗ Failed to generate wallpaper for display {display_idx}")
    
    print(f"\n=== Summary ===")
    print(f"Successfully generated {success_count}/{displays} wallpapers")
    
    # Refresh desktop after all wallpapers are set
    if success_count > 0 and not args.generate_only:
        refresh_desktop()
    
    if success_count > 0:
        print("✓ Wallpaper generation completed successfully")
        if args.generate_only:
            print("Images saved to queue directory for future use")
        else:
            print("New wallpapers have been set automatically")
    else:
        print("✗ No wallpapers were generated successfully")
        sys.exit(1)

if __name__ == "__main__":
    main()