"""
Image Display Engine

Handles rendering FITS data arrays as images with scaling using matplotlib.
"""

import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class ImageDisplayEngine:
    """Renders FITS data arrays as images with scaling."""
    
    def __init__(self):
        """Initialize the Image Display Engine."""
        # Create matplotlib figure with larger size
        self.figure = Figure(figsize=(12, 10), facecolor='#0a0a0a')
        self.axes = self.figure.add_subplot(111)
        
        # Set dark background
        self.axes.set_facecolor('#0a0a0a')
        
        # Current data and display parameters
        self.current_data = None
        self.vmin = None
        self.vmax = None
        self.scaling_mode = 'linear'
        self.colormap = 'viridis'
        
        # Image object
        self.image = None
        
        # Style the axes
        self.axes.tick_params(colors='#00d4ff', which='both')
        for spine in self.axes.spines.values():
            spine.set_edgecolor('#00d4ff')
            spine.set_linewidth(1)
    
    def set_data(self, data: np.ndarray) -> None:
        """
        Set new data array and calculate default scaling.
        
        Args:
            data: Numpy array with image data
        """
        if data is None:
            return
        
        self.current_data = data
        
        # Calculate automatic scaling
        self.vmin, self.vmax = self.auto_scale()
        
        # Update display
        self.update_display()
    
    def update_display(self) -> None:
        """Render current data with current scaling parameters."""
        if self.current_data is None:
            return
        
        # Clear previous image
        self.axes.clear()
        
        # Remove any existing colorbar
        if hasattr(self.figure, 'colorbar_ax') and self.figure.colorbar_ax is not None:
            self.figure.delaxes(self.figure.colorbar_ax)
            self.figure.colorbar_ax = None
        
        # Prepare data for display
        display_data = self._prepare_data_for_display()
        
        if display_data is None:
            return
        
        # Apply scaling transformation
        scaled_data = self._apply_scaling(display_data)
        
        # Check if RGB data
        is_rgb = scaled_data.ndim == 3 and scaled_data.shape[2] == 3
        
        # Display the image
        if is_rgb:
            # RGB image - no colormap needed
            self.image = self.axes.imshow(
                scaled_data,
                origin='lower',
                interpolation='nearest'
            )
        else:
            # Single channel - use colormap
            self.image = self.axes.imshow(
                scaled_data,
                cmap=self.colormap,
                origin='lower',
                interpolation='nearest',
                vmin=0,
                vmax=1
            )
        
        # Don't add colorbar - keep it clean
        # Users can see the colormap in the dropdown selection
        
        # Set title with data info
        title = f"Shape: {self.current_data.shape} | Type: {self.current_data.dtype}"
        self.axes.set_title(title, color='#00d4ff', fontsize=9, pad=5)
        
        # Remove axis labels to maximize image space
        self.axes.set_xlabel('')
        self.axes.set_ylabel('')
        
        # Style the axes
        self.axes.tick_params(colors='#00d4ff', which='both', labelsize=7)
        for spine in self.axes.spines.values():
            spine.set_edgecolor('#00d4ff')
            spine.set_linewidth(1)
        
        # Tight layout with minimal padding
        self.figure.tight_layout(pad=0.5)
        
        # Redraw
        self.figure.canvas.draw_idle()
    
    def _prepare_data_for_display(self) -> np.ndarray:
        """
        Prepare data for display based on dimensionality.
        
        Returns:
            2D array ready for display, or None if not displayable
        """
        if self.current_data is None:
            return None
        
        data = self.current_data
        
        # Handle different dimensionalities
        if data.ndim == 1:
            # 1D data - can't display as image
            return None
        elif data.ndim == 2:
            # 2D data - display directly
            return data
        elif data.ndim == 3:
            # 3D data - take middle slice or create RGB if 3 channels
            if data.shape[0] == 3:
                # Assume RGB channels - return raw data for scaling
                # Transpose to (height, width, channels)
                rgb_data = np.transpose(data, (1, 2, 0))
                return rgb_data
            else:
                # Take middle slice
                middle_idx = data.shape[0] // 2
                return data[middle_idx, :, :]
        else:
            # Higher dimensions - take middle slice of first two dimensions
            indices = [data.shape[i] // 2 for i in range(data.ndim - 2)]
            return data[tuple(indices)]
    
    def _apply_scaling(self, data: np.ndarray) -> np.ndarray:
        """
        Apply scaling transformation to data.
        
        Args:
            data: Input data array
            
        Returns:
            Scaled data array
        """
        if data is None:
            return None
        
        # Handle RGB data (3 channels) - apply scaling to each channel
        if data.ndim == 3 and data.shape[2] == 3:
            rgb_scaled = np.zeros_like(data, dtype=np.float32)
            for i in range(3):
                channel = data[:, :, i].astype(np.float32)
                # Apply scaling to this channel
                rgb_scaled[:, :, i] = self._apply_scaling_to_channel(channel)
            return rgb_scaled
        
        # Single channel data
        return self._apply_scaling_to_channel(data)
    
    def _apply_scaling_to_channel(self, data: np.ndarray) -> np.ndarray:
        """
        Apply scaling transformation to a single channel.
        
        Args:
            data: Input data array (single channel)
            
        Returns:
            Scaled data array normalized to 0-1
        """
        # Clip data to vmin/vmax range
        clipped = np.clip(data, self.vmin, self.vmax)
        
        if self.scaling_mode == 'linear':
            # Linear scaling - normalize to 0-1
            if self.vmax > self.vmin:
                return (clipped - self.vmin) / (self.vmax - self.vmin)
            return clipped
        
        elif self.scaling_mode == 'log':
            # Logarithmic scaling
            # Shift data to be positive
            shifted = clipped - self.vmin + 1
            scaled = np.log10(shifted)
            # Normalize to 0-1
            scaled_min, scaled_max = scaled.min(), scaled.max()
            if scaled_max > scaled_min:
                return (scaled - scaled_min) / (scaled_max - scaled_min)
            return scaled
        
        elif self.scaling_mode == 'sqrt':
            # Square root scaling
            shifted = clipped - self.vmin
            scaled = np.sqrt(np.abs(shifted))
            # Normalize to 0-1
            scaled_min, scaled_max = scaled.min(), scaled.max()
            if scaled_max > scaled_min:
                return (scaled - scaled_min) / (scaled_max - scaled_min)
            return scaled
        
        elif self.scaling_mode == 'asinh':
            # Inverse hyperbolic sine scaling
            scaled = np.arcsinh(clipped)
            # Normalize to 0-1
            scaled_min, scaled_max = scaled.min(), scaled.max()
            if scaled_max > scaled_min:
                return (scaled - scaled_min) / (scaled_max - scaled_min)
            return scaled
        
        else:
            # Default to linear
            if self.vmax > self.vmin:
                return (clipped - self.vmin) / (self.vmax - self.vmin)
            return clipped
    
    def auto_scale(self, percentile_low=0.5, percentile_high=99.5) -> tuple:
        """
        Calculate automatic scaling based on data statistics.
        
        Uses percentiles to handle outliers and provide optimal contrast.
        Default uses 0.5%-99.5% which clips extreme outliers while
        preserving detail in astronomical images.
        
        Args:
            percentile_low: Lower percentile (default 0.5)
            percentile_high: Upper percentile (default 99.5)
        
        Returns:
            Tuple of (vmin, vmax)
        """
        if self.current_data is None:
            return (0, 1)
        
        # Filter out NaN and Inf values
        valid_data = self.current_data[np.isfinite(self.current_data)]
        
        if len(valid_data) == 0:
            return (0, 1)
        
        # Use percentiles to avoid outliers
        vmin = np.percentile(valid_data, percentile_low)
        vmax = np.percentile(valid_data, percentile_high)
        
        # Ensure vmin < vmax
        if vmin >= vmax:
            vmin = valid_data.min()
            vmax = valid_data.max()
            
            if vmin >= vmax:
                vmax = vmin + 1
        
        return (float(vmin), float(vmax))
    
    def set_scaling_limits(self, vmin: float, vmax: float) -> None:
        """
        Set manual scaling limits.
        
        Args:
            vmin: Minimum display value
            vmax: Maximum display value
        """
        if vmin < vmax:
            self.vmin = vmin
            self.vmax = vmax
            self.update_display()
    
    def set_scaling_mode(self, mode: str) -> None:
        """
        Set scaling mode.
        
        Args:
            mode: Scaling mode ('linear', 'log', 'sqrt', 'asinh')
        """
        valid_modes = ['linear', 'log', 'sqrt', 'asinh']
        if mode in valid_modes:
            self.scaling_mode = mode
            self.update_display()
    
    def set_colormap(self, name: str) -> None:
        """
        Set colormap.
        
        Args:
            name: Matplotlib colormap name
        """
        self.colormap = name
        self.update_display()
    
    def handle_multidimensional(self, data: np.ndarray, slice_indices: tuple) -> np.ndarray:
        """
        Extract 2D slice from multi-dimensional data.
        
        Args:
            data: Multi-dimensional array
            slice_indices: Tuple of indices for slicing
            
        Returns:
            2D slice of the data
        """
        if data.ndim <= 2:
            return data
        
        # Build slice object
        slices = []
        for i, idx in enumerate(slice_indices):
            if i < data.ndim - 2:
                slices.append(idx)
            else:
                slices.append(slice(None))
        
        return data[tuple(slices)]


# Import pyplot for colorbar
import matplotlib.pyplot as plt
