from pathlib import Path
import sys

# Add project root directory to Python path
parent_dir = Path(__file__).parent.parent
if parent_dir not in sys.path:
    sys.path.append(str(parent_dir) )