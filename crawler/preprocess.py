from PIL import Image
import glob 
import natsort 
import shutil
from natsort import natsorted
from typing import List , Union, Optional
from pathlib import Path
from io import BytesIO
import requests
import numpy as np
from urllib.parse import quote , urlparse
from .utils import make_dir , save_image_as_jpg
from typing import Tuple

# Define a class to hold processed image segment information
class ProcessedImageSegment:
    def __init__(self, pil_image: Image.Image, original_url: str, segment_index: int, is_text_segment: bool , segment_id: int):
        self.pil_image: Image.Image = pil_image
        self.original_url: str = original_url
        self.segment_index: int = segment_index # Index within the original image
        self.is_text_segment: bool = is_text_segment # True if classified as text (wide)
        self.segment_id: int = segment_id
    def __repr__(self):
        type_str = "Text" if self.is_text_segment else "Image"
        return f"<ProcessedImageSegment original_url='{self.original_url}' index={self.segment_index} type={type_str} size={self.pil_image.size}>"


#TODO : text 이미지로 분류한 분활된 이미지를 가로 세로 비율이 맞을 때 까지 수직으로 이어 붙히는 코드 작성

def is_wide_image(image:Image.Image , threshold_ratio: float = 3.0) -> bool:
    return (image.width / image.height) > threshold_ratio 

# 파일 이동
def move_files(image_paths: Union[List[str], str], output_dirs:str) -> None:
    if isinstance(image_paths, str):
        image_paths = [image_paths]
    file_name = Path(image_paths[0]).name
    output_dir = Path(image_paths[0]).parent / output_dirs 
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    for image_path in image_paths:
        shutil.move(image_path, str(output_dir / file_name))
        # print(f"Moved {filename} to {category} images directory")


def get_pil_image_from_url(url:str)-> Optional[Image.Image]:
    # url 문자열 전처리 
    if url.startswith("//"):
        url = "https:" + url
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # HTTP 에러 발생시 예외 발생
        if response.status_code != 200:
            raise requests.exceptions.HTTPError(f"HTTP {response.status_code}: {response.reason}")
        image_stream = BytesIO(response.content)
        # image_array = np.frombuffer(image_stream.read(), np.uint8)
        pil_image = Image.open(image_stream).convert("RGB")
        return pil_image
    except requests.exceptions.RequestException as e:
        print(f"이미지 다운로드 실패: {url}, 에러: {str(e)}")
        return None


    
def pil_image_show(img:Image.Image , title:str = "image" ):
    if img is not None:
        img.show(title=title) # Add title to show window
    else:
        print("이미지가 없습니다." , type(img))

def is_image_height_enough(image:Image.Image , threshold_height:int = 30)->bool:
    _, height = image.size
    if height < threshold_height:
        return False
    return True


def find_split_points(white_rows: np.ndarray, threshold_height: int = 30) -> List[tuple]:
    """
    연속된 흰색 행을 그룹화하여 분할 지점을 찾습니다.
    
    Args:
        white_rows (np.ndarray): 흰색 밴드의 행 인덱스
        threshold_height (int): 최소 높이 임계값
        
    Returns:
        List[tuple]: 분할 지점 리스트 (시작, 끝)
    """
    split_points = []
    if len(white_rows) > 0:
        current_start = white_rows[0]
        white_height = 0
        for i in range(1, len(white_rows)):
            if white_rows[i] != white_rows[i-1] + 1:
                if white_height > threshold_height:
                    split_points.append((current_start, white_rows[i-1]))
                current_start = white_rows[i]
                white_height = 0
            else:
                white_height += 1
        split_points.append((current_start, white_rows[-1]))
    return split_points

def adjust_split_points(split_points: List[tuple], image_height: int, offset: int = 10) -> List[tuple]:
    """
    분할 지점을 조정하여 최종 분할 영역을 결정합니다.
    
    Args:
        split_points (List[tuple]): 원본 분할 지점
        image_height (int): 이미지 높이
        offset (int): 조정 오프셋
        
    Returns:
        List[tuple]: 조정된 분할 지점
    """
    if not split_points:
        return []
        
    if len(split_points) == 1:
        start, end = split_points[0]
        if start == 0:
            return [(end-offset, image_height)]
        else:
            return [(0, start+offset), (end-offset, image_height)]
    else:
        return [(split_points[i-1][1]-offset, split_points[i][0]+offset) 
                for i in range(1, len(split_points))]

def save_segments(segments: List[ProcessedImageSegment], save_dir:str ,suffix:str="jpg"):
    # Ensure the base directories exist before looping
    make_dir(f"{save_dir}/texts")
    make_dir(f"{save_dir}/images")

    for idx, seg in enumerate(segments):
        image_name = f"segment_{seg.segment_id}_{idx}.{suffix}" 
        if seg.is_text_segment:
            save_path = f"{save_dir}/texts/{image_name}"
        else:
            save_path = f"{save_dir}/images/{image_name}"
        
        save_image_as_jpg(seg.pil_image, save_path) 

 


