"""
Main Window for FITS Viewer

PyQt5-based main window with file menu, HDU list, header display, and image display.
High-tech futuristic design with enhanced visuals.
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTextEdit, QListWidget, QFileDialog, QMessageBox, QLabel,
    QAction, QListWidgetItem, QFrame, QGraphicsDropShadowEffect,
    QComboBox, QCheckBox, QPushButton, QSlider, QDoubleSpinBox, QGroupBox,
    QDialog, QSpinBox
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette, QLinearGradient, QBrush, QKeySequence
import sys

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT

from src.fits_file_manager import FITSFileManager
from src.image_display_engine import ImageDisplayEngine
from src.histogram_widget import HistogramWidget


class FullScreenImageDialog(QDialog):
    """Fullscreen dialog for viewing FITS images."""
    
    def __init__(self, image_engine, parent_canvas, parent=None):
        """
        Initialize fullscreen dialog.
        
        Args:
            image_engine: ImageDisplayEngine instance with the current image
            parent_canvas: Parent window's canvas to restore after closing
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.image_engine = image_engine
        self.parent_canvas = parent_canvas
        
        # Set up fullscreen dialog
        self.setWindowTitle("Full Screen View - Press ESC to exit")
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.showFullScreen()
        
        # Set dark background
        self.setStyleSheet("""
            QDialog {
                background: #000000;
            }
        """)
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create a new canvas for fullscreen display - TRUE FULLSCREEN
        self.fullscreen_canvas = FigureCanvasQTAgg(self.image_engine.figure)
        self.fullscreen_canvas.setStyleSheet("background: #000000;")
        layout.addWidget(self.fullscreen_canvas)
        
        # Redraw the image
        self.image_engine.figure.canvas.draw()
    
    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key_Escape:
            # Exit fullscreen and restore main window view
            self.close()
        else:
            super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """Handle dialog close - restore figure to main window canvas."""
        # Remove fullscreen canvas from layout
        self.layout().removeWidget(self.fullscreen_canvas)
        self.fullscreen_canvas.setParent(None)
        
        # Restore figure to parent canvas
        if self.parent_canvas:
            # Force the figure to redraw on the parent canvas
            self.image_engine.figure.canvas = self.parent_canvas
            self.parent_canvas.figure = self.image_engine.figure
            self.parent_canvas.draw()
        
        event.accept()


class HeaderMetadataDialog(QDialog):
    """Dialog for displaying FITS header metadata."""
    
    def __init__(self, header_text, hdu_index, parent=None):
        """
        Initialize header metadata dialog.
        
        Args:
            header_text: Header text to display (raw FITS format)
            hdu_index: HDU index number
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.setWindowTitle(f"📋 Header Metadata - HDU {hdu_index}")
        self.setMinimumSize(700, 600)
        
        # Set dark background
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a1a2e, stop:1 #0f3460);
            }
        """)
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title label
        title = QLabel(f"📋 HEADER METADATA - HDU {hdu_index}")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: #00d4ff;
            padding: 10px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #1a1a2e, stop:1 #16213e);
            border-radius: 5px;
            margin-bottom: 10px;
        """)
        layout.addWidget(title)
        
        # Format the header text nicely
        formatted_text = self.format_header_text(header_text)
        
        # Header text display
        self.header_display = QTextEdit()
        self.header_display.setReadOnly(True)
        self.header_display.setFont(QFont("Consolas", 14))
        self.header_display.setLineWrapMode(QTextEdit.NoWrap)
        self.header_display.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.header_display.setPlainText(formatted_text)
        self.header_display.setStyleSheet("""
            QTextEdit {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0a0a0a, stop:1 #1a1a2e);
                border: 2px solid #00d4ff;
                border-radius: 6px;
                padding: 15px;
                color: #00ff88;
                selection-background-color: #0080ff;
                font-family: 'Consolas', 'Courier New', monospace;
                line-height: 1.5;
            }
        """)
        layout.addWidget(self.header_display)
        
        # Close button
        close_btn = QPushButton("✖ Close")
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00d4ff, stop:1 #0080ff);
                color: #000000;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background: #00ffff;
            }
            QPushButton:pressed {
                background: #0080ff;
            }
        """)
        layout.addWidget(close_btn)
    
    def format_header_text(self, header_text):
        """
        Format FITS header text for better readability.
        
        Args:
            header_text: Raw FITS header text from astropy (80-char cards concatenated)
            
        Returns:
            Formatted header text with each key-value pair on separate lines
        """
        # FITS headers are 80 characters per card, split them
        lines = []
        for i in range(0, len(header_text), 80):
            card = header_text[i:i+80].rstrip()
            if card.strip():  # Skip empty cards
                lines.append(card)
        
        return '\n'.join(lines)
    
    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)


class FileInfoDialog(QDialog):
    """Dialog for displaying FITS file information."""
    
    def __init__(self, file_info_text, parent=None):
        """
        Initialize file info dialog.
        
        Args:
            file_info_text: File information text to display
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.setWindowTitle("ℹ️ File Information")
        self.setMinimumSize(700, 500)
        
        # Set dark background
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a1a2e, stop:1 #0f3460);
            }
        """)
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title label
        title = QLabel("ℹ️ FILE INFORMATION")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: #ffd93d;
            padding: 10px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #1a1a2e, stop:1 #3d2c00);
            border-radius: 5px;
            margin-bottom: 10px;
        """)
        layout.addWidget(title)
        
        # File info text display
        self.info_display = QTextEdit()
        self.info_display.setReadOnly(True)
        self.info_display.setFont(QFont("Segoe UI", 14))
        self.info_display.setPlainText(file_info_text)
        self.info_display.setStyleSheet("""
            QTextEdit {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0a0a0a, stop:1 #1a1a2e);
                border: 2px solid #ffd93d;
                border-radius: 6px;
                padding: 15px;
                color: #ffd93d;
                selection-background-color: #0080ff;
                font-family: 'Segoe UI', Arial;
                line-height: 1.5;
            }
        """)
        layout.addWidget(self.info_display)
        
        # Close button
        close_btn = QPushButton("✖ Close")
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ffd93d, stop:1 #ffaa00);
                color: #000000;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background: #ffff00;
            }
            QPushButton:pressed {
                background: #ffaa00;
            }
        """)
        layout.addWidget(close_btn)
    
    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)


class QuickStatsDialog(QDialog):
    """Dialog for displaying quick statistics."""
    
    def __init__(self, stats_text, parent=None):
        """
        Initialize quick stats dialog.
        
        Args:
            stats_text: Statistics text to display
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.setWindowTitle("📈 Quick Statistics")
        self.setMinimumSize(600, 500)
        
        # Set dark background
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a1a2e, stop:1 #0f3460);
            }
        """)
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title label
        title = QLabel("📈 QUICK STATISTICS")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: #a8dadc;
            padding: 10px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #1a1a2e, stop:1 #16213e);
            border-radius: 5px;
            margin-bottom: 10px;
        """)
        layout.addWidget(title)
        
        # Stats text display
        self.stats_display = QTextEdit()
        self.stats_display.setReadOnly(True)
        self.stats_display.setFont(QFont("Segoe UI", 14))
        self.stats_display.setPlainText(stats_text)
        self.stats_display.setStyleSheet("""
            QTextEdit {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0a0a0a, stop:1 #1a1a2e);
                border: 2px solid #a8dadc;
                border-radius: 6px;
                padding: 15px;
                color: #a8dadc;
                selection-background-color: #0080ff;
                font-family: 'Segoe UI', Arial;
                line-height: 1.5;
            }
        """)
        layout.addWidget(self.stats_display)
        
        # Close button
        close_btn = QPushButton("✖ Close")
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #a8dadc, stop:1 #6ba8b8);
                color: #000000;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background: #c8f0f0;
            }
            QPushButton:pressed {
                background: #6ba8b8;
            }
        """)
        layout.addWidget(close_btn)
    
    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)


