import numpy as np
from PIL import Image 
from ..preprocess import find_split_points_by_diff
from .utils import visualize_log_transform , get_white_rows_by_diff
from pathlib import Path



if __name__ == "__main__":
    
    # image_path = "./test/test_orgin_image_8_4385261_0.jpg"
    image_path = "./t5.jpg"
    image = Image.open(image_path)
    # results = find_split_points_by_diff(image_path)
    # width , height = image.size
    # if len(results) == 2:
    #     col_diff_min_mean , col_diff_max_mean = results[0]
    #     log_max_mean , log_range = results[1]
    #     points1 = [((width//2)//2 , idx) for idx , i in enumerate(log_max_mean) if i< 1 ]
        
    #     visualize_log_transform(results)
    #     # final = get_white_rows(image)
    #     # points2 = [((width//2)//2 , idx) for idx , i in enumerate(final) if i ]
        
    # else:
    #     col_diff_min_mean , col_diff_max_mean = results
    # draw_points(image , points1)
    # # draw_points(image , points2 , color=(0,255,0))
    # image.save(f"./split_function_test_1_.jpg")
      