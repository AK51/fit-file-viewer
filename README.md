# FITS Viewer

<img width="1274" height="735" alt="fit_main" src="https://github.com/user-attachments/assets/60ec9c83-b534-4cfd-9cb3-3c18683d1126" />

A Python-based FITS (Flexible Image Transport System) file viewer for astronomy.

## Features

- ✅ Open and parse FITS files (.fits, .fit extensions)
- ✅ Display FITS header metadata
- ✅ Navigate multiple HDUs (Header-Data Units)
- ✅ Support for various data types (8-bit to 64-bit integers and floats)
- ✅ Handle multi-dimensional data arrays (1D, 2D, 3D+)
- ✅ Modern PyQt5-based user interface with dark theme
- ✅ Image visualization with matplotlib
- ✅ Adjustable intensity scaling (linear, log, sqrt, asinh)
- ✅ 15+ colormaps with inversion support
- ✅ Real-time histogram display
- ✅ Interactive zoom and pan
- ✅ Pixel value inspection
- ✅ RGB to grayscale conversion
- ✅ Comprehensive keyboard shortcuts

## Quick Start

### 🚀 Easiest Way - Enhanced High-Tech GUI!

**Double-click `RUN_ENHANCED_VIEWER.bat`** to launch the viewer with your M31 file!

The new interface features:
- 🎨 Futuristic dark theme with cyan/blue accents
- ✨ Glowing borders and gradient backgrounds
- 📊 Three-panel layout (HDU Navigator | Display | Stats)
- 🌟 Icon-based navigation with emojis
- 📈 Real-time statistics panel
- 💫 Smooth animations and hover effects

### Alternative Methods

**Option 1: PowerShell (Current Environment)**
```powershell
.\.venv\Scripts\python.exe main.py "E:\Seestar\MyWorks\M 31\Stacked_932_M 31_10.0s_IRCUT_20241230-002547.fit"
```

**Option 2: Without a file**
```powershell
.\.venv\Scripts\python.exe main.py
```
Then use File → Open to select a FITS file.

## Current Status

### ✅ Completed Features

1. **FITS File Parsing** - Fully functional ⭐
   - Opens .fits and .fit files
   - Parses all HDUs (Primary and Extensions)
   - Extracts headers and data
   - Handles all FITS data types (uint8, int16, int32, int64, float32, float64)
   - Supports 1D, 2D, and 3D+ data arrays

2. **Enhanced High-Tech GUI** - Complete! 🚀
   - **Futuristic Design**: Dark theme with cyan/blue accents
   - **Three-Panel Layout**: HDU Navigator | Display | Stats
   - **Visual Effects**: Glowing borders, gradients, shadows
   - **Smart Icons**: Emoji-based navigation (🌟📊🖼️📦)
   - **Real-Time Stats**: Data type, shape, memory, statistics
   - **Smooth Animations**: Hover effects, status bar pulse
   - **Professional Look**: Space observatory control panel aesthetic

3. **Image Display Engine** - Complete! 🎨
   - **Matplotlib Integration**: High-quality image rendering
   - **Scaling Modes**: Linear, log, sqrt, asinh
   - **15+ Colormaps**: viridis, gray, hot, cool, rainbow, jet, plasma, inferno, magma, cividis, twilight, turbo, seismic, RdYlBu, Spectral
   - **Colormap Inversion**: Toggle to reverse any colormap
   - **Auto-scaling**: Automatic contrast optimization (1st-99th percentile)
   - **Manual Controls**: Interactive sliders for min/max values
   - **RGB Support**: Automatic RGB detection with grayscale conversion
   - **Navigation Toolbar**: Zoom, pan, home, back/forward, save

4. **Advanced Features** - Complete! 📊
   - **Real-time Histogram**: Log-scale histogram with scaling indicators
   - **Pixel Inspector**: Hover to see coordinates and values
   - **Interactive Sliders**: Real-time min/max adjustment
   - **RGB to Grayscale**: One-click conversion for colormap support
   - **Keyboard Shortcuts**: Full keyboard control (see [KEYBOARD_SHORTCUTS.md](KEYBOARD_SHORTCUTS.md))
   - **Menu System**: File, View, Scaling, Colormap, Help menus

5. **Testing** - Comprehensive test suite ✅
   - 10 property-based tests (100+ iterations each)
   - 17 unit tests for edge cases
   - All tests passing