class CustomRotationDialog(QDialog):
    """Dialog for custom rotation angle input."""
    
    def __init__(self, parent=None):
        """
        Initialize custom rotation dialog.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.setWindowTitle("🔄 Custom Rotation")
        self.setMinimumSize(400, 200)
        
        # Set dark background
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a1a2e, stop:1 #0f3460);
            }
        """)
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title label
        title = QLabel("🔄 CUSTOM ROTATION ANGLE")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #00d4ff;
            padding: 10px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #1a1a2e, stop:1 #16213e);
            border-radius: 5px;
            margin-bottom: 10px;
        """)
        layout.addWidget(title)
        
        # Instruction label
        instruction = QLabel("Enter rotation angle in degrees:")
        instruction.setStyleSheet("""
            font-size: 14px;
            color: #e0e0e0;
            padding: 5px;
        """)
        layout.addWidget(instruction)
        
        # Angle input
        input_layout = QHBoxLayout()
        
        self.angle_spinbox = QSpinBox()
        self.angle_spinbox.setMinimum(-360)
        self.angle_spinbox.setMaximum(360)
        self.angle_spinbox.setValue(0)
        self.angle_spinbox.setSuffix("°")
        self.angle_spinbox.setStyleSheet("""
            QSpinBox {
                background: #1a1a2e;
                color: #00d4ff;
                border: 2px solid #00d4ff;
                border-radius: 5px;
                padding: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background: #00d4ff;
                border-radius: 3px;
                width: 20px;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background: #00ffff;
            }
        """)
        input_layout.addWidget(self.angle_spinbox)
        
        layout.addLayout(input_layout)
        
        # Info label
        info = QLabel("💡 Positive = clockwise, Negative = counter-clockwise\n(Replaces any previous rotation)")
        info.setStyleSheet("""
            font-size: 12px;
            color: #ffd93d;
            padding: 5px;
            background: #1a1a2e;
            border: 1px solid #ffd93d;
            border-radius: 3px;
        """)
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        ok_btn = QPushButton("✓ Rotate")
        ok_btn.clicked.connect(self.accept)
        ok_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00d4ff, stop:1 #0080ff);
                color: #000000;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background: #00ffff;
            }
            QPushButton:pressed {
                background: #0080ff;
            }
        """)
        button_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("✖ Cancel")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #666666, stop:1 #444444);
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background: #888888;
            }
            QPushButton:pressed {
                background: #333333;
            }
        """)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def get_angle(self):
        """Get the entered rotation angle."""
        return self.angle_spinbox.value()
    
    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key_Escape:
            self.reject()
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.accept()
        else:
            super().keyPressEvent(event)


class MainWindow(QMainWindow):
    """Main application window for FITS Viewer."""
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        
        # Initialize FITS file manager
        self.fits_manager = FITSFileManager()
        self.current_hdu_index = 0
        
        # Store original RGB data before any conversions
        self.original_rgb_data = None
        
        # Store original data before any transformations (rotation/flip)
        self.original_data = None
        
        # Store file info text for dialog
        self.file_info_text = "No file loaded\n\nOpen a FITS file to see detailed information."
        
        # Store stats text for dialog
        self.stats_text = "No data"
        
        # Image transformation state
        self.rotation_angle = 0  # 0, 90, 180, 270
        self.flip_horizontal = False
        self.flip_vertical = False
        
        # Initialize image display engine
        self.image_engine = ImageDisplayEngine()
        # Set default scaling to log for better visibility of astronomical data
        self.image_engine.set_scaling_mode('log')
        
        # Set up the UI
        self.init_ui()
        
        # Apply dark theme styling
        self.apply_styling()
        
        # Initialize colormap status
        self.update_colormap_status()
        
        # Auto-load default FITS file if it exists
        self.auto_load_default_file()
    
    def auto_load_default_file(self):
        """Automatically load the default FITS file on startup."""
        import os
        default_file = r"E:\test\Kiro_fit\fit_file\Stacked_247_M 42_10.0s_LP_20250119-213147.fit"
        
        if os.path.exists(default_file):
            # Use QTimer to load after UI is fully initialized
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(100, lambda: self.open_file(default_file))
        else:
            self.statusBar().showMessage(f"⚠️ Default file not found: {default_file}")
    
    def init_ui(self):
        """Initialize the user interface with high-tech styling."""
        self.setWindowTitle("⭐ FITS Viewer - Astronomical Data Explorer")
        
        # Set window to maximum width with reasonable height
        from PyQt5.QtWidgets import QDesktopWidget
        screen = QDesktopWidget().screenGeometry()
        # Use full width and 90% of screen height
        self.setGeometry(0, 50, screen.width(), int(screen.height() * 0.9))
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Create main splitter (horizontal) - 2 panels only
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.setHandleWidth(2)
        
        # Center panel: Image display (full size)
        center_panel = self.create_center_panel()
        main_splitter.addWidget(center_panel)
        
        # Right panel: Info panel
        right_panel = self.create_right_panel()
        main_splitter.addWidget(right_panel)
        
        # Set splitter sizes - maximize image space, right panel for controls
        # Total width minus margins, give most space to image
        # User can adjust the splitter by dragging
        main_splitter.setSizes([1000, 450])
        
        main_layout.addWidget(main_splitter)
        
        # Status bar with enhanced styling
        self.statusBar().showMessage("🚀 Ready - Awaiting FITS file...")
        
        # Create menu bar (after widgets are created)
        self.create_menu_bar()
        
        # Add subtle pulsing animation to status bar
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status_animation)
        self.status_timer.start(2000)
        self.status_pulse = 0
    
    def create_center_panel(self):
        """Create the center panel with full-size image display."""
        panel = QFrame()
        panel.setFrameShape(QFrame.StyledPanel)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(0)
        
        # Create matplotlib canvas from image engine
        self.image_canvas = FigureCanvasQTAgg(self.image_engine.figure)
        self.image_canvas.setMinimumHeight(700)
        self.image_canvas.setStyleSheet("""
            background: #0a0a0a;
            border: 2px solid #00d4ff;
            border-radius: 8px;
        """)
        
        # Add glow effect to canvas
        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(20)
        glow.setColor(QColor(0, 212, 255, 80))
        glow.setOffset(0, 0)
        self.image_canvas.setGraphicsEffect(glow)
        
        # Connect mouse move event for cursor info
        self.image_canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        
        # Add matplotlib navigation toolbar (zoom, pan, save)
        self.toolbar = NavigationToolbar2QT(self.image_canvas, panel)
        self.toolbar.setStyleSheet("""
            QToolBar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1a1a2e, stop:1 #16213e);
                border: 1px solid #00d4ff;
                border-radius: 4px;
                padding: 2px;
            }
            QToolButton {
                background: transparent;
                color: #00d4ff;
                border: none;
                padding: 4px;
                margin: 2px;
            }
            QToolButton:hover {
                background: #00d4ff;
                color: #000000;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.toolbar)
        
        # Add fullscreen button
        fullscreen_btn = QPushButton("🖼️ Full Screen View (F11)")
        fullscreen_btn.clicked.connect(self.show_fullscreen_view)
        fullscreen_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1a1a2e, stop:1 #16213e);
                color: #00d4ff;
                border: 2px solid #00d4ff;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #00d4ff;
                color: #000000;
            }
            QPushButton:pressed {
                background: #0080ff;
            }
        """)
        layout.addWidget(fullscreen_btn)
        
        layout.addWidget(self.image_canvas)
        
        return panel
    
    def create_right_panel(self):
        """Create the right panel with file information and controls."""
        panel = QFrame()
        panel.setMinimumWidth(400)
        panel.setFrameShape(QFrame.StyledPanel)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # HDU Navigator section
        hdu_title = QLabel("📊 HDU NAVIGATOR")
        hdu_title.setAlignment(Qt.AlignCenter)
        hdu_title.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #00d4ff;
            padding: 8px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #1a1a2e, stop:1 #16213e);
            border-radius: 5px;
            margin-bottom: 5px;
        """)
        layout.addWidget(hdu_title)
        
        # HDU list (compact version)
        self.hdu_list_widget = QListWidget()
        self.hdu_list_widget.itemClicked.connect(self.on_hdu_selected)
        self.hdu_list_widget.setMaximumHeight(150)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 212, 255, 100))
        shadow.setOffset(0, 0)
        self.hdu_list_widget.setGraphicsEffect(shadow)
        
        layout.addWidget(self.hdu_list_widget)
        
        # Header Metadata button
        header_btn = QPushButton("📋 HEADER METADATA")
        header_btn.clicked.connect(self.show_header_metadata)
        header_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1a1a2e, stop:1 #4a0e4e);
                color: #ff6b6b;
                border: 2px solid #ff6b6b;
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton:hover {
                background: #ff6b6b;
                color: #000000;
            }
            QPushButton:pressed {
                background: #ff4444;
            }
        """)
        layout.addWidget(header_btn)
        
        # File Info button
        file_info_btn = QPushButton("ℹ️ FILE INFO")
        file_info_btn.clicked.connect(self.show_file_info)
        file_info_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1a1a2e, stop:1 #3d2c00);
                color: #ffd93d;
                border: 2px solid #ffd93d;
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton:hover {
                background: #ffd93d;
                color: #000000;
            }
            QPushButton:pressed {
                background: #ffaa00;
            }
        """)
        layout.addWidget(file_info_btn)
        
        # Colormap Controls
        colormap_group = self.create_colormap_controls()
        layout.addWidget(colormap_group)
        
        # Scaling Controls
        scaling_group = self.create_scaling_controls()
        layout.addWidget(scaling_group)
        
        # Quick Stats button
        stats_btn = QPushButton("📈 QUICK STATS")
        stats_btn.clicked.connect(self.show_quick_stats)
        stats_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1a1a2e, stop:1 #16213e);
                color: #a8dadc;
                border: 2px solid #a8dadc;
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
                font-size: 15px;
            }
            QPushButton:hover {
                background: #a8dadc;
                color: #000000;
            }
            QPushButton:pressed {
                background: #6ba8b8;
            }
        """)
        layout.addWidget(stats_btn)
        
        layout.addStretch()
        
        return panel
    
    def create_colormap_controls(self):
        """Create colormap selection controls."""
        group = QGroupBox("🎨 COLORMAP")
        group.setStyleSheet("""
            QGroupBox {
                color: #00ff88;
                font-weight: bold;
                border: 2px solid #00d4ff;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        layout = QVBoxLayout(group)
        
        # Status label
        self.colormap_status_label = QLabel("ℹ️ RGB image - colormap disabled")
        self.colormap_status_label.setStyleSheet("""
            QLabel {
                color: #ffd93d;
                font-size: 12px;
                padding: 5px;
                background: #1a1a2e;
                border: 1px solid #ffd93d;
                border-radius: 3px;
            }
        """)
        self.colormap_status_label.setWordWrap(True)
        layout.addWidget(self.colormap_status_label)
        
        # RGB to Grayscale button
        self.rgb_to_gray_btn = QPushButton("Convert RGB → Gray")
        self.rgb_to_gray_btn.clicked.connect(self.on_rgb_to_grayscale)
        self.rgb_to_gray_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1a1a2e, stop:1 #16213e);
                color: #ffd93d;
                border: 2px solid #ffd93d;
                border-radius: 5px;
                padding: 6px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background: #ffd93d;
                color: #000000;
            }
            QPushButton:pressed {
                background: #ffaa00;
            }
            QPushButton:disabled {
                background: #1a1a2e;
                color: #666666;
                border-color: #666666;
            }
        """)
        self.rgb_to_gray_btn.hide()
        layout.addWidget(self.rgb_to_gray_btn)
        
        # Colormap selection
        self.colormap_combo = QComboBox()
        colormaps = [
            'viridis', 'gray', 'hot', 'cool', 'rainbow',
            'jet', 'plasma', 'inferno', 'magma', 'cividis',
            'twilight', 'turbo', 'seismic', 'RdYlBu', 'Spectral'
        ]
        self.colormap_combo.addItems(colormaps)
        self.colormap_combo.setCurrentText('viridis')
        self.colormap_combo.currentTextChanged.connect(self.on_colormap_changed)
        self.colormap_combo.setStyleSheet("""
            QComboBox {
                background: #1a1a2e;
                color: #e0e0e0;
                border: 1px solid #00d4ff;
                border-radius: 3px;
                padding: 5px;
                font-size: 13px;
            }
            QComboBox:hover {
                border: 2px solid #00d4ff;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background: #1a1a2e;
                color: #e0e0e0;
                selection-background-color: #00d4ff;
                selection-color: #000000;
            }
            QComboBox:disabled {
                background: #0a0a0a;
                color: #666666;
                border-color: #666666;
            }
        """)
        select_label = QLabel("Select:")
        select_label.setStyleSheet("font-size: 13px;")
        layout.addWidget(select_label)
        layout.addWidget(self.colormap_combo)
        
        # Invert colormap checkbox
        self.invert_colormap_check = QCheckBox("Invert Colormap")
        self.invert_colormap_check.toggled.connect(self.on_invert_colormap)
        self.invert_colormap_check.setStyleSheet("""
            QCheckBox {
                color: #e0e0e0;
                spacing: 5px;
                font-size: 13px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #00d4ff;
                border-radius: 3px;
                background: #1a1a2e;
            }
            QCheckBox::indicator:checked {
                background: #00d4ff;
            }
            QCheckBox:disabled {
                color: #666666;
            }
            QCheckBox::indicator:disabled {
                border-color: #666666;
                background: #0a0a0a;
            }
        """)
        layout.addWidget(self.invert_colormap_check)
        
        # Reset view button
        reset_colormap_btn = QPushButton("🔄 Reset View")
        reset_colormap_btn.clicked.connect(self.on_reset_colormap)
        reset_colormap_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1a1a2e, stop:1 #16213e);
                color: #00ff88;
                border: 2px solid #00d4ff;
                border-radius: 5px;
                padding: 6px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #00d4ff;
                color: #000000;
            }
            QPushButton:pressed {
                background: #0080ff;
            }
            QPushButton:disabled {
                background: #1a1a2e;
                color: #666666;
                border-color: #666666;
            }
        """)
        layout.addWidget(reset_colormap_btn)
        
        return group
    
    def create_scaling_controls(self):
        """Create scaling mode controls."""
        group = QGroupBox("📊 SCALING")
        group.setStyleSheet("""
            QGroupBox {
                color: #00ff88;
                font-weight: bold;
                border: 2px solid #00d4ff;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        layout = QVBoxLayout(group)
        
        # Scaling mode selection
        self.scaling_combo = QComboBox()
        scaling_modes = ['linear', 'log', 'sqrt', 'asinh']
        self.scaling_combo.addItems(scaling_modes)
        self.scaling_combo.setCurrentText('log')
        self.scaling_combo.currentTextChanged.connect(self.on_scaling_mode_changed)
        self.scaling_combo.setStyleSheet("""
            QComboBox {
                background: #1a1a2e;
                color: #e0e0e0;
                border: 1px solid #00d4ff;
                border-radius: 3px;
                padding: 5px;
                font-size: 13px;
            }
            QComboBox:hover {
                border: 2px solid #00d4ff;
            }
            QComboBox QAbstractItemView {
                background: #1a1a2e;
                color: #e0e0e0;
                selection-background-color: #00d4ff;
                selection-color: #000000;
            }
        """)
        mode_label = QLabel("Mode:")
        mode_label.setStyleSheet("font-size: 13px;")
        layout.addWidget(mode_label)
        layout.addWidget(self.scaling_combo)
        
        # Histogram display
        histogram_label = QLabel("Histogram:")
        histogram_label.setStyleSheet("font-size: 13px;")
        layout.addWidget(histogram_label)
        self.histogram_widget = HistogramWidget(parent=group, width=2.8, height=1.8)
        self.histogram_widget.setStyleSheet("""
            background: #0a0a0a;
            border: 1px solid #00d4ff;
            border-radius: 4px;
        """)
        layout.addWidget(self.histogram_widget)
        
        # Min/Max sliders
        slider_style = """
            QSlider::groove:horizontal {
                border: 1px solid #00d4ff;
                height: 8px;
                background: #1a1a2e;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00d4ff, stop:1 #0080ff);
                border: 1px solid #00ffff;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: #00ffff;
            }
        """
        
        # Min slider
        min_label = QLabel("Min:")
        min_label.setStyleSheet("font-size: 13px;")
        layout.addWidget(min_label)
        min_layout = QHBoxLayout()
        self.min_slider = QSlider(Qt.Horizontal)
        self.min_slider.setMinimum(0)
        self.min_slider.setMaximum(2000)
        self.min_slider.setValue(0)
        self.min_slider.valueChanged.connect(self.on_min_slider_changed)
        self.min_slider.setStyleSheet(slider_style)
        
        self.min_value_label = QLabel("0")
        self.min_value_label.setMinimumWidth(60)
        self.min_value_label.setStyleSheet("color: #00d4ff; font-weight: bold; font-size: 13px;")
        
        min_layout.addWidget(self.min_slider)
        min_layout.addWidget(self.min_value_label)
        layout.addLayout(min_layout)
        
        # Max slider
        max_label = QLabel("Max:")
        max_label.setStyleSheet("font-size: 13px;")
        layout.addWidget(max_label)
        max_layout = QHBoxLayout()
        self.max_slider = QSlider(Qt.Horizontal)
        self.max_slider.setMinimum(0)
        self.max_slider.setMaximum(1000)
        self.max_slider.setValue(1000)
        self.max_slider.valueChanged.connect(self.on_max_slider_changed)
        self.max_slider.setStyleSheet(slider_style)
        
        self.max_value_label = QLabel("1")
        self.max_value_label.setMinimumWidth(60)
        self.max_value_label.setStyleSheet("color: #00d4ff; font-weight: bold; font-size: 13px;")
        
        max_layout.addWidget(self.max_slider)
        max_layout.addWidget(self.max_value_label)
        layout.addLayout(max_layout)
        
        # Auto-scale button
        auto_scale_btn = QPushButton("🔄 Auto Scale")
        auto_scale_btn.clicked.connect(self.on_auto_scale)
        auto_scale_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1a1a2e, stop:1 #16213e);
                color: #00ff88;
                border: 2px solid #00d4ff;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #00d4ff;
                color: #000000;
            }
            QPushButton:pressed {
                background: #0080ff;
            }
        """)
        layout.addWidget(auto_scale_btn)
        
        # Store data range for slider mapping
        self.data_min = 0
        self.data_max = 1
        
        return group
    
    def on_min_slider_changed(self, value):
        """Handle min slider change."""
        if self.image_engine.current_data is not None:
            # Map slider value (0-2000) to data range
            data_range = self.data_max - self.data_min
            actual_value = self.data_min + (value / 2000.0) * data_range
            
            # Update label
            self.min_value_label.setText(f"{actual_value:.2f}")
            
            # Update image engine if min < max
            if actual_value < self.image_engine.vmax:
                self.image_engine.vmin = actual_value
                self.image_engine.update_display()
                self.image_canvas.draw()
                
                # Update histogram lines
                self.histogram_widget.update_scaling_lines(actual_value, self.image_engine.vmax)
    
    def on_max_slider_changed(self, value):
        """Handle max slider change."""
        if self.image_engine.current_data is not None:
            # Map slider value (0-1000) to data range
            data_range = self.data_max - self.data_min
            actual_value = self.data_min + (value / 1000.0) * data_range
            
            # Update label
            self.max_value_label.setText(f"{actual_value:.2f}")
            
            # Update image engine if max > min
            if actual_value > self.image_engine.vmin:
                self.image_engine.vmax = actual_value
                self.image_engine.update_display()
                self.image_canvas.draw()
                
                # Update histogram lines
                self.histogram_widget.update_scaling_lines(self.image_engine.vmin, actual_value)
    
    def update_slider_ranges(self):
        """Update slider ranges based on current data."""
        if self.image_engine.current_data is not None:
            import numpy as np
            data = self.image_engine.current_data
            valid_data = data[np.isfinite(data)]
            
            if len(valid_data) > 0:
                self.data_min = float(valid_data.min())
                self.data_max = float(valid_data.max())
                
                # Set slider positions based on current vmin/vmax
                if self.data_max > self.data_min:
                    min_pos = int(((self.image_engine.vmin - self.data_min) / 
                                   (self.data_max - self.data_min)) * 2000)
                    max_pos = int(((self.image_engine.vmax - self.data_min) / 
                                   (self.data_max - self.data_min)) * 1000)
                    
                    self.min_slider.setValue(min_pos)
                    self.max_slider.setValue(max_pos)
                    
                    self.min_value_label.setText(f"{self.image_engine.vmin:.2f}")
                    self.max_value_label.setText(f"{self.image_engine.vmax:.2f}")
    
    def update_colormap_status(self):
        """Update colormap status based on current data."""
        if self.image_engine.current_data is None:
            self.colormap_status_label.setText("ℹ️ No data loaded")
            self.colormap_combo.setEnabled(False)
            self.invert_colormap_check.setEnabled(False)
            self.rgb_to_gray_btn.hide()
            return
        
        data = self.image_engine.current_data
        
        # Check if RGB (3-channel)
        if data.ndim == 3 and data.shape[0] == 3:
            self.colormap_status_label.setText("ℹ️ RGB image - colormap disabled\n(Convert to grayscale to use colormaps)")
            self.colormap_status_label.setStyleSheet("""
                QLabel {
                    color: #ffd93d;
                    font-size: 12px;
                    padding: 5px;
                    background: #1a1a2e;
                    border: 1px solid #ffd93d;
                    border-radius: 3px;
                }
            """)
            self.colormap_combo.setEnabled(False)
            self.invert_colormap_check.setEnabled(False)
            self.rgb_to_gray_btn.show()
            self.rgb_to_gray_btn.setEnabled(True)
        else:
            # Single channel - colormap applies
            self.colormap_status_label.setText("✅ Grayscale - colormap active")
            self.colormap_status_label.setStyleSheet("""
                QLabel {
                    color: #00ff88;
                    font-size: 12px;
                    padding: 5px;
                    background: #1a1a2e;
                    border: 1px solid #00ff88;
                    border-radius: 3px;
                }
            """)
            self.colormap_combo.setEnabled(True)
            self.invert_colormap_check.setEnabled(True)
            self.rgb_to_gray_btn.hide()
            self.rgb_to_gray_btn.setEnabled(False)
    
    def on_rgb_to_grayscale(self):
        """Convert RGB image to grayscale."""
        if self.image_engine.current_data is None:
            return
        
        data = self.image_engine.current_data
        
        # Check if RGB
        if data.ndim == 3 and data.shape[0] == 3:
            import numpy as np
            
            # Store original RGB data before conversion
            self.original_rgb_data = data.copy()
            
            # Convert RGB to grayscale using luminosity method
            # Y = 0.299*R + 0.587*G + 0.114*B
            r, g, b = data[0], data[1], data[2]
            grayscale = 0.299 * r + 0.587 * g + 0.114 * b
            
            # Update image engine with grayscale data
            self.image_engine.current_data = grayscale
            self.image_engine.set_data(grayscale)
            self.image_canvas.draw()
            
            # Update controls
            self.update_colormap_status()
            self.update_slider_ranges()
            self.histogram_widget.update_histogram(grayscale,
                                                   self.image_engine.vmin,
                                                   self.image_engine.vmax)
            
            self.statusBar().showMessage("✅ Converted to grayscale - colormaps now available")
    
    def on_colormap_changed(self, colormap_name):
        """Handle colormap selection change."""
        if self.invert_colormap_check.isChecked():
            colormap_name = colormap_name + '_r'
        self.image_engine.set_colormap(colormap_name)
        self.image_canvas.draw()
    
    def on_invert_colormap(self, checked):
        """Handle colormap inversion toggle."""
        current = self.colormap_combo.currentText()
        if checked:
            self.image_engine.set_colormap(current + '_r')
        else:
            self.image_engine.set_colormap(current)
        self.image_canvas.draw()
    
    def on_reset_colormap(self):
        """Reset view to original state (restore RGB colors if converted)."""
        if self.image_engine.current_data is None:
            self.statusBar().showMessage("⚠️ No image loaded to reset")
            return
        
        # If we have original RGB data stored, restore it
        if self.original_rgb_data is not None:
            # Restore original RGB data
            self.image_engine.current_data = self.original_rgb_data
            self.image_engine.set_data(self.original_rgb_data)
            
            # Update controls for RGB
            self.update_colormap_status()
            self.update_slider_ranges()
            self.histogram_widget.update_histogram(self.original_rgb_data,
                                                   self.image_engine.vmin,
                                                   self.image_engine.vmax)
            
            self.statusBar().showMessage("✅ View reset - original RGB colors restored")
        else:
            # No RGB conversion was done, just reset settings
            # Reset colormap to default
            self.colormap_combo.setCurrentText('viridis')
            
            # Uncheck invert if it's checked
            if self.invert_colormap_check.isChecked():
                self.invert_colormap_check.setChecked(False)
            
            # Apply the default colormap
            self.image_engine.set_colormap('viridis')
            
            # Reset scaling mode to log (default)
            self.scaling_combo.setCurrentText('log')
            self.image_engine.set_scaling_mode('log')
            
            # Reset to auto-scale
            vmin, vmax = self.image_engine.auto_scale(percentile_low=0.5, percentile_high=99.5)
            self.image_engine.set_scaling_limits(vmin, vmax)
            
            # Update sliders
            self.update_slider_ranges()
            
            # Update histogram
            self.histogram_widget.update_histogram(self.image_engine.current_data,
                                                   self.image_engine.vmin,
                                                   self.image_engine.vmax)
            
            self.statusBar().showMessage("✅ View reset to original state")
        
        # Reset zoom (home view)
        self.toolbar.home()
        
        # Clear and redraw
        self.image_engine.axes.clear()
        
        # Remove any existing colorbar
        if hasattr(self.image_engine.figure, 'colorbar_ax') and self.image_engine.figure.colorbar_ax is not None:
            self.image_engine.figure.delaxes(self.image_engine.figure.colorbar_ax)
            self.image_engine.figure.colorbar_ax = None
        
        # Redraw the image
        self.image_engine.update_display()
        self.image_canvas.draw()
    
    def on_scaling_mode_changed(self, mode):
        """Handle scaling mode change."""
        self.image_engine.set_scaling_mode(mode)
        self.image_canvas.draw()
    
    def on_auto_scale(self):
        """Handle auto-scale button click with optimal settings for astronomical images."""
        if self.image_engine.current_data is not None:
            import numpy as np
            
            # Use 0.5%-99.5% percentile for better contrast in astronomical images
            vmin, vmax = self.image_engine.auto_scale(percentile_low=0.5, percentile_high=99.5)
            self.image_engine.set_scaling_limits(vmin, vmax)
            self.image_canvas.draw()
            self.update_slider_ranges()
            self.histogram_widget.update_scaling_lines(vmin, vmax)
            
            # Calculate how much data is clipped
            valid_data = self.image_engine.current_data[np.isfinite(self.image_engine.current_data)]
            clipped = np.sum((valid_data < vmin) | (valid_data > vmax))
            clipped_pct = (clipped / valid_data.size) * 100
            
            self.statusBar().showMessage(
                f"✅ Auto-scaled: [{vmin:.1f}, {vmax:.1f}] "
                f"(clips {clipped_pct:.1f}% outliers for optimal contrast)"
            )
    
    def update_status_animation(self):
        """Update status bar animation."""
        self.status_pulse = (self.status_pulse + 1) % 3
        dots = "." * self.status_pulse
        if self.fits_manager.filepath:
            self.statusBar().showMessage(f"✅ File loaded: {self.fits_manager.filepath}")
        else:
            self.statusBar().showMessage(f"🚀 Ready{dots}")
    
    def create_menu_bar(self):
        """Create the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        # Open action
        open_action = QAction("&Open FITS File...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file_dialog)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        # Zoom actions
        zoom_in_action = QAction("Zoom &In", self)
        zoom_in_action.setShortcut("Ctrl++")
        zoom_in_action.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("Zoom &Out", self)
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_action)
        
        zoom_fit_action = QAction("Zoom &Fit", self)
        zoom_fit_action.setShortcut("Ctrl+0")
        zoom_fit_action.triggered.connect(self.zoom_fit)
        view_menu.addAction(zoom_fit_action)
        
        view_menu.addSeparator()
        
        # Pan action
        pan_action = QAction("&Pan/Move View", self)
        pan_action.setShortcut("Ctrl+P")
        pan_action.triggered.connect(self.activate_pan)
        view_menu.addAction(pan_action)
        
        view_menu.addSeparator()
        
        # Fullscreen action
        fullscreen_action = QAction("&Full Screen View", self)
        fullscreen_action.setShortcut("F11")
        fullscreen_action.triggered.connect(self.show_fullscreen_view)
        view_menu.addAction(fullscreen_action)
        
        view_menu.addSeparator()
        
        # Rotation submenu
        rotate_menu = view_menu.addMenu("🔄 &Rotate")
        
        # Custom rotation
        custom_rotate_action = QAction("Custom Angle...", self)
        custom_rotate_action.setShortcut("Ctrl+Shift+R")
        custom_rotate_action.triggered.connect(self.rotate_custom)
        rotate_menu.addAction(custom_rotate_action)
        
        rotate_menu.addSeparator()
        
        rotate_90_action = QAction("Rotate 90° CW", self)
        rotate_90_action.setShortcut("Ctrl+R")
        rotate_90_action.triggered.connect(lambda: self.rotate_image(90))
        rotate_menu.addAction(rotate_90_action)
        
        rotate_180_action = QAction("Rotate 180°", self)
        rotate_180_action.triggered.connect(lambda: self.rotate_image(180))
        rotate_menu.addAction(rotate_180_action)
        
        rotate_270_action = QAction("Rotate 270° CW (90° CCW)", self)
        rotate_270_action.triggered.connect(lambda: self.rotate_image(270))
        rotate_menu.addAction(rotate_270_action)
        
        rotate_menu.addSeparator()
        
        flip_h_action = QAction("Flip &Horizontal", self)
        flip_h_action.setShortcut("Ctrl+Shift+H")
        flip_h_action.triggered.connect(self.flip_horizontal_image)
        rotate_menu.addAction(flip_h_action)
        
        flip_v_action = QAction("Flip &Vertical", self)
        flip_v_action.setShortcut("Ctrl+Shift+V")
        flip_v_action.triggered.connect(self.flip_vertical_image)
        rotate_menu.addAction(flip_v_action)
        
        rotate_menu.addSeparator()
        
        reset_transform_action = QAction("Reset Transformations", self)
        reset_transform_action.triggered.connect(self.reset_transformations)
        rotate_menu.addAction(reset_transform_action)
        
        view_menu.addSeparator()
        
        # Scaling menu
        scaling_menu = menubar.addMenu("&Scaling")
        
        # Scaling mode actions
        linear_action = QAction("&Linear", self)
        linear_action.setShortcut("Ctrl+1")
        linear_action.triggered.connect(lambda: self.set_scaling_mode_shortcut('linear'))
        scaling_menu.addAction(linear_action)
        
        log_action = QAction("L&og", self)
        log_action.setShortcut("Ctrl+2")
        log_action.triggered.connect(lambda: self.set_scaling_mode_shortcut('log'))
        scaling_menu.addAction(log_action)
        
        sqrt_action = QAction("&Sqrt", self)
        sqrt_action.setShortcut("Ctrl+3")
        sqrt_action.triggered.connect(lambda: self.set_scaling_mode_shortcut('sqrt'))
        scaling_menu.addAction(sqrt_action)
        
        asinh_action = QAction("&Asinh", self)
        asinh_action.setShortcut("Ctrl+4")
        asinh_action.triggered.connect(lambda: self.set_scaling_mode_shortcut('asinh'))
        scaling_menu.addAction(asinh_action)
        
        scaling_menu.addSeparator()
        
        # Auto-scale action
        auto_scale_action = QAction("&Auto Scale", self)
        auto_scale_action.setShortcut("Ctrl+A")
        auto_scale_action.triggered.connect(self.on_auto_scale)
        scaling_menu.addAction(auto_scale_action)
        
        # Colormap menu
        colormap_menu = menubar.addMenu("&Colormap")
        
        # Common colormaps with shortcuts
        gray_action = QAction("&Gray", self)
        gray_action.setShortcut("Ctrl+G")
        gray_action.triggered.connect(lambda: self.set_colormap_shortcut('gray'))
        colormap_menu.addAction(gray_action)
        
        hot_action = QAction("&Hot", self)
        hot_action.setShortcut("Ctrl+H")
        hot_action.triggered.connect(lambda: self.set_colormap_shortcut('hot'))
        colormap_menu.addAction(hot_action)
        
        cool_action = QAction("&Cool", self)
        cool_action.setShortcut("Ctrl+C")
        cool_action.triggered.connect(lambda: self.set_colormap_shortcut('cool'))
        colormap_menu.addAction(cool_action)
        
        viridis_action = QAction("&Viridis", self)
        viridis_action.setShortcut("Ctrl+V")
        viridis_action.triggered.connect(lambda: self.set_colormap_shortcut('viridis'))
        colormap_menu.addAction(viridis_action)
        
        colormap_menu.addSeparator()
        
        # Invert colormap
        invert_action = QAction("&Invert Colormap", self)
        invert_action.setShortcut("Ctrl+I")
        invert_action.setCheckable(True)
        invert_action.triggered.connect(self.invert_colormap_check.toggle)
        colormap_menu.addAction(invert_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        # Keyboard shortcuts
        shortcuts_action = QAction("&Keyboard Shortcuts", self)
        shortcuts_action.setShortcut("F1")
        shortcuts_action.triggered.connect(self.show_keyboard_shortcuts)
        help_menu.addAction(shortcuts_action)
        
        # About
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def apply_styling(self):
        """Apply high-tech futuristic theme styling."""
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0a0a0a, stop:0.5 #1a1a2e, stop:1 #0a0a0a);
            }
            
            QWidget {
                background-color: transparent;
                color: #e0e0e0;
                font-family: 'Segoe UI', Arial;
            }
            
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #16213e, stop:1 #0f3460);
                border: 1px solid #00d4ff;
                border-radius: 8px;
            }
            
            QListWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0a0a0a, stop:1 #1a1a2e);
                border: 2px solid #00d4ff;
                border-radius: 6px;
                padding: 8px;
                color: #e0e0e0;
                font-size: 14px;
            }
            
            QListWidget::item {
                padding: 12px;
                border-radius: 5px;
                margin: 2px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #16213e, stop:1 #0f3460);
                border: 1px solid #2a4a6a;
            }
            
            QListWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00d4ff, stop:1 #0080ff);
                color: #000000;
                font-weight: bold;
                border: 2px solid #00ffff;
            }
            
            QListWidget::item:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1e3a5f, stop:1 #2a4a6a);
                border: 1px solid #00d4ff;
            }
            
            QTextEdit {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0a0a0a, stop:1 #1a1a2e);
                border: 2px solid #00d4ff;
                border-radius: 6px;
                padding: 10px;
                color: #00ff88;
                selection-background-color: #0080ff;
                font-family: 'Consolas', 'Courier New', monospace;
            }
            
            QLabel {
                color: #e0e0e0;
            }
            
            QMenuBar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1a1a2e, stop:1 #16213e);
                color: #00d4ff;
                border-bottom: 2px solid #00d4ff;
                padding: 4px;
                font-weight: bold;
            }
            
            QMenuBar::item {
                padding: 8px 16px;
                background: transparent;
                border-radius: 4px;
            }
            
            QMenuBar::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00d4ff, stop:1 #0080ff);
                color: #000000;
            }
            
            QMenu {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a1a2e, stop:1 #0f3460);
                color: #e0e0e0;
                border: 2px solid #00d4ff;
                border-radius: 6px;
                padding: 5px;
            }
            
            QMenu::item {
                padding: 8px 30px;
                border-radius: 4px;
                margin: 2px;
                font-size: 15px;
            }
            
            QMenu::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00d4ff, stop:1 #0080ff);
                color: #000000;
                font-weight: bold;
            }
            
            QStatusBar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1a1a2e, stop:1 #16213e);
                color: #00ff88;
                border-top: 2px solid #00d4ff;
                padding: 5px;
                font-weight: bold;
                font-size: 15px;
            }
            
            QSplitter::handle {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00d4ff, stop:1 #0080ff);
                width: 2px;
                height: 2px;
            }
            
            QSplitter::handle:hover {
                background: #00ffff;
            }
            
            QScrollBar:vertical {
                background: #0a0a0a;
                width: 12px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00d4ff, stop:1 #0080ff);
                border-radius: 6px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background: #00ffff;
            }
            
            QScrollBar:horizontal {
                background: #0a0a0a;
                height: 12px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00d4ff, stop:1 #0080ff);
                border-radius: 6px;
                min-width: 20px;
            }
            
            QScrollBar::handle:horizontal:hover {
                background: #00ffff;
            }
        """)
    
    def open_file_dialog(self):
        """Open file dialog to select a FITS file."""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Open FITS File",
            "",
            "FITS Files (*.fits *.fit);;All Files (*.*)"
        )
        
        if filepath:
            self.open_file(filepath)
    
    def open_file(self, filepath):
        """
        Open a FITS file with enhanced feedback.
        
        Args:
            filepath: Path to the FITS file
        """
        # Show loading message
        self.statusBar().showMessage(f"⏳ Loading: {filepath}...")
        
        # Try to open the file
        success = self.fits_manager.open_file(filepath)
        
        if not success:
            QMessageBox.critical(
                self,
                "❌ Error Opening File",
                f"Failed to open FITS file:\n\n{filepath}\n\n"
                "Please check that:\n"
                "• The file exists\n"
                "• The file is a valid FITS format\n"
                "• You have permission to read the file"
            )
            self.statusBar().showMessage("❌ Failed to open file")
            return
        
        # Clear transformation state when opening new file
        self.rotation_angle = 0
        self.flip_horizontal = False
        self.flip_vertical = False
        self.original_data = None
        self.original_rgb_data = None
        
        # Update UI with file contents
        self.update_hdu_list()
        
        # Update file info panel
        self.update_file_info(filepath)
        
        # Select and display the first HDU
        if self.fits_manager.num_hdus > 0:
            self.current_hdu_index = 0
            self.hdu_list_widget.setCurrentRow(0)
            self.update_displays()
        
        # Update status bar
        self.statusBar().showMessage(f"✅ Loaded: {filepath}")
    
    def update_file_info(self, filepath):
        """Update the file information text."""
        import os
        
        info = f"📁 File Path:\n{filepath}\n\n"
        
        # File size
        file_size = os.path.getsize(filepath)
        if file_size < 1024:
            size_str = f"{file_size} bytes"
        elif file_size < 1024 * 1024:
            size_str = f"{file_size / 1024:.2f} KB"
        else:
            size_str = f"{file_size / 1024 / 1024:.2f} MB"
        
        info += f"💾 File Size: {size_str}\n\n"
        info += f"📊 HDU Count: {self.fits_manager.num_hdus}\n\n"
        
        # HDU summary
        hdu_summary = self.fits_manager.get_hdu_list_summary()
        info += "📋 HDU Summary:\n"
        for hdu_info in hdu_summary:
            info += f"\n  HDU {hdu_info['index']}: {hdu_info['type']}\n"
            if hdu_info['has_data']:
                dims = ' × '.join(str(d) for d in hdu_info['dimensions'])
                info += f"    {dims} ({hdu_info['dtype']})\n"
            else:
                info += f"    No data\n"
        
        # Store the file info text
        self.file_info_text = info
    
    def update_hdu_list(self):
        """Update the HDU list widget with HDUs from the current file."""
        self.hdu_list_widget.clear()
        
        hdu_summary = self.fits_manager.get_hdu_list_summary()
        
        for hdu_info in hdu_summary:
            # Format HDU item text with icons
            index = hdu_info['index']
            hdu_type = hdu_info['type']
            dimensions = hdu_info['dimensions']
            dtype = hdu_info['dtype']
            extname = hdu_info['extname']
            
            # Choose icon based on HDU type
            if index == 0:
                icon = "🌟"  # Primary HDU
            else:
                icon = "📊"  # Extension HDU
            
            # Build display text
            if dimensions:
                dim_str = ' × '.join(str(d) for d in dimensions)
                type_str = f"{dim_str}\n📐 {dtype}" if dtype else dim_str
            else:
                type_str = "⚠️ No data"
            
            if extname:
                item_text = f"{icon} HDU {index}: {extname}\n{hdu_type}\n{type_str}"
            else:
                item_text = f"{icon} HDU {index}\n{hdu_type}\n{type_str}"
            
            item = QListWidgetItem(item_text)
            self.hdu_list_widget.addItem(item)
    
    def on_hdu_selected(self, item):
        """
        Handle HDU selection from the list.
        
        Args:
            item: Selected QListWidgetItem
        """
        # Get the selected HDU index
        self.current_hdu_index = self.hdu_list_widget.row(item)
        
        # Clear transformation state when switching HDUs
        self.rotation_angle = 0
        self.flip_horizontal = False
        self.flip_vertical = False
        self.original_data = None
        self.original_rgb_data = None
        
        # Update displays
        self.update_displays()
    
    def update_displays(self):
        """Update header and image displays for the current HDU."""
        self.update_header_display()
        self.update_image_display()
    
    def update_header_display(self):
        """Update the header text display (no longer used - kept for compatibility)."""
        # This method is no longer needed since we removed the left panel
        # Header is now shown in a separate dialog via show_header_metadata()
        pass
    
    def show_header_metadata(self):
        """Show header metadata in a separate dialog window."""
        if self.fits_manager.filepath is None:
            QMessageBox.information(
                self,
                "No File Loaded",
                "Please open a FITS file first to view header metadata."
            )
            return
        
        # Get header text for current HDU
        header_str = self.fits_manager.get_header(self.current_hdu_index)
        
        # Create and show dialog
        dialog = HeaderMetadataDialog(header_str, self.current_hdu_index, self)
        dialog.exec_()
    
    def show_file_info(self):
        """Show file information in a separate dialog window."""
        if self.fits_manager.filepath is None:
            QMessageBox.information(
                self,
                "No File Loaded",
                "Please open a FITS file first to view file information."
            )
            return
        
        # Create and show dialog with current file info
        dialog = FileInfoDialog(self.file_info_text, self)
        dialog.exec_()
    
    def show_quick_stats(self):
        """Show quick statistics in a separate dialog window."""
        if self.image_engine.current_data is None:
            QMessageBox.information(
                self,
                "No Data",
                "Please open a FITS file first to view statistics."
            )
            return
        
        # Create and show dialog with current stats
        dialog = QuickStatsDialog(self.stats_text, self)
        dialog.exec_()
    
    def rotate_image(self, angle):
        """
        Rotate the image by specified angle (absolute, not cumulative).
        
        Args:
            angle: Rotation angle in degrees (replaces previous rotation)
        """
        if self.image_engine.current_data is None:
            return
        
        # Set rotation to the specified angle (not cumulative)
        self.rotation_angle = angle % 360
        
        # Apply transformation and redisplay
        self.apply_transformations()
        
        self.statusBar().showMessage(f"✅ Rotated image to {self.rotation_angle:.1f}°")
    
    def rotate_custom(self):
        """Open dialog for custom rotation angle."""
        if self.image_engine.current_data is None:
            self.statusBar().showMessage("⚠️ No image loaded")
            return
        
        dialog = CustomRotationDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            angle = dialog.get_angle()
            if angle != 0:
                self.rotate_image(angle)
    
    def flip_horizontal_image(self):
        """Flip the image horizontally."""
        if self.image_engine.current_data is None:
            return
        
        self.flip_horizontal = not self.flip_horizontal
        self.apply_transformations()
        
        status = "flipped" if self.flip_horizontal else "unflipped"
        self.statusBar().showMessage(f"✅ Horizontal {status}")
    
    def flip_vertical_image(self):
        """Flip the image vertically."""
        if self.image_engine.current_data is None:
            return
        
        self.flip_vertical = not self.flip_vertical
        self.apply_transformations()
        
        status = "flipped" if self.flip_vertical else "unflipped"
        self.statusBar().showMessage(f"✅ Vertical {status}")
    
    def reset_transformations(self):
        """Reset all image transformations (rotation and flips)."""
        if self.image_engine.current_data is None:
            return
        
        self.rotation_angle = 0
        self.flip_horizontal = False
        self.flip_vertical = False
        
        # Clear the stored original data so it gets refreshed
        self.original_data = None
        
        self.apply_transformations()
        
        self.statusBar().showMessage("✅ All transformations reset")
    
    def apply_transformations(self):
        """Apply current rotation and flip transformations to the image."""
        if self.image_engine.current_data is None:
            return
        
        import numpy as np
        from scipy import ndimage
        
        # Always start from the original unrotated data
        if self.original_data is not None:
            data = self.original_data.copy()
        else:
            # First time - store the original data
            data = self.fits_manager.get_data(self.current_hdu_index)
            if data is None:
                return
            self.original_data = data.copy()
            data = data.copy()
        
        # Store original dtype to preserve it after rotation
        original_dtype = data.dtype
        
        # Apply rotation
        if self.rotation_angle != 0:
            try:
                # For RGB images (channels, height, width), rotate each channel
                if data.ndim == 3 and data.shape[0] == 3:
                    rotated_channels = []
                    for i in range(3):
                        # Rotate with prefilter=False to preserve values better
                        rotated = ndimage.rotate(data[i], self.rotation_angle, 
                                                reshape=True, order=1, mode='constant', 
                                                cval=0, prefilter=False)
                        rotated_channels.append(rotated)
                    data = np.array(rotated_channels)
                # For grayscale or other formats
                else:
                    data = ndimage.rotate(data, self.rotation_angle, 
                                         reshape=True, order=1, mode='constant', 
                                         cval=0, prefilter=False)
                
                # Preserve original data type
                if data.dtype != original_dtype:
                    # Clip to valid range for the dtype
                    if np.issubdtype(original_dtype, np.integer):
                        info = np.iinfo(original_dtype)
                        data = np.clip(data, info.min, info.max)
                    data = data.astype(original_dtype)
                    
            except Exception as e:
                self.statusBar().showMessage(f"⚠️ Rotation error: {str(e)}")
                return
        
        # Apply flips
        if self.flip_horizontal:
            data = np.flip(data, axis=-1)
        if self.flip_vertical:
            data = np.flip(data, axis=-2)
        
        # Store current vmin/vmax before updating
        old_vmin = self.image_engine.vmin
        old_vmax = self.image_engine.vmax
        
        # Update display
        self.image_engine.current_data = data
        self.image_engine.set_data(data)
        
        # Restore the scaling limits to prevent color shift
        if old_vmin is not None and old_vmax is not None:
            self.image_engine.vmin = old_vmin
            self.image_engine.vmax = old_vmax
            self.image_engine.update_display()
        
        self.image_canvas.draw()
        
        # Update histogram
        self.histogram_widget.update_histogram(data,
                                               self.image_engine.vmin,
                                               self.image_engine.vmax)
    
    def zoom_in(self):
        """Zoom in on the image and activate pan mode."""
        if self.image_engine.current_data is None:
            return
        
        # Get current axis limits
        xlim = self.image_engine.axes.get_xlim()
        ylim = self.image_engine.axes.get_ylim()
        
        # Calculate center
        x_center = (xlim[0] + xlim[1]) / 2
        y_center = (ylim[0] + ylim[1]) / 2
        
        # Calculate new range (zoom in by factor of 0.8)
        x_range = (xlim[1] - xlim[0]) * 0.8 / 2
        y_range = (ylim[1] - ylim[0]) * 0.8 / 2
        
        # Set new limits
        self.image_engine.axes.set_xlim(x_center - x_range, x_center + x_range)
        self.image_engine.axes.set_ylim(y_center - y_range, y_center + y_range)
        
        # Redraw
        self.image_canvas.draw()
        
        # Automatically activate pan mode
        self.toolbar.pan()
        self.statusBar().showMessage("🔍 Zoomed in - Pan mode activated (click and drag to move)")
    
    def zoom_out(self):
        """Zoom out from the image, stopping at maximum (full image) size."""
        if self.image_engine.current_data is None:
            return
        
        # Get the image data shape to determine maximum extent
        data = self.image_engine.current_data
        
        # Determine dimensions based on data shape
        if data.ndim == 2:
            height, width = data.shape
        elif data.ndim == 3 and data.shape[2] == 3:
            height, width = data.shape[0], data.shape[1]
        elif data.ndim == 3 and data.shape[0] == 3:
            height, width = data.shape[1], data.shape[2]
        else:
            height, width = data.shape[-2], data.shape[-1]
        
        # Maximum extent (full image)
        max_xlim = (-0.5, width - 0.5)
        max_ylim = (-0.5, height - 0.5)
        
        # Get current axis limits
        xlim = self.image_engine.axes.get_xlim()
        ylim = self.image_engine.axes.get_ylim()
        
        # Check if already at maximum extent
        if (xlim[0] <= max_xlim[0] and xlim[1] >= max_xlim[1] and
            ylim[0] <= max_ylim[0] and ylim[1] >= max_ylim[1]):
            self.statusBar().showMessage("🔍 Already at maximum zoom (full image)")
            return
        
        # Calculate center
        x_center = (xlim[0] + xlim[1]) / 2
        y_center = (ylim[0] + ylim[1]) / 2
        
        # Calculate new range (zoom out by factor of 1.25)
        x_range = (xlim[1] - xlim[0]) * 1.25 / 2
        y_range = (ylim[1] - ylim[0]) * 1.25 / 2
        
        # Calculate new limits
        new_xlim = (x_center - x_range, x_center + x_range)
        new_ylim = (y_center - y_range, y_center + y_range)
        
        # Clamp to maximum extent (don't zoom out beyond full image)
        final_xlim = (max(new_xlim[0], max_xlim[0]), min(new_xlim[1], max_xlim[1]))
        final_ylim = (max(new_ylim[0], max_ylim[0]), min(new_ylim[1], max_ylim[1]))
        
        # Set new limits
        self.image_engine.axes.set_xlim(final_xlim)
        self.image_engine.axes.set_ylim(final_ylim)
        
        # Redraw
        self.image_canvas.draw()
        
        # Check if we reached maximum
        if (final_xlim[0] <= max_xlim[0] and final_xlim[1] >= max_xlim[1] and
            final_ylim[0] <= max_ylim[0] and final_ylim[1] >= max_ylim[1]):
            self.statusBar().showMessage("🔍 Zoomed out to maximum (full image)")
        else:
            self.statusBar().showMessage("🔍 Zoomed out")
    
    def zoom_fit(self):
        """Fit the image to the window (reset zoom)."""
        if self.image_engine.current_data is None:
            return
        
        # Get the image data shape
        data = self.image_engine.current_data
        
        # Determine dimensions based on data shape
        if data.ndim == 2:
            # Grayscale image
            height, width = data.shape
        elif data.ndim == 3 and data.shape[2] == 3:
            # RGB image (height, width, channels)
            height, width = data.shape[0], data.shape[1]
        elif data.ndim == 3 and data.shape[0] == 3:
            # RGB image (channels, height, width)
            height, width = data.shape[1], data.shape[2]
        else:
            # Use toolbar home as fallback
            self.toolbar.home()
            self.statusBar().showMessage("🔍 Zoom reset to fit")
            return
        
        # Set axis limits to show entire image
        # Matplotlib uses (left, right) for x and (bottom, top) for y
        # Image coordinates: origin='lower' means (0,0) is bottom-left
        self.image_engine.axes.set_xlim(-0.5, width - 0.5)
        self.image_engine.axes.set_ylim(-0.5, height - 0.5)
        
        # Redraw
        self.image_canvas.draw()
        self.statusBar().showMessage("🔍 Zoom reset to fit - Showing entire image")
    
    def activate_pan(self):
        """Activate pan/move mode for the image."""
        if self.image_engine.current_data is None:
            return
        
        # Activate pan mode in the toolbar
        self.toolbar.pan()
        self.statusBar().showMessage("✋ Pan mode activated - Click and drag to move the view. Click Pan again to deactivate.")
    
    def update_image_display(self):
        """Update the image display with enhanced visuals."""
        # Get HDU info
        hdu_info = self.fits_manager.get_hdu_info(self.current_hdu_index)
        
        if not hdu_info.get('has_data', False):
            # Clear the canvas and show message
            self.image_engine.axes.clear()
            self.image_engine.axes.text(
                0.5, 0.5, 
                "⚠️ NO IMAGE DATA\n\nThis HDU contains header information only",
                ha='center', va='center', 
                color='#00d4ff', fontsize=14, fontweight='bold',
                transform=self.image_engine.axes.transAxes
            )
            self.image_engine.axes.set_facecolor('#0a0a0a')
            self.image_engine.axes.axis('off')
            self.image_engine.figure.canvas.draw_idle()
            return
        
        # Get data
        data = self.fits_manager.get_data(self.current_hdu_index)
        
        if data is None:
            # Clear the canvas and show error
            self.image_engine.axes.clear()
            self.image_engine.axes.text(
                0.5, 0.5,
                "❌ FAILED TO LOAD\n\nUnable to retrieve image data",
                ha='center', va='center',
                color='#ff6b6b', fontsize=14, fontweight='bold',
                transform=self.image_engine.axes.transAxes
            )
            self.image_engine.axes.set_facecolor('#0a0a0a')
            self.image_engine.axes.axis('off')
            self.image_engine.figure.canvas.draw_idle()
            return
        
        # Update stats
        import numpy as np
        self.update_stats(data)
        
        # Store original RGB data if this is RGB (3 channels)
        if data.ndim == 3 and data.shape[0] == 3:
            self.original_rgb_data = data.copy()
        else:
            # Not RGB, clear the stored original
            self.original_rgb_data = None
        
        # Check if data is displayable (2D or 3D with 3 channels)
        if data.ndim == 1:
            # Show 1D data info
            self.image_engine.axes.clear()
            info = f"📊 1D SPECTRUM DATA\n\n"
            info += f"Length: {data.shape[0]:,} pixels\n"
            info += f"Type: {data.dtype}\n"
            info += f"Range: {data.min():.2f} to {data.max():.2f}\n"
            info += f"Mean: {data.mean():.2f}"
            self.image_engine.axes.text(
                0.5, 0.5, info,
                ha='center', va='center',
                color='#00d4ff', fontsize=12,
                transform=self.image_engine.axes.transAxes
            )
            self.image_engine.axes.set_facecolor('#0a0a0a')
            self.image_engine.axes.axis('off')
            self.image_engine.figure.canvas.draw_idle()
            return
        
        # Display 2D or 3D data using the image engine
        self.image_engine.set_data(data)
        self.image_canvas.draw()
        
        # Update slider ranges
        self.update_slider_ranges()
        
        # Update histogram
        self.histogram_widget.update_histogram(data, 
                                               self.image_engine.vmin, 
                                               self.image_engine.vmax)
        
        # Update colormap status
        self.update_colormap_status()
    
    def update_stats(self, data):
        """Update the statistics text."""
        import numpy as np
        
        stats = f"📊 Data Type: {data.dtype}\n"
        stats += f"📐 Shape: {' × '.join(str(d) for d in data.shape)}\n"
        stats += f"📏 Size: {data.size:,} elements\n"
        stats += f"💾 Memory: {data.nbytes / 1024 / 1024:.2f} MB\n\n"
        stats += f"📈 Statistics:\n"
        stats += f"  Min: {data.min():.4f}\n"
        stats += f"  Max: {data.max():.4f}\n"
        stats += f"  Mean: {data.mean():.4f}\n"
        stats += f"  Std: {data.std():.4f}\n"
        
        if np.issubdtype(data.dtype, np.floating):
            nan_count = np.isnan(data).sum()
            inf_count = np.isinf(data).sum()
            if nan_count > 0 or inf_count > 0:
                stats += f"\n⚠️ Special values:\n"
                if nan_count > 0:
                    stats += f"  NaN: {nan_count:,}\n"
                if inf_count > 0:
                    stats += f"  Inf: {inf_count:,}\n"
        
        # Store the stats text
        self.stats_text = stats
    
    def on_mouse_move(self, event):
        """Handle mouse move event to display cursor information."""
        if event.inaxes and self.image_engine.current_data is not None:
            try:
                x, y = int(event.xdata), int(event.ydata)
                data = self.image_engine.current_data
                
                # Handle different dimensionalities
                if data.ndim == 2:
                    if 0 <= y < data.shape[0] and 0 <= x < data.shape[1]:
                        value = data[y, x]
                        self.statusBar().showMessage(
                            f"📍 X: {x}, Y: {y} | 💡 Value: {value:.2f}"
                        )
                elif data.ndim == 3 and data.shape[0] == 3:
                    # RGB data
                    if 0 <= y < data.shape[1] and 0 <= x < data.shape[2]:
                        r, g, b = data[0, y, x], data[1, y, x], data[2, y, x]
                        self.statusBar().showMessage(
                            f"📍 X: {x}, Y: {y} | 🎨 RGB: ({r}, {g}, {b})"
                        )
            except (IndexError, ValueError):
                pass
    
    def set_scaling_mode_shortcut(self, mode):
        """
        Set scaling mode via keyboard shortcut.
        
        Args:
            mode: Scaling mode ('linear', 'log', 'sqrt', 'asinh')
        """
        self.scaling_combo.setCurrentText(mode)
        self.statusBar().showMessage(f"🔧 Scaling mode: {mode}")
    
    def set_colormap_shortcut(self, colormap):
        """
        Set colormap via keyboard shortcut.
        
        Args:
            colormap: Colormap name
        """
        if self.colormap_combo.isEnabled():
            self.colormap_combo.setCurrentText(colormap)
            self.statusBar().showMessage(f"🎨 Colormap: {colormap}")
        else:
            self.statusBar().showMessage("⚠️ Colormap disabled for RGB images")
    
    def show_keyboard_shortcuts(self):
        """Display keyboard shortcuts dialog."""
        shortcuts_text = """
<h2 style='color: #00d4ff;'>⌨️ Keyboard Shortcuts</h2>

<h3 style='color: #00ff88;'>File Operations</h3>
<table style='color: #e0e0e0;'>
<tr><td><b>Ctrl+O</b></td><td>Open FITS file</td></tr>
<tr><td><b>Ctrl+Q</b></td><td>Exit application</td></tr>
</table>

<h3 style='color: #00ff88;'>View Controls</h3>
<table style='color: #e0e0e0;'>
<tr><td><b>F11</b></td><td>Full screen view</td></tr>
<tr><td><b>ESC</b></td><td>Exit full screen</td></tr>
<tr><td><b>Ctrl++</b></td><td>Zoom in</td></tr>
<tr><td><b>Ctrl+-</b></td><td>Zoom out</td></tr>
<tr><td><b>Ctrl+0</b></td><td>Zoom fit (reset view)</td></tr>
</table>

<h3 style='color: #00ff88;'>Scaling Modes</h3>
<table style='color: #e0e0e0;'>
<tr><td><b>Ctrl+1</b></td><td>Linear scaling</td></tr>
<tr><td><b>Ctrl+2</b></td><td>Log scaling</td></tr>
<tr><td><b>Ctrl+3</b></td><td>Sqrt scaling</td></tr>
<tr><td><b>Ctrl+4</b></td><td>Asinh scaling</td></tr>
<tr><td><b>Ctrl+A</b></td><td>Auto-scale</td></tr>
</table>

<h3 style='color: #00ff88;'>Colormaps</h3>
<table style='color: #e0e0e0;'>
<tr><td><b>Ctrl+G</b></td><td>Gray colormap</td></tr>
<tr><td><b>Ctrl+H</b></td><td>Hot colormap</td></tr>
<tr><td><b>Ctrl+C</b></td><td>Cool colormap</td></tr>
<tr><td><b>Ctrl+V</b></td><td>Viridis colormap</td></tr>
<tr><td><b>Ctrl+I</b></td><td>Invert colormap</td></tr>
</table>

<h3 style='color: #00ff88;'>Help</h3>
<table style='color: #e0e0e0;'>
<tr><td><b>F1</b></td><td>Show keyboard shortcuts</td></tr>
</table>
"""
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Keyboard Shortcuts")
        msg.setTextFormat(Qt.RichText)
        msg.setText(shortcuts_text)
        msg.setStyleSheet("""
            QMessageBox {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a1a2e, stop:1 #0f3460);
            }
            QLabel {
                color: #e0e0e0;
                min-width: 500px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00d4ff, stop:1 #0080ff);
                color: #000000;
                border: none;
                border-radius: 5px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #00ffff;
            }
        """)
        msg.exec_()
    
    def show_about(self):
        """Display about dialog."""
        about_text = """
<h2 style='color: #00d4ff;'>⭐ FITS Viewer</h2>
<h3 style='color: #00ff88;'>Astronomical Data Explorer</h3>

<p style='color: #e0e0e0;'>
<b>Version:</b> 1.0.0<br>
<b>Created by:</b> Andy Kong<br>
<b>Built with:</b> Python, PyQt5, Matplotlib, Astropy<br>
</p>

<p style='color: #e0e0e0;'>
A professional FITS file viewer for astronomical data analysis.
Features include multi-HDU support, advanced scaling modes,
customizable colormaps, and real-time histogram analysis.
</p>

<h3 style='color: #00ff88;'>Features:</h3>
<ul style='color: #e0e0e0;'>
<li>📂 Open and browse FITS files</li>
<li>📊 Multi-HDU navigation</li>
<li>🎨 15+ colormaps with inversion</li>
<li>📈 4 scaling modes (linear, log, sqrt, asinh)</li>
<li>📉 Real-time histogram display</li>
<li>🔍 Interactive zoom and pan</li>
<li>💡 Pixel value inspection</li>
<li>🌈 RGB to grayscale conversion</li>
</ul>

<p style='color: #00d4ff;'>
<b>FITS Format:</b> Flexible Image Transport System<br>
Standard format for astronomical data interchange.
</p>
"""
        
        msg = QMessageBox(self)
        msg.setWindowTitle("About FITS Viewer")
        msg.setTextFormat(Qt.RichText)
        msg.setText(about_text)
        msg.setStyleSheet("""
            QMessageBox {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a1a2e, stop:1 #0f3460);
            }
            QLabel {
                color: #e0e0e0;
                min-width: 500px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00d4ff, stop:1 #0080ff);
                color: #000000;
                border: none;
                border-radius: 5px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #00ffff;
            }
        """)
        msg.exec_()
    
    def show_fullscreen_view(self):
        """Show the FITS image in fullscreen mode."""
        if self.image_engine.current_data is None:
            QMessageBox.information(
                self,
                "No Image",
                "Please open a FITS file first to view in fullscreen."
            )
            return
        
        # Create fullscreen dialog with parent canvas for restoration
        fullscreen_dialog = FullScreenImageDialog(self.image_engine, self.image_canvas, self)
        fullscreen_dialog.exec_()
        
        # After dialog closes, ensure main window canvas is updated
        self.image_canvas.draw()
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Close any open FITS file
        self.fits_manager.close_file()
        event.accept()
