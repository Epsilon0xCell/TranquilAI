# TranquilAI - Serene AI Wallpaper Generator

A Python script that generates tranquil AI wallpapers using Google Gemini (model gemini-2.0-flash-exp, as configured in the code) for prompt enhancement and Pollinations (Flux) for free wallpaper image generation, with post-processing applied to the downloaded image before it is set.

- Generates a new tranquil wallpaper on each run (run it at login for a fresh wallpaper daily)
- To me, other than music, wallpapers are the ultimate form of aesthetic art in the 21st century
- I recommend upscaling the result with Upscayl (16x, Double Upscale) as Pollinations is limited to a certain resolution.
- Do I recommend this tool? I do not recommend this tool if you are a wallpaper purist, AI generally creates low-quality, bad artistic style content, additionally unless you pay extremely high-costs, getting higher-resolution AI is difficult and it often has to be paired with an upscaler to look right, I'd recommend this tool to help you generate and view wallpapers before upscaling them and adding them to a proper wallpaper pack you are building, this should only be used as a preview tool if you want super-high-quality images. AI is generally low-quality and I recommend Wallhaven and Alphacoders Wallpaper Abyss instead.
- I do not recommend using bulk image downloaders, they generally pull every single image whether good or not. I suggest handbuilding your own collection.
- If you want a high-quality wallpaper every-day on MacOS I recommend this tool with Bing Wallpapers, ignoring the AI settings: https://www.dailywallpaperapp.com (Here is where the wallpapers are sourced from: https://www.bing.com/)
- The only AI I have seen that can create good AI wallpapers is Google Whisk after replicating features of another image and then upscaling with another tool.
- The issue with AI is that it often looks high-quality at a low size but when it is set at a wallpaper you start to notice the inherent flaws.
- I avoid video wallpapers because they tend to get boring quickly, and the limited availability makes it hard to find many worth downloading; additionally, they require third-party tools that consume system resources and may not be compatible with all operating systems. I also appreciate the aesthetics and thoughtfulness of photos, which are easier to edit and manipulate than videos, editing videos is more work than I’m willing to put in for a wallpaper. Furthermore, videos can be distracting and take focus away from productive tasks on the computer.
- However, the best Video Wallpapers I have ever seen are located at https://www.3planesoft.com, they offer free versions which makes me respect their company. These wallpapers are 3D, high-quality, and extremely detailed, Wallpaper Engine is probably the best engine, yet is isn't available on mac.

- Inspired by the macos-gen-ai-wallpaper project and created by Epsilon0xCell

## ✨ Example Output

Here are examples of the stunning wallpapers this generator creates:

![Example Wallpaper](example_wallpaper.jpg)
*Generated from prompt: "serene forest lake" - Enhanced by Gemini into a detailed, cinematic description*

![Example Wallpaper 2](wallpaper_example_2.jpg)

![Example Wallpaper 3](wallpaper_example_3.jpg)

![Example Wallpaper 4](wallpaper_example_4.jpg)

![Example Wallpaper 5](wallpaper_example_5.jpg)

![Example Wallpaper 6](wallpaper_example_6.jpg)

![Example Wallpaper 7](wallpaper_example_7.jpg)

![Example Wallpaper 8](wallpaper_example_8.jpg)

![Example Wallpaper 9](wallpaper_example_9.jpg)

These breathtaking 5K wallpapers showcase the tranquil quality you can expect for the low price of free, featuring:
- **Photorealistic detail** with morning mist and golden sunlight
- **Perfect composition** with glass-like water reflections  
- **Professional lighting** creating depth and atmosphere
- **5120x2880 resolution** for crisp display on any screen
- **Advanced post-processing** with brightness, contrast and color adjustment, noise reduction, and sharpening

## Features

- **Single Script**: All functionality consolidated into one Python file
- **Intelligent Prompt Enhancement**: Uses Google Gemini to enhance prompts for better AI-generated wallpapers
- **High-Quality Image Generation**: Uses Pollinations AI with the Flux model for stunning wallpapers
- **Advanced Post-Processing**: Automatic image enhancement with adaptive brightness correction, gentle contrast and color adjustment, light noise reduction, and subtle sharpening
- **Multiple Wallpaper Tools**: Supports wallpaper-cli, m-cli, and AppleScript for setting wallpapers
- **Multi-Display Support**: Automatically detects and generates wallpapers for multiple displays
- **5K Resolution**: Generates up to 5120x2880 resolution for maximum quality on macOS displays
- **Backup & Queue**: Saves copies and queues images with timestamps
- **Private Mode**: Option to skip prompt enhancement and use minimal parameters
- **Easy Setup**: One-command dependency installation

## Quick Start

### 1. Setup (One-time)

```bash
# Install dependencies
python3 wallpaper_generator.py --setup
```

### 2. Setup Google Gemini API (Optional but Recommended)

For enhanced prompts that generate better wallpapers:

