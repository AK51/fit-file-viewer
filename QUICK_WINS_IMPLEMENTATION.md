# Quick Wins: DS9-Inspired Features

## Overview

These are the easiest, highest-impact features we can add to match DS9 functionality.

## 1. Matplotlib Navigation Toolbar ⭐

**What it provides**:
- Zoom in/out buttons
- Pan (move) button
- Home (reset view) button
- Back/forward navigation
- Save figure button
- Configure subplots

**Implementation**: ~30 minutes
```python
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT

# In MainWindow.create_center_panel():
toolbar = NavigationToolbar2QT(self.image_canvas, self)
layout.addWidget(toolbar)
```

**User benefit**: Professional zoom/pan controls immediately

---

## 2. Colormap Selection Dropdown ⭐

**What it provides**:
- 20+ matplotlib colormaps
- DS9-style colormaps (grayscale, heat, cool)
- Colormap inversion
- Real-time preview

**Implementation**: ~2 hours
```python
# Add to right panel or as toolbar
colormap_combo = QComboBox()
colormaps = ['viridis', 'gray', 'hot', 'cool', 'rainbow', 
             'jet', 'plasma', 'inferno', 'magma']
colormap_combo.addItems(colormaps)
colormap_combo.currentTextChanged.connect(
    lambda name: self.image_engine.set_colormap(name)
)
```

**User benefit**: Visualize data in different color schemes

---

## 3. Cursor Information Display ⭐

**What it provides**:
- Pixel X, Y coordinates
- Pixel value at cursor
- Real-time updates as mouse moves

**Implementation**: ~2 hours
```python
# Connect matplotlib event
def on_mouse_move(event):
    if event.inaxes:
        x, y = int(event.xdata), int(event.ydata)
        value = data[y, x]
        self.statusBar().showMessage(
            f"X: {x}, Y: {y}, Value: {value:.2f}"
        )

self.image_canvas.mpl_connect('motion_notify_event', on_mouse_move)
```

**User benefit**: Know exact pixel coordinates and values

---

## 4. Interactive Scaling Controls ⭐⭐

**What it provides**:
- Min/max sliders
- Scaling mode buttons (linear, log, sqrt, asinh)
- Auto-scale button
- Histogram display (optional)

**Implementation**: ~4 hours

**Layout**:
```
┌─────────────────────────────┐
│ Scaling Mode: [Linear ▼]   │
├─────────────────────────────┤
│ Min: [====|=============] 0 │
│ Max: [=============|====] 1 │
├─────────────────────────────┤
│ [Auto Scale] [Reset]        │
└─────────────────────────────┘
```

**User benefit**: Fine-tune image contrast interactively

---

## 5. Colormap Inversion Toggle ⭐

**What it provides**:
- Invert colormap (black↔white)
- Useful for different viewing preferences

**Implementation**: ~30 minutes
```python
invert_checkbox = QCheckBox("Invert Colormap")
invert_checkbox.toggled.connect(self.toggle_colormap_inversion)

def toggle_colormap_inversion(self, checked):
    current = self.image_engine.colormap
    if checked:
        self.image_engine.set_colormap(current + '_r')
    else:
        self.image_engine.set_colormap(current.replace('_r', ''))
```

**User benefit**: Quick contrast reversal

---

## Implementation Order

### Phase 1: Immediate (Total: ~3 hours)
1. ✅ Matplotlib Navigation Toolbar (30 min)
2. ✅ Cursor Information Display (2 hours)
3. ✅ Colormap Inversion Toggle (30 min)

### Phase 2: Next Session (Total: ~6 hours)
4. ✅ Colormap Selection Dropdown (2 hours)
5. ✅ Interactive Scaling Controls (4 hours)

### Phase 3: Polish (Total: ~2 hours)
6. ✅ Keyboard shortcuts (1 hour)
7. ✅ Tooltips and help text (1 hour)

---

## Visual Mockup

### Current Layout
```
┌──────────┬────────────────┬──────────┐
│ HDU List │                │ File     │
│          │                │ Info     │
├──────────┤   IMAGE        │          │
│ Header   │                │ Stats    │
│ Metadata │                │          │
└──────────┴────────────────┴──────────┘
```

### Enhanced Layout (with Quick Wins)
```
┌──────────┬────────────────┬──────────┐
│ HDU List │ [Zoom Pan Save]│ Colormap │
│          ├────────────────┤ [Gray ▼] │
├──────────┤                │ [Invert] │
│ Header   │   IMAGE        ├──────────┤
│ Metadata │                │ Scaling  │
│          │                │ Mode: Log│
└──────────┤                │ Min: [==]│
           │                │ Max: [==]│
           └────────────────┴──────────┘
Status: X: 512, Y: 256, Value: 6234.5
```

---

## Comparison with DS9

| Feature | DS9 | Our Viewer (Current) | After Quick Wins |
|---------|-----|----------------------|------------------|
| Zoom/Pan | ✅ | ❌ | ✅ |
| Colormap Selection | ✅ | ❌ | ✅ |
| Scaling Controls | ✅ | ⚠️ (code only) | ✅ |
| Cursor Info | ✅ | ❌ | ✅ |
| Multiple Frames | ✅ | ❌ | ❌ (Phase 2) |
| Regions | ✅ | ❌ | ❌ (Phase 3) |
| WCS Support | ✅ | ❌ | ❌ (Phase 4) |

---

## Estimated Timeline

**Quick Wins Implementation**: 1-2 days
- Day 1 Morning: Navigation toolbar + cursor info
- Day 1 Afternoon: Colormap selection
- Day 2 Morning: Scaling controls
- Day 2 Afternoon: Testing and polish

**Result**: Professional FITS viewer with core DS9 functionality

---

## Would You Like Me to Implement These?

I can start implementing the Quick Wins right now:

1. **Matplotlib Navigation Toolbar** - Instant zoom/pan
2. **Cursor Information Display** - See pixel coordinates
3. **Colormap Selection** - Choose visualization colors
4. **Scaling Controls** - Interactive contrast adjustment

These will transform your viewer into a much more powerful tool for astronomical image analysis!

Let me know if you'd like me to proceed with implementation. 🚀
