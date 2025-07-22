import os
from pathlib import Path
import shutil
from PIL import Image
import numpy as np
from natsort import natsorted
from collections import defaultdict
from io import BytesIO
import requests
import logging
from urllib.parse import quote , urlparse
from dataclasses import dataclass , field
import asyncio
import aiohttp
from .utils import make_dir , save_image_as_jpg , set_error_logger
from typing import Tuple

logger = logging.getLogger(__name__)
logger_error = set_error_logger(__name__+".error" , "logs/images_split.log")
# Define a class to hold processed image segment information
@dataclass
class ImageMetadata:
    pil_image: Image.Image
    image_idx: int
    segment_idx: int|None = None    
    is_text_segment: bool|None = None
    
    # def __repr__(self):
    #     type_str = "Text" if self.is_text_segment else "Image"
    #     return f"<ProcessedImageSegment original_url='{self.original_url}' index={self.segment_index} type={type_str} size={self.pil_image.size}>"

@dataclass
class ImageData:
    product_id : str
    summary_images_url : list[str]
    detail_images_url : list[str]
    category_main : str
    category_sub : str
    image_suffix : str = "jpg"
    detail_images : list[ImageMetadata]= field(default_factory=list)
    segmented_img : list[ImageMetadata]= field(default_factory=list)
    target_size : int = 512
    
    def __post_init__(self):
        self.HOME_DIR = Path(__file__).parent.parent
        self.BASE_DIR = self.HOME_DIR / str(self.category_main) / str(self.category_sub) / str(self.product_id)
        
        self.SUMMARY_IMAGE_DIR = self.BASE_DIR / "summary"
        self.DETAIL_IMAGE_DIR = self.BASE_DIR / "detail"
        self.SEGMENT_IMAGE_DIR = self.BASE_DIR / "segment"
        self.TEXT_IMAGE_DIR = self.BASE_DIR / "text"

    async def create_all_directories(self) :
        await asyncio.gather(
            self._create_single_directory_async(self.SUMMARY_IMAGE_DIR),
            self._create_single_directory_async(self.DETAIL_IMAGE_DIR),
            self._create_single_directory_async(self.SEGMENT_IMAGE_DIR),
            self._create_single_directory_async(self.TEXT_IMAGE_DIR)
        )
    
    async def _create_single_directory_async(self, path: Path):
        """단일 디렉토리를 비동기적으로 생성"""
        await asyncio.to_thread(self._create_single_directory, path)
    
    def _create_single_directory(self, path: Path):
        """단일 디렉토리를 동기적으로 생성"""
        path.mkdir(parents=True, exist_ok=True)
        
        

    

def is_wide_image(image:Image.Image , threshold_ratio: float = 8.0) -> bool:
    
    return (image.width / image.height) > threshold_ratio 

# 파일 이동
def move_files(image_paths: list[str]| str, output_dirs:str) -> None:
    if isinstance(image_paths, str):
        image_paths = [image_paths]
    file_name = Path(image_paths[0]).name
    output_dir = Path(image_paths[0]).parent / output_dirs 
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    for image_path in image_paths:
        shutil.move(image_path, str(output_dir / file_name))
        # print(f"Moved {filename} to {category} images directory")

# FIXME : 여기 부분 비동기 처리로??
# def get_pil_image_from_url(url:str)-> Image.Image | None:
#     # url 문자열 전처리 
#     if url.startswith("//"):
#         url = "https:" + url
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
#     }
    
#     try:
#         response = requests.get(url, headers=headers, timeout=10)
#         response.raise_for_status()  # HTTP 에러 발생시 예외 발생
#         if response.status_code != 200:
#             raise requests.exceptions.HTTPError(f"HTTP {response.status_code}: {response.reason}")
#         image_stream = BytesIO(response.content)
#         # image_array = np.frombuffer(image_stream.read(), np.uint8)
#         pil_image = Image.open(image_stream).convert("RGB")
#         return pil_image
#     except requests.exceptions.RequestException as e:
#         print(f"이미지 다운로드 실패: {url}, 에러: {str(e)}")
#         return None


