import _path_utils
import numpy as np
from PIL import Image 
from crawler.visualize.utils import visualize_log_transform , get_white_rows_by_diff , draw_points
from crawler.preprocess import get_white_rows , get_white_rows_by_meancount, get_white_rows_by_diff
from pathlib import Path



if __name__ == "__main__":
    
    image_path = "./test/test_orgin_image_3076224_3.jpg"
    image = Image.open(image_path)
    cond1 = get_white_rows_by_meancount(image , mean_threshold = 230, dark_threshold = 200 ,dark_threshold_count = 5 )
    cond2 = get_white_rows_by_diff(image)
    # visualize_log_transform(results)
    cond1_cond2 = get_white_rows(image)
    point1 = [((image.width//2)//2 , idx) for idx , i in enumerate(cond1) if i ]
    point2 = [((image.width//2) , idx) for idx , i in enumerate(cond2) if i ]
    point3 = [((image.width//2) + ((image.width//2)//2) , idx) for idx , i in enumerate(cond1_cond2) if i ]
    draw_points(image , point1  , color=(255,255,0))
    draw_points(image , point2  , color=(0,255,0))
    draw_points(image , point3  , color=(0,0,255))
    image.save(f"./split_function_test_1_.jpg")
    