def split_image_by_white_rows(
    img: Image.Image,
    white_rows: np.ndarray,
    min_white_band: int = 10,
    offset: int = 10 , # 기본 offset 5 픽셀d
    min_image_height:int = 10
) -> List[Image.Image]:
    """
    긴 이미지를 white_rows 기반으로 여러 이미지로 분할 (offset 추가)

    Args:
        img: PIL.Image (원본 이미지)
        white_rows: 각 행이 흰색인지(True)/아닌지(False) 담은 배열
        min_white_band: 무시할 흰색 영역 최소 길이
        offset: crop 시 여백 추가 픽셀 수
    
    Returns:
        분할된 PIL 이미지 리스트
    """
    height, width = img.height, img.width

    # 분할 기준 찾기
    split_points = []
    in_white = False
    start_idx = 0

    for y in range(height):
        if white_rows[y]:
            if not in_white:
                start_idx = y
                in_white = True
        else:
            if in_white:
                end_idx = y
                if end_idx - start_idx >= min_white_band:
                    split_points.append((start_idx, end_idx))
                in_white = False

    # 마지막이 흰색으로 끝나는 경우
    if in_white:
        end_idx = height
        if end_idx - start_idx >= min_white_band:
            split_points.append((start_idx, end_idx))

    # 분할하기
    cropped_images = []
    prev_end = 0
    for start, end in split_points:
        # 이전 검정(콘텐츠) 영역 자르기
        cropped_start = max(prev_end - offset, 0)
        cropped_end = min(start + offset, height)

        if cropped_start < cropped_end and cropped_end-cropped_start >= min_image_height :  # 범위가 정상일 때만 crop
            cropped = img.crop((0, cropped_start, width, cropped_end))
            cropped_images.append(cropped)

        prev_end = end

    # 마지막 남은 부분 추가
    if prev_end < height:
        cropped_start = max(prev_end - offset, 0)
        cropped_end = height
        if cropped_start < cropped_end and cropped_end-cropped_start >= min_image_height:
            cropped = img.crop((0, cropped_start, width, cropped_end))
            cropped_images.append(cropped)

    return cropped_images

def get_white_rows_by_meancount(image:Image.Image ,  mean_threshold, dark_threshold ,dark_threshold_count )->np.ndarray:
    """
    이미지에서 흰색 행을 찾는 함수
    """
    if isinstance(image, str):
        image = Image.open(image)
    image_np = np.asarray(image.copy())
    mean_pixels = image_np[:, :, :3].mean(axis=(1, 2)) > mean_threshold
    dark_pixels = [np.sum(row < dark_threshold) > dark_threshold_count for row in np.mean(image_np, axis=2)]
    final = ~np.array(dark_pixels) & mean_pixels   # Changed from 'not dark_pixels' to '~np.array(dark_pixels)'
    return final

def get_white_rows_by_diff(image_path:Union[str,Image.Image] , log_threshold:float = 1.2)->Tuple[np.ndarray,np.ndarray]:
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
    

    log_max_mean = np.log1p(col_diff_max_mean)
    # col_diff_range = col_diff_max_mean - col_diff_min_mean
    # log_range = np.log1p(col_diff_range)
    
    return np.array(log_max_mean < log_threshold) 

def get_white_rows(image:Image.Image , mean_threshold = 230, dark_threshold = 200 ,dark_threshold_count = 5 )->np.ndarray:
    """
    이미지에서 흰색 행을 찾는 함수
    """
    cond1 = get_white_rows_by_meancount(image , mean_threshold , dark_threshold , dark_threshold_count)
    cond2 = get_white_rows_by_diff(image)
    return cond1 & cond2
    


def image_preprocess(images_url: Union[List[str], str], 
                     is_crop:bool = True,
                     min_white_band: int = 40,
                     crop_offset: int = 10,
                     min_segment_height: int = 10
                     ) -> List[ProcessedImageSegment]:
    """
    Downloads images from URLs, optionally splits them into segments based on white rows,
    and returns a list of ProcessedImageSegment objects containing the PIL images and metadata.

    Args:
        images_url (List[str]): List of image URLs to process.
        is_crop (bool): Whether to crop images into segments. Defaults to True.
        min_white_band (int): Minimum height of a white band to consider for splitting.
        crop_offset (int): Offset pixels to add/subtract when cropping segments.
        min_segment_height (int): Minimum height for a cropped segment to be kept.

    Returns:
        List[ProcessedImageSegment]: A list containing ProcessedImageSegment objects
                                      for each resulting image or segment.
    """
    processed_segments: List[ProcessedImageSegment] = []
    if isinstance(images_url, str):
        images_url = [images_url]
    for idx , url in enumerate(images_url):
        image = get_pil_image_from_url(url)
        if image is None:
            continue

        if is_crop:
            # Detect white rows for potential splitting
            white_rows = get_white_rows(image)
            # Split the image based on detected white rows
            segments = split_image_by_white_rows(
                image, 
                white_rows, 
                min_white_band=min_white_band, 
                offset=crop_offset,
                min_image_height=min_segment_height
            )
            
            # Create ProcessedImageSegment objects for each segment
            for i, seg in enumerate(segments):
                is_text = is_wide_image(seg)
                segment_obj = ProcessedImageSegment(
                    pil_image=seg,
                    original_url=url,
                    segment_index=i,
                    is_text_segment=is_text,
                    segment_id=idx
                )
                processed_segments.append(segment_obj)
        else:
            # If not cropping, treat the whole image as a single segment
            is_text = is_wide_image(image)
            segment_obj = ProcessedImageSegment(
                pil_image=image,
                original_url=url,
                segment_index=0, # Index 0 for the whole image
                is_text_segment=is_text,
                segment_id=idx
            )
            processed_segments.append(segment_obj)
            
    return processed_segments
            
def is_image_height_enough(image:Image.Image , threshold_height:int = 30)->bool:
    _, height = image.size
    if height < threshold_height:
        return False
    return True