# def save_image_from_url(url: str, save_path: str) -> bool:
#     """
#     URL에서 이미지를 다운로드하여 지정된 경로에 저장합니다.
#     """
#     # url 문자열 전처리 
#     if url.startswith("//"):
#         url = "https:" + url
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
#     }
    
#     try:
#         response = requests.get(url, headers=headers, timeout=10)
#         response.raise_for_status()  # HTTP 에러 발생시 예외 발생
#         if response.status_code != 200:
#             raise requests.exceptions.HTTPError(f"HTTP {response.status_code}: {response.reason}")
        
#         # 이미지를 PIL Image로 변환 후 저장
#         image_stream = BytesIO(response.content)
#         pil_image = Image.open(image_stream).convert("RGB")
#         pil_image.save(save_path, "JPEG", quality=95)
#         return True
        
#     except Exception as e:
#         print(f"이미지 다운로드 실패: {url}, 에러: {str(e)}")
#         return False

async def get_pil_image_from_url_async(session: aiohttp.ClientSession, url: str , headers:dict) -> Image.Image | None:
    """
    Asynchronously downloads an image from a URL and returns a PIL image object.
    """
    if url.startswith("//"):
        url = "https:" + url
    try:
        async with session.get(url, headers=headers, timeout=30) as response:
            response.raise_for_status()
            content = await response.read()
            image_stream = BytesIO(content)
            pil_image = Image.open(image_stream).convert("RGB")
            return pil_image
    except Exception as e:
        logger_error.error(f"Async 이미지 다운로드 실패 : {url} , 에러: {str(e)}")
        return None
    
async def _download_images_async(image_urls:list[str])->list[Image.Image | None]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
    }
    async with aiohttp.ClientSession() as session:
        tasks = [get_pil_image_from_url_async(session, url, headers) for url in image_urls]
        return await asyncio.gather(*tasks)

async def save_summary_images_async(
   process:ImageData,
) -> tuple[int, int]:
    
    urls=process.summary_images_url
    save_dir=process.SUMMARY_IMAGE_DIR
    image_suffix=process.image_suffix
    product_id=process.product_id

    total_images = len(urls)
    downloaded_images = await _download_images_async(urls)
    success_count = sum(1 for img in downloaded_images if img is not None)

    for idx, image in enumerate(downloaded_images):
        if image is None:
            continue
        save_path = os.path.join(save_dir, f"{idx}.{image_suffix}")
        save_image_as_jpg(image, save_path , process.target_size)
    
    error_count = total_images - success_count
    if error_count > 0:
        logger.error(
            f"{product_id} summary Image download completed. "
            f"Total: {total_images}, Success: {success_count}, Failed: {error_count}"
        )
    else:
        logger.info(f"{product_id} summary Image download completed. Total: {total_images} ")
    return success_count, error_count

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


def find_split_points(white_rows: np.ndarray, threshold_height: int = 30) -> list[tuple]:
    """
    연속된 흰색 행을 그룹화하여 분할 지점을 찾습니다.
    
    Args:
        white_rows (np.ndarray): 흰색 밴드의 행 인덱스
        threshold_height (int): 최소 높이 임계값
        
    Returns:
        list[tuple]: 분할 지점 리스트 (시작, 끝)
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

def adjust_split_points(split_points: list[tuple], image_height: int, offset: int = 10) -> list[tuple]:
    """
    분할 지점을 조정하여 최종 분할 영역을 결정합니다.
    
    Args:
        split_points (list[tuple]): 원본 분할 지점
        image_height (int): 이미지 높이
        offset (int): 조정 오프셋
        
    Returns:
        list[tuple]: 조정된 분할 지점
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

def find_content_regions(white_rows):
    """컨텐츠(비흰색) 영역의 시작점과 끝점을 찾는 함수"""
    height = len(white_rows)
    content_regions = []
    
    i = 0
    while i < height:
        # 컨텐츠 영역 시작점 찾기
        if not white_rows[i]:
            start = i
            # 컨텐츠 영역 끝점 찾기
            while i < height and not white_rows[i]:
                i += 1
            end = i - 1
            content_regions.append((start, end))
        else:
            i += 1
    
    return content_regions