## Keyboard Shortcuts ⌨️

Full keyboard control for efficient workflow! Press `F1` in the app or see [KEYBOARD_SHORTCUTS.md](KEYBOARD_SHORTCUTS.md) for complete reference.

**Quick Reference:**
- `Ctrl+O` - Open file
- `Ctrl+1/2/3/4` - Scaling modes (linear/log/sqrt/asinh)
- `Ctrl+A` - Auto-scale
- `Ctrl+G/H/C/V` - Colormaps (gray/hot/cool/viridis)
- `Ctrl+I` - Invert colormap
- `Ctrl++/-/0` - Zoom in/out/fit
- `F1` - Show keyboard shortcuts

### ⏳ Future Enhancements

- Multi-dimensional data cube slicing controls
- WCS (World Coordinate System) support
- FITS header editing
- Batch processing capabilities

## Testing Your FITS File

Your test file has been successfully loaded:
- **File**: `Stacked_932_M 31_10.0s_IRCUT_20241230-002547.fit`
- **HDUs**: 1 (Primary HDU)
- **Data**: 3D array (3 channels × 1920 × 1080 pixels)
- **Type**: 16-bit unsigned integers (uint16)
- **Range**: 5520 to 65058
- **Mean**: 6180.55

This appears to be a color astronomical image of M31 (Andromeda Galaxy)!

## Development

### Run Tests

```bash
# Activate virtual environment
.venv\Scripts\activate

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_fits_manager.py

# Run property-based tests
pytest tests/property/test_properties_fits_parsing.py
```

### Test Results

All tests passing:
- ✅ 10 property-based tests (Hypothesis, 100 iterations each)
- ✅ 17 unit tests for edge cases
- ✅ Total: 27 tests, ~40 seconds runtime

### Project Structure

```
fits-viewer/
├── .venv/                  # Virtual environment (Python 3.10)
├── src/                    # Source code
│   ├── __init__.py
│   ├── fits_file_manager.py    # FITS file operations
│   └── main_window.py          # PyQt5 main window
├── tests/                  # Test suite
│   ├── unit/              # Unit tests
│   │   └── test_fits_manager.py
│   └── property/          # Property-based tests
│       └── test_properties_fits_parsing.py
├── fixtures/              # Test fixtures
├── main.py               # Application entry point
├── RUN_VIEWER.bat        # Quick launch script
├── RUN_VIEWER_WITH_FILE.bat  # Launch with test file
├── test_basic_functionality.py  # Quick functionality test
├── requirements.txt      # Python dependencies
├── pyproject.toml       # Project configuration
└── README.md            # This file
```

## Requirements

- Python 3.10+ (✅ Installed: Python 3.10.6)
- astropy (✅ Installed: 6.1.7)
- PyQt5 (✅ Installed: 5.15.11)
- matplotlib (✅ Installed: 3.10.8)
- numpy (✅ Installed: 2.2.6)
- pytest (✅ Installed: 9.0.2)
- hypothesis (✅ Installed: 6.148.7)
- pytest-qt (✅ Installed: 4.5.0)

All dependencies are already installed in the virtual environment!

## Troubleshooting

### Application won't start
- Make sure you're using the `.bat` files which activate the virtual environment
- Or manually activate: `.venv\Scripts\activate.bat`

### File won't open
- Check that the file path is correct
- Ensure the file has .fits or .fit extension
- Verify the file is a valid FITS file

### Tests fail
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.10+)

## Next Steps

The FITS Viewer is now feature-complete with professional-grade functionality! 🎉

**Current capabilities:**
- ✅ Full FITS file support (all data types, multi-HDU)
- ✅ Professional image display with 4 scaling modes
- ✅ 15+ colormaps with inversion
- ✅ Real-time histogram and statistics
- ✅ Interactive zoom, pan, and pixel inspection
- ✅ RGB to grayscale conversion
- ✅ Comprehensive keyboard shortcuts
- ✅ Modern high-tech UI design

**Optional future enhancements:**
- Multi-dimensional data cube slicing UI
- WCS (World Coordinate System) overlay
- FITS header editing capabilities
- Batch processing tools
- Custom colormap creation
- Image comparison tools

## License

This project is part of the FITS Viewer specification implementation.


