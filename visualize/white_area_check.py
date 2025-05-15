import _path_utils
import numpy as np
from PIL import Image 
from crawler.preprocess import get_white_rows , get_white_rows_by_meancount, get_white_rows_by_diff
from pathlib import Path
from crawler.visualize.utils import get_rows_diff , visualize_log_transform , draw_points



if __name__ == "__main__":
    
    image_path = "./2.jpg"
    image = Image.open(image_path)
    cond1 = get_white_rows_by_meancount(image , mean_threshold = 240, dark_threshold = 220 ,dark_threshold_count = 5 )
    cond2 = get_white_rows_by_diff(image,log_threshold=2.1)
    # visualize_log_transform(results)
    cond3 = cond1 & cond2
    point1 = [((image.width//2)//2 , idx) for idx , i in enumerate(cond1) if i ]
    point2 = [((image.width//2) , idx) for idx , i in enumerate(cond2) if i ]
    point3 = [((image.width//2) + ((image.width//2)//2) , idx) for idx , i in enumerate(cond3) if i ]
    
    draw_points(image , point1  , color=(255,255,0))
    draw_points(image , point2  , color=(0,255,0))
    draw_points(image , point3  , color=(0,0,255))
    image.save(f"./split_function_test_1_.jpg")
    
    
    # value =get_rows_diff(image_path)
    # visualize_log_transform(value)
    