def process_content_regions(content_regions, image_height, min_content_height, min_white_gap, padding=10):
    """
    컨텐츠 영역을 처리하는 함수
    - 너무 작은 컨텐츠 영역은 노이즈로 제거
    - 너무 가까운 컨텐츠 영역은 병합
    - 적절한 여백 추가
    
    Parameters:
    - content_regions: 원본 컨텐츠 영역 리스트 [(시작행, 끝행), ...]
    - image_height: 전체 이미지 높이
    - min_content_height: 유효한 컨텐츠로 간주할 최소 높이
    - min_white_gap: 컨텐츠 영역을 분리하기 위한 최소 흰색 영역 높이
    - padding: 각 분할 영역에 추가할 상하 여백
    
    Returns:
    - 최종 분할 영역 리스트 [(시작행, 끝행), ...]
    """
    if not content_regions:
        return [(0, image_height-1)]
    
    # 1. 너무 작은 컨텐츠 영역 제거 (노이즈 제거)
    valid_regions = []
    for start, end in content_regions:
        if end - start + 1 >= min_content_height:
            valid_regions.append((start, end))
    
    if not valid_regions:
        return [(0, image_height-1)]
    
    # 2. 가까운 컨텐츠 영역 병합
    merged_regions = []
    current_start, current_end = valid_regions[0]
    
    for i in range(1, len(valid_regions)):
        next_start, next_end = valid_regions[i]
        
        # 두 컨텐츠 영역 사이의 흰색 영역 길이 계산
        white_gap = next_start - current_end - 1
        
        # 흰색 간격이 충분히 크지 않으면 병합
        if white_gap < min_white_gap:
            current_end = next_end  # 현재 영역 확장
        else:
            # 충분한 간격이 있으면 현재 영역 저장하고 다음 영역으로 이동
            merged_regions.append((current_start, current_end))
            current_start, current_end = next_start, next_end
    
    # 마지막 영역 추가
    merged_regions.append((current_start, current_end))
    
    # 3. 분할 영역 계산 (여백 포함) - 직접 패딩 적용
    split_regions = []
    for i, (start, end) in enumerate(merged_regions):
        # 패딩 적용한 시작점과 끝점 계산
        padded_start = max(0, start - padding)
        padded_end = min(image_height - 1, end + padding)
        split_regions.append((padded_start, padded_end))
    
    
    return split_regions



def split_image_by_white_rows(
    img: Image.Image,
    white_rows: np.ndarray,
    min_white_band: int = 10,
    offset: int = 10 , # 기본 offset 5 픽셀d
    min_image_height:int = 10
) -> list[Image.Image]:
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
    이미지에서 흰색 행을 찾는 함수 ()
    """
    if isinstance(image, str):
        image = Image.open(image)
    image_np = np.asarray(image.copy())
    mean_pixels = image_np[:, :, :3].mean(axis=(1, 2)) > mean_threshold
    dark_pixels = [np.sum(row < dark_threshold) > dark_threshold_count for row in np.mean(image_np[:,:,:3], axis=2)]
    final = ~np.array(dark_pixels) & mean_pixels   # Changed from 'not dark_pixels' to '~np.array(dark_pixels)'
    return final

def get_white_rows_by_diff(image_path: str| Image.Image , log_threshold:float = 1.2)->tuple[np.ndarray,np.ndarray]:
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
    


# def image_preprocess(images_url: list[str] | str, 
#                      is_crop:bool = True,
#                      min_white_band: int = 40,
#                      crop_offset: int = 10,
#                      min_segment_height: int = 10
#                      ) -> list[ProcessedImageSegment]:
#     """
#     Downloads images from URLs, optionally splits them into segments based on white rows,
#     and returns a list of ProcessedImageSegment objects containing the PIL images and metadata.

#     Args:
#         images_url (list[str]): list of image URLs to process.
#         is_crop (bool): Whether to crop images into segments. Defaults to True.
#         min_white_band (int): Minimum height of a white band to consider for splitting.
#         crop_offset (int): Offset pixels to add/subtract when cropping segments.
#         min_segment_height (int): Minimum height for a cropped segment to be kept.

