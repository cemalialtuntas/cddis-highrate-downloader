import os
import sys
from pathlib import Path

def get_crx2rnx_path() -> Path:
    """Returns the path to CRX2RNX executable."""
    package_dir = Path(__file__).parent
    
    if sys.platform == "win32":
        exe_name = "CRX2RNX.exe"
    else:
        exe_name = "CRX2RNX"
        
    return package_dir / exe_name

def check_crx2rnx() -> bool:
    """Checks if CRX2RNX is available in the package directory."""
    crx2rnx_path = get_crx2rnx_path()
    if not crx2rnx_path.exists():
        print(f"Error: {crx2rnx_path.name} not found in package directory.")
        return False
        
    # Make executable on Unix-like systems
    if sys.platform != "win32":
        os.chmod(crx2rnx_path, 0o755)
        
    return True 