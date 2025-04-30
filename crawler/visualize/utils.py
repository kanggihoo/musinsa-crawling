from PIL import Image , ImageDraw
import numpy as np
from typing import Tuple,Union
import matplotlib.pyplot as plt
from typing import List

def draw_points(img, points, color=(255, 0, 0)):
    draw = ImageDraw.Draw(img)
    for point in points:
        draw.ellipse((point[0] - 3, point[1] - 3, point[0] + 3, point[1] + 3), fill=color)
    return img

def get_white_rows_by_diff(image_path:Union[str,Image.Image],log_transform:bool=True)->Tuple[np.ndarray,np.ndarray]:
    """
    각 열의 차이를 계산(절대값 적용)하고 정렬하여 전체 열의 0.05 크기만큼 샘플링하여 최소값과 최대값의 평균을 계산
    log_transform = True일 경우 로그 변환 적용하여 앞에 구한 각 열의 최대 평균의 로그 값과, 최대 최소의 차이의 로그 값을 반환
    """
    if isinstance(image_path, str):
    # 이미지 로드
        img = Image.open(image_path)
    elif isinstance(image_path, np.ndarray):
        img = Image.fromarray(image_path)
    else:
        img = image_path
    gray = img.convert("L")
    gray_np = np.array(gray)
    # 각 행 간의 차이 계산
    col_diff = abs(np.diff(gray_np.astype(np.int16), axis=1))
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
        plt.scatter(np.arange(len(col_diff_min_mean)), col_diff_min_mean, c="red", s=2, label="Min Horizontal Diff (Original)")
        plt.scatter(np.arange(len(col_diff_max_mean)), col_diff_max_mean, c="blue", s=2, label="Max Horizontal Diff (Original)")
        # plt.plot(np.arange(len(col_diff_range)), col_diff_range, c="green", label="Range (Max - Min, Original)")
        plt.ylabel("Pixel Difference Value (Original)")
        plt.title("Original Horizontal Difference Metrics per Row")
        plt.legend()
        plt.grid(True)

        # 두 번째 서브플롯: 로그 변환 값 그래프
        plt.subplot(2, 1, 2) # 2행 1열의 두 번째 플롯
        plt.scatter(np.arange(len(log_max_mean)), log_max_mean, c="blue", label="Max Horizontal Diff (Log Transformed)")
        plt.scatter(np.arange(len(log_range)), log_range, c="green", label="Range (Max - Min, Log Transformed)")

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