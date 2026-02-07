"""
Histogram Widget

Displays histogram of FITS data for scaling analysis.
"""

import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class HistogramWidget(FigureCanvasQTAgg):
    """Widget to display data histogram."""
    
    def __init__(self, parent=None, width=3, height=2):
        """Initialize the histogram widget."""
        # Create matplotlib figure
        self.figure = Figure(figsize=(width, height), facecolor='#0a0a0a')
        self.axes = self.figure.add_subplot(111)
        
        # Set dark background
        self.axes.set_facecolor('#0a0a0a')
        
        # Initialize
        super().__init__(self.figure)
        self.setParent(parent)
        
        # Style the axes
        self.axes.tick_params(colors='#00d4ff', which='both', labelsize=7)
        for spine in self.axes.spines.values():
            spine.set_edgecolor('#00d4ff')
            spine.set_linewidth(1)
        
        # Current data
        self.current_data = None
        self.vmin_line = None
        self.vmax_line = None
    
    def update_histogram(self, data, vmin=None, vmax=None, bins=100):
        """
        Update histogram with new data - enhanced with vivid colors.
        
        Args:
            data: Numpy array with image data
            vmin: Minimum scaling value (for vertical line)
            vmax: Maximum scaling value (for vertical line)
            bins: Number of histogram bins
        """
        if data is None:
            return
        
        self.current_data = data
        
        # Clear previous plot
        self.axes.clear()
        
        # Filter out NaN and Inf values
        valid_data = data[np.isfinite(data)]
        
        if len(valid_data) == 0:
            return
        
        # Calculate histogram
        counts, bin_edges = np.histogram(valid_data, bins=bins)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        
        # Create colorful gradient bars - use a colormap for vivid colors
        # Normalize counts for color mapping
        norm_counts = counts / counts.max() if counts.max() > 0 else counts
        
        # Use a vibrant colormap - create gradient from cyan to magenta
        colors = []
        for i, nc in enumerate(norm_counts):
            # Create gradient: cyan -> blue -> magenta -> red based on height
            if nc < 0.25:
                # Cyan to blue
                r = 0.0
                g = 0.8 - nc * 2
                b = 1.0
            elif nc < 0.5:
                # Blue to purple
                r = (nc - 0.25) * 2
                g = 0.2
                b = 1.0
            elif nc < 0.75:
                # Purple to magenta
                r = 0.5 + (nc - 0.5) * 2
                g = 0.0
                b = 1.0 - (nc - 0.5) * 1.5
            else:
                # Magenta to red
                r = 1.0
                g = 0.0
                b = 0.5 - (nc - 0.75) * 2
            
            colors.append((r, g, b, 0.85))  # RGBA with high alpha
        
        # Plot histogram with gradient colors
        self.axes.bar(bin_edges[:-1], counts, width=np.diff(bin_edges),
                     color=colors, edgecolor='#ffffff', linewidth=0.3)
        
        # Add a subtle glow effect by plotting a slightly wider, more transparent version
        self.axes.bar(bin_edges[:-1], counts, width=np.diff(bin_edges) * 1.1,
                     color='#00ffff', alpha=0.15, edgecolor='none')
        
        # Add vertical lines for vmin/vmax with enhanced styling
        if vmin is not None:
            self.vmin_line = self.axes.axvline(vmin, color='#ff3366', 
                                               linestyle='--', linewidth=3, 
                                               label=f'Min: {vmin:.2f}', alpha=0.9)
            # Add glow to min line
            self.axes.axvline(vmin, color='#ff3366', linestyle='--', 
                            linewidth=6, alpha=0.3)
        
        if vmax is not None:
            self.vmax_line = self.axes.axvline(vmax, color='#00ff88', 
                                               linestyle='--', linewidth=3,
                                               label=f'Max: {vmax:.2f}', alpha=0.9)
            # Add glow to max line
            self.axes.axvline(vmax, color='#00ff88', linestyle='--', 
                            linewidth=6, alpha=0.3)
        
        # Labels and title with enhanced styling
        self.axes.set_xlabel('Pixel Value', color='#00ffff', fontsize=9, fontweight='bold')
        self.axes.set_ylabel('Count', color='#00ffff', fontsize=9, fontweight='bold')
        self.axes.set_title('Data Histogram', color='#00ffff', fontsize=10, 
                          pad=8, fontweight='bold')
        
        # Log scale for y-axis (better for astronomical data)
        self.axes.set_yscale('log')
        
        # Add grid for better readability
        self.axes.grid(True, alpha=0.2, color='#00d4ff', linestyle=':', linewidth=0.5)
        
        # Legend with enhanced styling
        if vmin is not None or vmax is not None:
            legend = self.axes.legend(loc='upper right', fontsize=8, 
                                     facecolor='#0a0a0a', edgecolor='#00ffff',
                                     framealpha=0.9)
            legend.get_frame().set_linewidth(2)
            for text in legend.get_texts():
                text.set_color('#ffffff')
                text.set_fontweight('bold')
        
        # Style the axes with vivid colors
        self.axes.tick_params(colors='#00ffff', which='both', labelsize=8, width=1.5)
        for spine in self.axes.spines.values():
            spine.set_edgecolor('#00ffff')
            spine.set_linewidth(2)
        
        # Tight layout
        self.figure.tight_layout(pad=0.5)
        
        # Redraw
        self.draw()
    
    def update_scaling_lines(self, vmin, vmax):
        """
        Update the vmin/vmax lines without recalculating histogram.
        
        Args:
            vmin: Minimum scaling value
            vmax: Maximum scaling value
        """
        if self.current_data is None:
            return
        
        # Remove old lines (including glow effects)
        # Clear all vertical lines
        for line in self.axes.lines[:]:
            line.remove()
        
        # Add new lines with glow effects
        # Min line with glow
        self.axes.axvline(vmin, color='#ff3366', linestyle='--', 
                        linewidth=6, alpha=0.3)
        self.vmin_line = self.axes.axvline(vmin, color='#ff3366', 
                                           linestyle='--', linewidth=3,
                                           label=f'Min: {vmin:.2f}', alpha=0.9)
        
        # Max line with glow
        self.axes.axvline(vmax, color='#00ff88', linestyle='--', 
                        linewidth=6, alpha=0.3)
        self.vmax_line = self.axes.axvline(vmax, color='#00ff88', 
                                           linestyle='--', linewidth=3,
                                           label=f'Max: {vmax:.2f}', alpha=0.9)
        
        # Update legend with enhanced styling
        legend = self.axes.legend(loc='upper right', fontsize=8,
                                 facecolor='#0a0a0a', edgecolor='#00ffff',
                                 framealpha=0.9)
        legend.get_frame().set_linewidth(2)
        for text in legend.get_texts():
            text.set_color('#ffffff')
            text.set_fontweight('bold')
        
        # Redraw
        self.draw()
