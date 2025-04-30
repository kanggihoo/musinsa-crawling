import _path_utils
from crawler.preprocess import split_image_by_white_rows
from crawler.utils import draw_points
from typing import List , Tuple
import numpy as np
import cv2
from PIL import Image
import matplotlib.pyplot as plt
from crawler.preprocess import get_white_rows
from tqdm import tqdm

def find_split_points_by_diff(image_path , log_transform:bool=True):
    """
    각 열의 차이를 계산(절대값 적용)하고 정렬하여 전체 열의 0.05 크기만큼 샘플링하여 최소값과 최대값의 평균을 계산
    log_transform = True일 경우 로그 변환 적용하여 앞에 구한 각 열의 최대 평균의 로그 값과, 최대 최소의 차이의 로그 값을 반환
    """
    
    # 이미지 로드
    img = Image.open(image_path)
    gray = img.convert("L")
    gray_np = np.array(gray)
    
    # 각 행 간의 차이 계산
    col_diff = abs(np.diff(gray_np.astype(np.int16)[:,40:-40], axis=1))
    col_diff_sort = np.sort(col_diff, axis=1)
    # sample_interval = int(img.width*0.025)
    # print(sample_interval)
    col_diff_min_mean , col_diff_max_mean = col_diff_sort[:,:10].mean(axis=1) , col_diff_sort[:,-4:].mean(axis=1)
    

    col_diff_range = col_diff_max_mean - col_diff_min_mean
    log_max_mean = np.log1p(col_diff_max_mean)
    log_range = np.log1p(col_diff_range)
    
    if log_transform:
        return (col_diff_min_mean , col_diff_max_mean) , (log_max_mean , log_range)
    else:
        return (col_diff_min_mean , col_diff_max_mean)
    

def visualize_log_transform(values:List[Tuple[np.ndarray , np.ndarray]]):
    if len(values) != 2:
       raise ValueError("값의 길이가 2이상 길이: " , len(values))
   
    if len(values) == 1:
        col_diff_min_mean , col_diff_max_mean = values[0]
    else:
        col_diff_min_mean , col_diff_max_mean = values[0]
        log_max_mean , log_range = values[1]
    if len(values) == 1:
        plt.figure(figsize=(12, 8))
        plt.scatter(np.arange(len(col_diff_min_mean)), col_diff_min_mean, c="red", s=5, label="Min Horizontal Diff (Original)")
        plt.scatter(np.arange(len(col_diff_max_mean)), col_diff_max_mean, c="blue", s=5, label="Max Horizontal Diff (Original)")
        plt.ylabel("Pixel Difference Value (Original)")
        plt.title("Original Horizontal Difference Metrics per Row")
        plt.legend()
        plt.grid(True)
        plt.tight_layout() # 그래프 간 간격 조정
        plt.show()
    
    if len(values) == 2:
        plt.figure(figsize=(12, 8))
        # 첫 번째 서브플롯: 원본 값 그래프
        plt.subplot(2, 1, 1) # 2행 1열의 첫 번째 플롯
        plt.scatter(np.arange(len(col_diff_min_mean)), col_diff_min_mean, c="red", s=5, label="Min Horizontal Diff (Original)")
        plt.scatter(np.arange(len(col_diff_max_mean)), col_diff_max_mean, c="blue", s=5, label="Max Horizontal Diff (Original)")
        # plt.plot(np.arange(len(col_diff_range)), col_diff_range, c="green", label="Range (Max - Min, Original)")
        plt.ylabel("Pixel Difference Value (Original)")
        plt.title("Original Horizontal Difference Metrics per Row")
        plt.legend()
        plt.grid(True)

        # 두 번째 서브플롯: 로그 변환 값 그래프
        plt.subplot(2, 1, 2) # 2행 1열의 두 번째 플롯
        plt.plot(np.arange(len(log_max_mean)), log_max_mean, c="blue", label="Max Horizontal Diff (Log Transformed)")
        plt.plot(np.arange(len(log_range)), log_range, c="green", label="Range (Max - Min, Log Transformed)")

    # 사용자 분의 원래 의도에 맞춰 Range 그래프를 더 강조해볼 수도 있습니다.
    # 또는 Max Mean 그래프가 콘텐츠 탐지에 더 유용할 수 있으므로 둘 다 그리거나 선택합니다.
    # plt.plot(np.arange(len(log_max_mean)), log_max_mean, c="blue", label="Max Diff (Log Transformed)")
    # plt.plot(np.arange(len(log_range)), log_range, c="green", linestyle='--', label="Range (Log Transformed)")
        plt.xlabel("Row Index")
        plt.ylabel("Log(1 + Value)")
        plt.title("Log Transformed Horizontal Difference Metrics per Row")
        plt.legend()
        plt.grid(True)

        plt.tight_layout() # 그래프 간 간격 조정
        plt.show()
    



if __name__ == "__main__":
    from pathlib import Path
    import glob
    image_paths = glob.glob("./test/test_orgin_image_*.jpg")
    product_ids = [Path(image_path).stem.split("_")[-2] for image_path in image_paths]
    for idx , image_path in tqdm(enumerate(image_paths)):
        product_id = product_ids[idx]
        index = Path(image_path).stem.split("_")[-1]
        image = Image.open(image_path)
        results = find_split_points_by_diff(image_path)
        width , height = image.size
        if len(results) == 2:
            col_diff_min_mean , col_diff_max_mean = results[0]
            log_max_mean , log_range = results[1]
            points1 = [(width//2 , idx) for idx , i in enumerate(log_max_mean) if i< 1 ]
            
            # 새로운 방식
            # points2 = [((width//2)//2 , idx) for idx , i in enumerate(log_range) if i<0.8 ]

            # visualize_log_transform(results)
            
            # 이전방식
            final = get_white_rows(image)
            points2 = [((width//2)//2 , idx) for idx , i in enumerate(final) if i ]
            
        else:
            col_diff_min_mean , col_diff_max_mean = results
        draw_points(image , points1)
        draw_points(image , points2 , color=(0,0,255))
        image.save(f"./split_function_test_{product_ids[idx]}_{index}.jpg")
      
