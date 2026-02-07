# FITS Viewer - Quick Start Guide

## How to Run the Program

### Method 1: PowerShell (Recommended)

```powershell
# Basic launch
.\.venv\Scripts\python.exe main.py

# Launch with M31 file
.\.venv\Scripts\python.exe main.py "E:\Seestar\MyWorks\M 31\Stacked_932_M 31_10.0s_IRCUT_20241230-002547.fit"
```

### Method 2: Batch File (CMD)

Double-click `RUN_M31_VIEWER.bat` to launch with your M31 file automatically.

### Method 3: Command Line with Virtual Environment

```cmd
.venv\Scripts\activate.bat
python main.py
```

## What's New! ✨

### DS9-Inspired Professional Features! 🔭
- **Navigation Toolbar** - Zoom, pan, save with professional controls
- **Cursor Information** - Real-time pixel coordinates and values
- **15 Colormap Options** - Gray, hot, cool, viridis, plasma, and more
- **Colormap Inversion** - Reverse any colormap instantly
- **4 Scaling Modes** - Linear, log, sqrt, asinh
- **Auto-Scale Button** - One-click optimal contrast

### Image Display is Now Working!
- **Real image visualization** using matplotlib
- **Logarithmic scaling by default** - optimized for astronomical data
- **RGB support** - automatically detects 3-channel data
- **Auto-scaling** - uses 1st-99th percentile clipping for optimal contrast

### Window Display
- **Maximized on startup** - full screen for optimal viewing
- **High-tech futuristic design** - space observatory control panel aesthetic
- **Three-panel layout**:
  - Left: HDU Navigator + Header Metadata (350px)
  - Center: Image Display (900px, full size for maximum visibility)
  - Right: File Info + Quick Stats (320px)

## What You'll See

When you open your M31 file, you'll see:

1. **Left Panel**: 
   - **Top**: HDU Navigator showing "🌟 HDU 0: PrimaryHDU"
   - **Bottom**: Header Metadata with all FITS keywords (scrollable)

2. **Center Panel - Image Display**: 
   - Full-color RGB image of M31 Andromeda Galaxy
   - Log scaling applied for enhanced visibility
   - Maximum size for optimal viewing

3. **Right Panel - File Info**:
   - File path and size
   - HDU count and summary
   - Quick statistics (min, max, mean, std)
   - Memory usage

## Using the Viewer

### Opening a File

1. Click **File → Open FITS File...** (or press Ctrl+O)
2. Navigate to your FITS file (.fits or .fit)
3. Select and open

### Viewing Different HDUs

1. Click on any HDU in the left panel
2. The image and header update automatically
3. Statistics refresh in the right panel

### Understanding the Display

**For 2D Images**:
- Displayed with colormap (default: viridis)
- Colorbar shows intensity scale
- Axes show pixel coordinates

**For 3D RGB Data** (like your M31 file):
- Automatically detects 3-channel structure
- Applies log scaling to each channel independently
- Displays as full-color image

**For 1D Spectrum Data**:
- Shows data statistics
- Image visualization coming soon

## Your M31 File Information

**File**: `Stacked_932_M 31_10.0s_IRCUT_20241230-002547.fit`

**Contents**:
- **Shape**: 3 × 1920 × 1080 (RGB channels)
- **Type**: uint16 (16-bit unsigned integer)
- **Auto-scaling range**: ~6093 to 6389
- **Content**: M31 Andromeda Galaxy color image

The viewer automatically:
1. Detects the 3-channel RGB structure
2. Applies log scaling to each channel
3. Displays the full-color image with enhanced visibility

## Supported Features

### Current Implementation ✅
- File opening and parsing (.fits, .fit)
- HDU navigation and selection
- Header display with scrolling
- **Image visualization** (2D and 3D RGB)
- **Logarithmic scaling** (default)
- **Automatic intensity scaling**
- RGB channel detection
- Statistics display
- High-tech UI design

### Scaling Modes Available
- **Linear** - Direct pixel value mapping
- **Log** - Logarithmic scaling (default, best for faint features)
- **Sqrt** - Square root scaling
- **Asinh** - Inverse hyperbolic sine scaling

### Coming Soon ⏳
- Interactive scaling controls (sliders for vmin/vmax)
- Colormap selection for single-channel images
- Multi-dimensional slicing controls for data cubes
- Zoom and pan capabilities
- Manual scaling mode selection in UI

## Testing

### Integration Tests
```powershell
.\.venv\Scripts\python.exe test_image_integration.py
.\.venv\Scripts\python.exe test_log_scaling.py
```

### Full Test Suite
```powershell
.\.venv\Scripts\python.exe -m pytest tests/ -v
```

Expected results:
- 27+ tests should pass
- Property-based tests run 100 iterations each
- All tests should show PASSED ✅

## Troubleshooting

### Image appears too dark
- The default log scaling should help, but you can adjust by modifying the code
- Future versions will have interactive controls

### PowerShell won't run .bat files
- Use the direct Python command: `.\.venv\Scripts\python.exe main.py`
- Or run in CMD instead of PowerShell

### "Module not found" error
- Reinstall dependencies: `.\.venv\Scripts\pip.exe install -r requirements.txt`

### Application window doesn't appear
- Check console for error messages
- Run integration test: `python test_image_integration.py`

## Keyboard Shortcuts

- **Ctrl+O**: Open file
- **Ctrl+Q**: Quit application

## Technical Details

### Image Display Engine
- Uses matplotlib with Qt5Agg backend
- Percentile-based auto-scaling (1st-99th)
- Handles NaN and Inf values gracefully
- Supports multiple data types (uint8, int16, int32, int64, float32, float64)

### Performance
- Memory-mapped file access disabled (Windows compatibility)
- Efficient RGB channel processing
- Real-time canvas updates

## Next Development Steps

From the task list (`.kiro/specs/fits-viewer/tasks.md`):
- Task 5.2: Implement scaling controls panel
- Task 6: Multi-dimensional data slicing
- Task 11: Interactive scaling controls widget
- Task 16: Wire scaling controls to display

---

**Enjoy exploring your FITS files with real image visualization!** 🔭✨🌌

