from PIL import Image , ImageOps
import numpy as np
import requests
from io import BytesIO
from pathlib import Path
from typing import List , Dict , Optional , Tuple 
import pandas as pd
import os
import logging


# 로그 설정
def set_error_logger(name:str , file_path: str ):
    """
    """
    # 로거 인스턴스를 가져옵니다. 고정된 이름을 사용하여 항상 동일한 로거를 사용합니다.
    logger = logging.getLogger(name)
    logger.setLevel(logging.ERROR)  
    file_path = Path(file_path)
    file_name = file_path.name
    if not file_path.exists():
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] : %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 파일 저장을 위한 FileHandler 설정 (ERROR 레벨 이상)
    file_handler = logging.FileHandler(file_path, mode="a" ,  encoding='utf-8')
    file_handler.setLevel(logging.ERROR)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

def concat_images_horizontally_centered(images):
    # images: PIL.Image 리스트

    # 각 이미지 크기 확인
    widths, heights = zip(*(img.size for img in images))
    
    # 전체 가로폭 = 모든 이미지의 가로폭 합
    total_width = sum(widths)
    
    # 최대 세로폭 = 가장 높은 이미지의 높이
    max_height = max(heights)
    
    # 새 캔버스 생성 (흰색 배경)
    new_image = Image.new('RGB', (total_width, max_height), (255, 255, 255))
    
    # 이미지 하나씩 붙이기
    x_offset = 0
    for img in images:
        w, h = img.size
        # y_offset을 계산: (최대 높이 - 이미지 높이) // 2
        y_offset = (max_height - h) // 2
        new_image.paste(img, (x_offset, y_offset))
        x_offset += w
    
    return new_image

def concat_images_vertically(images):
    widths = [img.width for img in images]
    heights = [img.height for img in images]

    max_width = max(widths)
    total_height = sum(heights)

    new_img = Image.new('RGB', (max_width, total_height))

    y_offset = 0
    for img in images:
        new_img.paste(img, (0, y_offset))
        y_offset += img.height

    return new_img

def pil_to_numpy(pil_image:Image.Image) -> np.ndarray:
    return np.array(pil_image)
def numpy_to_pil(np_image:np.ndarray)->Image.Image:
    return Image.fromarray(np_image)

def pil_image_show(img:Image.Image , title:str = "image" ):
    if img is not None:
        img.show()
    else:
        print("이미지가 없습니다." , type(img))

def is_wide_image(image:Image.Image , threshold_ratio: float = 3.0) -> bool:
    width, height = image.size
    return width / height > threshold_ratio


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
        pil_image = Image.open(image_stream)
        # 원본 모드 유지하면서 필요한 경우에만 변환
        if pil_image.mode in ['RGBA', 'LA']:
            # 알파 채널이 있는 경우 유지
            return pil_image
        elif pil_image.mode == 'P':
            # 팔레트 이미지의 경우 원본 색상 유지하며 변환
            return pil_image.convert('RGBA' if 'transparency' in pil_image.info else 'RGB')
        elif pil_image.mode == 'CMYK':
            # CMYK는 RGB로 변환 필요
            return pil_image.convert('RGB')
        else:
            # 그 외의 경우 원본 유지
            return pil_image
    
    except requests.exceptions.RequestException as e:
        print(f"이미지 다운로드 실패: {url}, 에러: {str(e)}")
        return None
    

def make_dir(dir_path:str)->None:
    if not Path(dir_path).exists():
        Path(dir_path).mkdir(parents=True)



#FIXME : 여기에 들어오는 data가 기존의 df와 동일하다는 보장이 없음
def add_data_to_dataframe(df: pd.DataFrame, data_list: List[Dict]) -> pd.DataFrame:
    """
    주어진 데이터프레임에 새로운 데이터 목록을 추가합니다.
    
    Args:
        df (pd.DataFrame): 원본 데이터프레임
        data_list (List[Dict]): 추가할 데이터 목록 (각 딕셔너리는 행을 나타냄)
        
    Returns:
        pd.DataFrame: 데이터가 추가된 새로운 데이터프레임
    """
    if not data_list:
        return df
    
    new_df = pd.DataFrame(data_list)
    return pd.concat([df, new_df], ignore_index=True)

def save_dataframe_to_csv(df: pd.DataFrame, file_path: Path, mode: str = 'w'):
    """
    데이터프레임을 CSV 파일로 저장합니다.
    
    Args:
        df (pd.DataFrame): 저장할 데이터프레임
        file_path (Path): 저장할 파일 경로
        index_column (str, optional): 인덱스로 사용할 컬럼명. Defaults to None.
        mode (str, optional): 파일 쓰기 모드 ('w' for write, 'a' for append). Defaults to 'w'.
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)

        
    df.to_csv(file_path, mode=mode, index=False, encoding='utf-8-sig')
    # print(f"데이터프레임을 '{file_path}'에 저장했습니다.")

def load_dataframe_from_csv(csv_path:str)->pd.DataFrame:
    return pd.read_csv(csv_path,encoding="utf-8")

#FIXME : 이미지 저장하는 코드 왜케 지저분 해보이지 
def save_image_as_jpg(image: Image.Image, save_path: str|Path, target_size: int = None) -> None:
    """
    원본 이미지의 비율은 유지하면서 가장 긴 변을 target_size로 고정 
    Args:
        image (PIL.Image.Image): PIL Image object to save
        save_path (str): Path where to save the JPG file
        target_size (tuple, optional): Target size (width, height) for resizing with padding
    """
    
    #Convert RGBA images to RGB
    if image.mode == 'RGBA':
        # Create white background
        background = Image.new('RGB', image.size, (255, 255, 255))
        # Paste using alpha channel as mask
        background.paste(image, mask=image.split()[3])
        image = background
    # Convert P (palette) mode to RGB
    elif image.mode == 'P':
        image = image.convert('RGB')
    # Convert LA (grayscale with alpha) to RGB
    elif image.mode == 'LA':
        background = Image.new('RGB', image.size, (255, 255, 255))
        background.paste(image, mask=image.split()[1])
        image = background
    # Convert L (grayscale) to RGB
    elif image.mode == 'L':
        image = image.convert('RGB')
    
    # Apply target_size with padding if specified
    if target_size is not None:
        image.thumbnail((target_size , target_size) , Image.LANCZOS)
        
    
    # Save the image
    try:
        image.save(save_path, 'JPEG', quality=95)   
    except Exception as e:
        image.save(save_path)