#     Returns:
#         list[ProcessedImageSegment]: A list containing ProcessedImageSegment objects
#                                       for each resulting image or segment.
#     """
#     processed_segments: list[ProcessedImageSegment] = []
#     if isinstance(images_url, str):
#         images_url = [images_url]
#     for idx , url in enumerate(images_url):
#         image = get_pil_image_from_url(url)
#         if image is None:
#             continue

#         if is_crop:
#             # Detect white rows for potential splitting
#             white_rows = get_white_rows(image)
#             # Split the image based on detected white rows
#             segments = split_image_by_white_rows(
#                 image, 
#                 white_rows, 
#                 min_white_band=min_white_band, 
#                 offset=crop_offset,
#                 min_image_height=min_segment_height
#             )
            
#             # Create ProcessedImageSegment objects for each segment
#             for i, seg in enumerate(segments):
#                 is_text = is_wide_image(seg)
#                 segment_obj = ProcessedImageSegment(
#                     pil_image=seg,
#                     original_url=url,
#                     segment_index=i,
#                     is_text_segment=is_text,
#                     segment_id=idx
#                 )
#                 processed_segments.append(segment_obj)
#         else:
#             # If not cropping, treat the whole image as a single segment
#             is_text = is_wide_image(image)
#             segment_obj = ProcessedImageSegment(
#                 pil_image=image,
#                 original_url=url,
#                 segment_index=0, # Index 0 for the whole image
#                 is_text_segment=is_text,
#                 segment_id=idx
#             )
#             processed_segments.append(segment_obj)
            
#     return processed_segments

async def image_segmentation_async(process : ImageData ,
                         min_content_height: int = 20,
                         min_white_gap: int = 3,
                         padding: int = 5
                      ):
    """
    Downloads and segments detail images. 
    Uses asyncio internally to download images concurrently.
    """
    
    downloaded_images = await _download_images_async(process.detail_images_url)
    
    success_count = sum(1 for img in downloaded_images if img is not None)
    total_count = len(process.detail_images_url)
    logger.info(f"[{process.product_id}] 상세 이미지 다운로드 완료 ({success_count}/{total_count} 성공).")

    tasks = []
    for image_idx, image in enumerate(downloaded_images):
        if image is None:
            continue
        
        task = process_single_image_async(image , image_idx , process , min_content_height , min_white_gap , padding)
        tasks.append(task)
    
    if tasks:
        await asyncio.gather(*tasks)

async def process_single_image_async(image:Image.Image , image_idx:int , process:ImageData , min_content_height:int , min_white_gap:int , padding:int)->list[Tuple[Image.Image , bool]]:
    """
    단일 이미지를 컨텐츠 기반으로 분할
    """
    process.detail_images.append(ImageMetadata(pil_image=image, image_idx=image_idx))
    
    
    segments = await asyncio.to_thread(segment_image_by_content, image , min_content_height , min_white_gap , padding)
    
    for segment_idx ,(segment_image , is_text) in enumerate(segments):
        segment_obj = ImageMetadata(
            pil_image=segment_image,
            image_idx=image_idx,
            segment_idx=segment_idx,
            is_text_segment=is_text
        )
        process.segmented_img.append(segment_obj)
    
        
    
def segment_image_by_content(image:Image.Image , min_content_height:int , min_white_gap:int , padding:int)->list[Tuple[Image.Image , bool]]:
    """이미지를 컨텐츠 기반으로 분할
    Returns:
        list[Tuple[Image.Image , bool]]: [분활된 이미지, ist_text_segment]
    """
    segments = []
    # 흰색 영역 찾기
    white_rows = get_white_rows(image)
    
    # 컨텐츠 영역 찾기
    content_regions = find_content_regions(white_rows)
    
    # 이미지 분할 영역 계산
    split_regions = process_content_regions(
        content_regions, 
        image.height, 
        min_content_height, 
        min_white_gap, 
        padding
    )
    for i, (start , end) in enumerate(split_regions):
        if start == end:
            continue
        seg = image.crop((0, start, image.width, end))  
        is_text = is_wide_image(seg)
        segments.append((seg, is_text))
    
    return segments
    


