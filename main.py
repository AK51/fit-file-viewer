"""
FITS Viewer - Main Application Entry Point

A Python-based FITS file viewer for astronomy.
"""

import sys
from PyQt5.QtWidgets import QApplication
from src.main_window import MainWindow


def main():
    """Main application entry point."""
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("FITS Viewer")
    app.setOrganizationName("FITS Viewer Team")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Check if a file path was provided as command-line argument
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        window.open_file(filepath)
    
    # Run application event loop
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
