"""
FITS File Manager

Handles opening, closing, and accessing FITS files using astropy.io.fits.
"""

from typing import Optional, List, Dict
from astropy.io import fits
import numpy as np


class FITSFileManager:
    """Manages FITS file operations using astropy."""
    
    def __init__(self):
        """Initialize the FITS File Manager."""
        self.hdulist: Optional[fits.HDUList] = None
        self.filepath: Optional[str] = None
        self.num_hdus: int = 0
    
    def open_file(self, filepath: str) -> bool:
        """
        Open a FITS file using astropy.io.fits.open().
        
        Args:
            filepath: Path to the FITS file
            
        Returns:
            True on success, False on failure
        """
        try:
            # Close any currently open file
            self.close_file()
            
            # Open the FITS file without memory mapping to avoid file locking issues
            # memmap=False loads the entire file into memory
            self.hdulist = fits.open(filepath, memmap=False)
            self.filepath = filepath
            self.num_hdus = len(self.hdulist)
            
            return True
            
        except IOError as e:
            # File access errors (doesn't exist, no permissions, etc.)
            print(f"IOError: Cannot open file: {str(e)}")
            return False
            
        except fits.VerifyError as e:
            # FITS format errors (malformed file, invalid structure, etc.)
            print(f"VerifyError: Invalid FITS file: {str(e)}")
            return False
            
        except Exception as e:
            # Catch any other unexpected errors
            print(f"Unexpected error opening file: {str(e)}")
            return False
    
    def close_file(self) -> None:
        """Close the currently open FITS file."""
        if self.hdulist is not None:
            self.hdulist.close()
            self.hdulist = None
            self.filepath = None
            self.num_hdus = 0
    
    def get_hdu_list_summary(self) -> List[Dict]:
        """
        Return list of all HDUs with basic info.
        
        Returns:
            List of dictionaries containing HDU metadata
        """
        if self.hdulist is None:
            return []
        
        summary = []
        for i, hdu in enumerate(self.hdulist):
            hdu_info = {
                'index': i,
                'type': type(hdu).__name__,
                'dimensions': hdu.data.shape if hdu.data is not None else None,
                'dtype': str(hdu.data.dtype) if hdu.data is not None else None,
                'has_data': hdu.data is not None,
                'extname': hdu.header.get('EXTNAME', '')
            }
            summary.append(hdu_info)
        
        return summary
    
    def get_hdu_info(self, index: int) -> Dict:
        """
        Return HDU metadata (type, dimensions, data type).
        
        Args:
            index: HDU index
            
        Returns:
            Dictionary with HDU metadata
        """
        if self.hdulist is None or index < 0 or index >= self.num_hdus:
            return {}
        
        hdu = self.hdulist[index]
        
        return {
            'index': index,
            'type': type(hdu).__name__,
            'dimensions': hdu.data.shape if hdu.data is not None else None,
            'dtype': str(hdu.data.dtype) if hdu.data is not None else None,
            'has_data': hdu.data is not None,
            'extname': hdu.header.get('EXTNAME', '')
        }
    
    def get_header(self, index: int) -> str:
        """
        Return formatted header string for HDU.
        
        Args:
            index: HDU index
            
        Returns:
            Formatted header string
        """
        if self.hdulist is None or index < 0 or index >= self.num_hdus:
            return ""
        
        hdu = self.hdulist[index]
        return str(hdu.header)
    
    def get_data(self, index: int) -> Optional[np.ndarray]:
        """
        Return data array for HDU.
        
        Args:
            index: HDU index
            
        Returns:
            Numpy array with data, or None if no data
        """
        if self.hdulist is None or index < 0 or index >= self.num_hdus:
            return None
        
        hdu = self.hdulist[index]
        return hdu.data