1. **Get API Key**: Visit [Google AI Studio](https://aistudio.google.com/apikey) to get your free API key
2. **Create .env file**:
   ```bash
   echo "GOOGLE_API_KEY=your_actual_api_key_here" > .env
   ```

### 3. Generate and Set Wallpapers

**Basic Usage (with Gemini enhancement)**:
```bash
python3 wallpaper_generator.py "a serene mountain landscape at sunset"
```

**Private Mode (no prompt enhancement)**:
```bash
python3 wallpaper_generator.py "a serene mountain landscape at sunset" --private
```

### 4. Advanced Usage

#### Custom Resolution
```bash
python3 wallpaper_generator.py "cyberpunk city neon lights" --resolution 2560x1440
```

#### Save Copies to Custom Directory
```bash
python3 wallpaper_generator.py "abstract art colorful" --save-dir ~/Pictures/AI-Wallpapers
```

#### Generate Only (Don't Set as Wallpaper)
```bash
python3 wallpaper_generator.py "ocean waves" --generate-only
```

#### Specific Wallpaper Tool
```bash
python3 wallpaper_generator.py "forest path" --tool applescript
```

#### Multiple Displays
```bash
python3 wallpaper_generator.py "space nebula" --displays 3
```

## How It Works

1. **Prompt Enhancement**: If a Google API key is available and not in private mode, Gemini enhances your prompt with detailed visual descriptions
2. **Display Detection**: Automatically detects the number of connected displays
3. **Image Generation**: Uses Pollinations AI with enhanced prompts to generate high-quality images (default 5K resolution)
4. **Queue System**: Saves images to a queue directory with unique timestamped filenames
5. **Wallpaper Setting**: Uses the best available tool to set wallpapers per display
6. **Desktop Refresh**: Refreshes the desktop to apply changes

## Wallpaper Setting Methods

The script tries multiple methods to set wallpapers (in order of preference):

1. **wallpaper-cli** - Cross-platform Node.js tool
2. **m-cli** - macOS-specific Homebrew tool  
3. **AppleScript** - Built-in macOS scripting (fallback)

## Command Line Options

```
positional arguments:
  prompt                Text prompt for image generation

options:
  -h, --help            show this help message and exit
  --displays DISPLAYS   Number of displays (auto-detect if not specified)
  --save-dir SAVE_DIR   Directory to save copies of generated images
  --resolution RESOLUTION
                        Image resolution (e.g., 1920x1080, 2560x1440, 5120x2880)
  --tool {wallpaper-cli,m-cli,applescript,auto}
                        Wallpaper setting tool to use
  --queue-dir QUEUE_DIR
                        Directory for queued wallpaper images
  --private             Skip prompt enhancement and use minimal parameters
  --no-enhance          Disable post-processing image enhancement effects
  --setup               Install required dependencies
  --generate-only       Only generate images, don't set as wallpaper
```

## Requirements

- macOS (tested on macOS 10.15+)
- Python 3.9+ (required by the google-genai client)
- Internet connection for image generation

## Dependencies

**Core Dependencies (Auto-installed):**
- `requests` - For API calls to Pollinations
- `wallpaper-cli` or `m-cli` - Wallpaper setting tools

**Gemini Enhancement Dependencies (Auto-installed):**
- `google-genai` - Google Gemini client (the package the script imports)
- `python-dotenv` - Environment variable management
- Valid Google API key from [Google AI Studio](https://aistudio.google.com/apikey) (optional)

## Examples

### Nature Scene (with Gemini Enhancement)
```bash
python3 wallpaper_generator.py "peaceful forest with morning mist and sunbeams"
```

### Abstract Art (Private Mode)
```bash
python3 wallpaper_generator.py "geometric abstract art with vibrant colors" --private
```

### Cityscape (5K Resolution)
```bash
python3 wallpaper_generator.py "futuristic city skyline at night with neon lights" --resolution 5120x2880
```

### Space Theme (Save Copy)
```bash
python3 wallpaper_generator.py "deep space nebula with stars and galaxies" --save-dir ~/Pictures/AI-Wallpapers
```

## Prompt Enhancement

When a Google API key is available and not in private mode, the script uses Gemini to enhance your prompts:

**Original**: `"mountain landscape"`
**Enhanced**: `"Breathtaking mountain landscape with dramatic peaks piercing through morning clouds, golden hour lighting casting warm glows across snow-capped summits, pristine alpine meadows with wildflowers in the foreground, crystal clear mountain lake reflecting the majestic scenery, professional landscape photography, ultra-high resolution, cinematic composition"`

This results in significantly more detailed and visually stunning wallpapers.

## Advanced Post-Processing

The wallpaper generator automatically applies professional-grade image enhancement effects to improve visual quality:

### Automatic Enhancement Features
- **Adaptive Brightness**: Brightness is raised for dark images and lowered for very bright ones, based on the mean pixel value
- **Contrast Enhancement**: A gentle 5 percent contrast boost
- **Color Optimization**: A gentle 8 percent saturation boost
- **Noise Reduction**: A light blend with a Gaussian-blurred copy (15 percent) to reduce grain while preserving detail
- **Sharpening**: A subtle unsharp-mask style pass for clarity

### Post-Processing Control
- **Enabled by Default**: All generated wallpapers receive automatic enhancement
- **Disable Option**: Use `--no-enhance` flag to skip post-processing for faster generation
- **Quality Preservation**: All effects are carefully calibrated to avoid artifacts or over-processing

**Example Enhancement Process:**
```
Original Image → Adaptive Brightness → Contrast → Color → Noise Reduction → Sharpening → Final Wallpaper
```

## Quality & Examples

### What Makes These Wallpapers Special

The combination of **Gemini** prompt enhancement + **Pollinations AI** generation + **Advanced Post-Processing** creates serene wallpapers with:

- Default 5K resolution (5120x2880) for Retina displays
- Gemini turns a short prompt into a longer description before it is sent to Pollinations
- Post-processing runs brightness, contrast, color, noise reduction, and sharpening in that order

### Prompt Enhancement Examples

**Your Input:** `"mountain sunset"`

**Gemini Enhanced:** `"A breathtaking panoramic mountain vista during golden hour, with dramatic peaks silhouetted against a blazing orange and pink sunset sky. Wispy clouds catch the warm light, creating depth and atmosphere. Professional landscape photography, ultra-high resolution, 8K quality."`

That example is the shape of what the enhancement prompt asks for. What comes back varies by run, and the fallback when Gemini is unavailable or errors is your original prompt with the no text instruction added.

### Supported Styles
- **Landscapes**: Mountains, forests, lakes, deserts
- **Cityscapes**: Modern skylines, neon-lit streets, architectural subjects
- **Abstract Art**: Geometric patterns, fluid dynamics, color studies
- **Space**: Nebulae, galaxies, cosmic phenomena
- **Nature**: Ocean waves, tropical scenes, seasonal imagery
- **Tranquil Scenes**: Peaceful, meditative, and calming imagery

## Tests

25 tests, run from the repo root:

```bash
python3 -m unittest
```

- test_parsing.py (3 tests) imports parse_gemini_response from wallpaper_generator.py and asserts on it, including the two option sample that made me write the parser. It used to hold a copy of the function and print what the copy did; a green run proved nothing about the shipped code, so it tests the real one now.
- test_wallpaper_generator.py (22 tests) covers the no text instruction, Gemini key selection (GOOGLE_API_KEY first, GEMINI_API_KEY accepted on its own, no key falls back to the original prompt), the Pollinations download with requests stubbed (real image bytes accepted, an error page rejected and deleted, a network error returns False), generation in private mode, post-processing returning a path on success and None on a corrupt file, the AppleScript availability check and path escaping, and the CLI refusing a blank prompt, a zero or negative display count, and bad resolutions before any generation runs.
- No test touches the network or a live API. The Gemini client is stubbed, because the google-genai package is not installed in every environment.
- Wallpaper setting itself is macOS-only (osascript, wallpaper-cli, m-cli) and is covered here through stubbed commands, not on a real Mac desktop.

## Troubleshooting

### Missing Dependencies
If you get import errors:
```bash
python3 wallpaper_generator.py --setup
```

### Gemini API Key Issues
If prompt enhancement isn't working:
1. Make sure you have a `.env` file in the script directory
2. Verify your API key is correctly set: `GOOGLE_API_KEY=your_actual_key`
3. Get your API key from: [Google AI Studio](https://aistudio.google.com/apikey)
4. Test without enhancement: `python3 wallpaper_generator.py "test" --private`

### Permission Issues
If you get permission errors:
```bash
chmod +x wallpaper_generator.py
```

### Wallpaper Not Setting
Try using AppleScript method specifically:
```bash
python3 wallpaper_generator.py "your prompt" --tool applescript
```

### Network Issues
The script requires internet access for Pollinations API. Check your connection.

### Multiple Displays
The script automatically detects displays. If detection fails, specify manually:
```bash
python3 wallpaper_generator.py "your prompt" --displays 2
```

## Privacy

- **Standard Mode**: Sends enhanced prompts to Pollinations with optimization parameters
- **Private Mode**: Uses `--private` flag to skip Gemini enhancement and use minimal parameters with Pollinations
- **What leaves your machine**: In standard mode your prompt is sent to Gemini (when a key is configured) and to Pollinations. Private mode skips Gemini and sends Pollinations only the minimal parameter set (no enhance, quality, or steps parameters)

## Migration from Previous Versions

This version removes Google Imagen-3 support and focuses on the proven Gemini + Pollinations workflow for better reliability and quality.

### Quick Migration
1. Remove old Imagen-3 related files and directories
2. Update your API key setup to use `.env` file in the main directory
3. Run setup: `python3 wallpaper_generator.py --setup`
4. Test: `python3 wallpaper_generator.py "test prompt" --generate-only`
