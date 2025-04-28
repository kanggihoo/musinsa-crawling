from PIL import Image
import glob 
import natsort 
import shutil
from natsort import natsorted
from typing import List , Union
from pathlib import Path
from io import BytesIO
import requests
import numpy as np
from urllib.parse import quote , urlparse
from .utils import make_dir



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


def get_pil_image_from_url(url:str)->np.ndarray:
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
        image_array = np.frombuffer(image_stream.read(), np.uint8)
        img = Image.open(image_stream).convert("RGB")
        return img
    except requests.exceptions.RequestException as e:
        print(f"이미지 다운로드 실패: {url}, 에러: {str(e)}")
        return None

def save_image_as_jpg(image: Image.Image, save_path: str) -> None:
    """
    Safely save a PIL image to JPG format regardless of its original mode
    
    Args:
        image (PIL.Image.Image): PIL Image object to save
        save_path (str): Path where to save the JPG file
    """
    # Create a copy to avoid modifying the original image
    img_to_save = image.copy()
    
    # Convert RGBA images to RGB
    if img_to_save.mode == 'RGBA':
        # Create white background
        background = Image.new('RGB', img_to_save.size, (255, 255, 255))
        # Paste using alpha channel as mask
        background.paste(img_to_save, mask=img_to_save.split()[3])
        img_to_save = background
    # Convert P (palette) mode to RGB
    elif img_to_save.mode == 'P':
        img_to_save = img_to_save.convert('RGB')
    # Convert LA (grayscale with alpha) to RGB
    elif img_to_save.mode == 'LA':
        background = Image.new('RGB', img_to_save.size, (255, 255, 255))
        background.paste(img_to_save, mask=img_to_save.split()[1])
        img_to_save = background
    # Convert L (grayscale) to RGB
    elif img_to_save.mode == 'L':
        img_to_save = img_to_save.convert('RGB')
    
    # Save the image
    img_to_save.save(save_path, 'JPEG', quality=95)



def get_pil_image_from_url(url:str)->Image.Image:
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
        pil_image = Image.open(image_stream).convert("RGB")
        return pil_image
    except requests.exceptions.RequestException as e:
        print(f"이미지 다운로드 실패: {url}, 에러: {str(e)}")
        return None
    
def pil_image_show(img:Image.Image , title:str = "image" ):
    if img is not None:
        img.show()
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

def save_segments(segments: List[Image.Image], save_dir:str ,suffix:str="jpg", **kwargs):
    file_num = kwargs.get("file_num", 1)
    for i, seg in enumerate(segments):  
        image_name = f"split_segment_{file_num}_{i+1}.{suffix}"
        if is_wide_image(seg):
            save_image_as_jpg(seg, f"{save_dir}/texts/{image_name}")
        else:
            save_image_as_jpg(seg, f"{save_dir}/images/{image_name}")

 
        
    
def split_image_by_white_rows(
    img: Image.Image,
    white_rows: np.ndarray,
    min_white_band: int = 10,
    offset: int = 10 , # 기본 offset 5 픽셀d
    min_image_height:int = 15
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

def image_preprocess(images_url: List[str], 
                     is_crop:bool = True ,
                     is_save:bool = True ,
                     save_dir:str = "./data" ,
                     save_single_dir:bool = False,
                     suffix:str = "jpg"
                     ):
    if is_save and not is_crop:
        make_dir(f"{save_dir}/images")
    if is_save and is_crop:
        make_dir(f"{save_dir}/images")
        make_dir(f"{save_dir}/texts")
        

    file_num = 1
    for idx in range(len(images_url)):
        image = get_pil_image_from_url(images_url[idx])
       
        if is_crop:
            
            image_np = np.asarray(image.copy())

            # 흰색 밴드 감지 (최적화된 버전)
            mean_threshold = 220
            dark_threshold = 200
            dark_threshold_count = 5
            
            # 방법 1: 흰색이 아닌 픽셀 수 계산
            # RGB 채널별로 한 번에 처리
            # 행별로 모든 픽셀이 흰색인지 확인 (axis 1은 너비, axis 2는 채널)
            white = image_np[:, :, :3].mean(axis=(1, 2)) > mean_threshold
            dark_pixels = [np.sum(row < dark_threshold) > dark_threshold_count for row in np.mean(image_np, axis=2)]
            final = ~np.array(dark_pixels) & white  # Changed from 'not dark_pixels' to '~np.array(dark_pixels)'
            
            
            segments = split_image_by_white_rows(image , final, min_white_band=40)
            # # 세그먼트 저장
            if is_save:
                save_segments(segments, save_dir = save_dir, file_num=file_num ,save_single_dir=save_single_dir)
                file_num += 1
        else:
            if is_save:
                save_path = f"{save_dir}/images/summary_{idx}.{suffix}"
                save_image_as_jpg(image, save_path)
                 
            
def is_image_height_enough(image:Image.Image , threshold_height:int = 30)->bool:
    _, height = image.size
    if height < threshold_height:
        return False
    return True


# move_files(text_images, "text")
# move_files(cloth_images, "cloth")






