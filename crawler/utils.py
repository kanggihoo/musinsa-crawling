from PIL import Image , ImageDraw
import numpy as np
import requests
from io import BytesIO
from pathlib import Path
from typing import List , Dict , Optional , Tuple 
import pandas as pd

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
    
def draw_points(img, points, color=(255, 0, 0)):
    draw = ImageDraw.Draw(img)
    for point in points:
        draw.ellipse((point[0] - 3, point[1] - 3, point[0] + 3, point[1] + 3), fill=color)
    return img

def make_dir(dir_path:str)->None:
    if not Path(dir_path).exists():
        Path(dir_path).mkdir(parents=True)



def add_data_to_dataframe(data:List[Dict], df:pd.DataFrame):
    result_df = pd.concat([df , pd.DataFrame(data)])
    return result_df

def save_dataframe_to_csv(df:pd.DataFrame , csv_path:str, index_column:Optional[str]=None):
    if index_column is not None:
        if index_column not in df.columns:
            raise ValueError(f"dataframe 내에 {index_column} 열이 존재하지 않음")
        df_to_save = df.set_index(index_column)
        df_to_save.to_csv(csv_path)
    else:
        df.to_csv(csv_path , index=True)
def load_dataframe_from_csv(csv_path:str)->pd.DataFrame:
    return pd.read_csv(csv_path,encoding="utf-8")