async def save_detail_images_async(process:ImageData):
    # 원본 detail 이미지 저장
    save_tasks = []
    for img in process.detail_images:
        save_path = process.DETAIL_IMAGE_DIR/ f"{img.image_idx}.{process.image_suffix}"
        task = asyncio.to_thread(save_image_as_jpg, img.pil_image, save_path)
        save_tasks.append(task)
        
    # 분할된 이미지 저장
    for seg in process.segmented_img:
        if seg.is_text_segment:
            save_path = process.TEXT_IMAGE_DIR/ f"{seg.image_idx}_{seg.segment_idx}.{process.image_suffix}"
        else:
            save_path = process.SEGMENT_IMAGE_DIR/ f"{seg.image_idx}_{seg.segment_idx}.{process.image_suffix}"
            
        save_tasks.append(asyncio.to_thread(save_image_as_jpg, seg.pil_image, save_path , process.target_size))
    if save_tasks:
        await asyncio.gather(*save_tasks)
        
    logger.info(f"save_detail_images completed! "
                f"[detail images : {len(process.detail_images)}, segmented images : {len(process.segmented_img)}]")

def is_image_height_enough(image:Image.Image , threshold_height:int = 30)->bool:
    _, height = image.size
    if height < threshold_height:
        return False
    return True


def merge_segmented_images(directory , target_size: int|None = None):
    """
    Args:
        directory (str): The directory containing the segmented image files.
                         Expected filename format: segment_{original_index}_{segment_index}.jpg
        output_directory (str): The directory where merged images will be saved.
                                Merged files will be named: merged_{original_index}.jpg
    """

    image_files = [f for f in os.listdir(directory) if f.lower().endswith('.jpg')]

    if not image_files:
        logger.debug(f"No 'segment_*.jpg' files found in the directory: {directory}")
        return

    grouped_images = defaultdict(list)
    # pattern = re.compile(r'segment_(\d+)_(\d+)\.jpg', re.IGNORECASE)

    for filename in image_files:
        try:
            split_name = filename.split("_")
            if len(split_name) > 2:
                continue
            elif len(split_name) == 2:
                original_index , segment_index = split_name
                original_index , segment_index = map(int,[original_index,segment_index.split(".")[0]])
            full_path = os.path.join(directory, filename)
            grouped_images[original_index].append((segment_index, full_path))
        except:
            logger.warning(filename,"Not matched the expected pattern 'X_Y.jpg'")


    if not grouped_images:
        logger.warning("No valid segments found for any original image.")
        return

    # Process each group of images
    for original_index, segments in grouped_images.items():
        # Sort segments by segment index (the first element of the tuple)
        segments = natsorted(segments , key=lambda x: x[0])

        if len(segments) == 1:
            logger.debug(f"Skipping original image index {original_index} as it has only one segment.")
            continue

        image_objects = []
        total_height = 0
        width = 0
        # Load image objects and calculate dimensions
        for _, img_path in segments:
            try:
                with Image.open(img_path) as img:
                    width = img.width
                    height = img.height
                    if height < 10:
                        continue
                    image_objects.append(img.copy())
                    total_height += img.height
            except Exception as e:
                logger.error(f"Error opening image file {img_path}: {e}. Skipping this image.")
                
        if len(image_objects) == 0 or total_height < 80:
            logger.warning(f"No valid images found for original image index {original_index}.")
            continue
        merged_image = Image.new(image_objects[0].mode, (width, total_height))

        # Paste segments vertically
        current_y = 0
        for img in image_objects:
            merged_image.paste(img, (0, current_y))
            current_y += img.height
            

        # Save the merged image
        output_filename = f"merged_{original_index}.jpg"
        output_path = os.path.join(directory, output_filename)
        try:
            if target_size is not None:
                save_image_as_jpg(merged_image, output_path , target_size)
            else:
                save_image_as_jpg(merged_image, output_path) 
            logger.debug(f"Successfully saved merged image: {output_path}")
        except Exception as e:
            logger.error(f"Error saving merged image {output_path}: {e}")

    # 기존의 이미지 삭제
    for image in image_files:
        os.remove(os.path.join(directory, image))