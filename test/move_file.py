import _path_utils
from pathlib import Path 
from crawler.utils import move_file , move_directory
import glob

# src_files = glob.glob("./test/*.jpg")
src_dir = Path("./test/images")
dst_dir = Path("./")
move_directory(src_dir, dst_dir)


