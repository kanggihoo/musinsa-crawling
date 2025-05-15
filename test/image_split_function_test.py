import numpy as np
from PIL import Image
import _path_utils
from crawler.preprocess import image_preprocess ,save_segments , get_white_rows  , split_image_by_white_rows , get_pil_image_from_url , ProcessedImageSegment , is_wide_image




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

def process_content_regions(content_regions, image_height, min_content_height=20, min_white_gap=3, padding=5):
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
    
    
    # 여기서 텍스트 이면 padding을 작게 해서 
    # for i, (start, end) in enumerate(merged_regions):
    #     # 패딩 적용한 시작점과 끝점 계산
    #     padded_start = max(0, start - padding)
    #     padded_end = min(image_height - 1, end + padding)
        
    #     # 첫 번째 영역이거나 이전 영역과 겹치지 않는 경우
    #     if i == 0 or padded_start > split_regions[-1][1]:
    #         split_regions.append((padded_start, padded_end))
    #     else:
    #         # 이전 영역과 겹치는 경우, 이전 영역의 끝점을 현재 영역의 끝점으로 확장
    #         prev_start, _ = split_regions[-1]
    #         split_regions[-1] = (prev_start, padded_end)
    
    # # 결과 검증 (누락된 영역이 없는지)
    # validated_regions = []
    # last_end = -1
    
    # for start, end in split_regions:
    #     # 영역 사이에 누락된 부분이 있으면 채움
    #     if start > last_end + 1 and last_end != -1:
    #         # 두 영역 사이의 간격이 매우 작으면 (임계값의 2배 이하) 병합
    #         if start - last_end - 1 <= min_white_gap * 2:
    #             # 이전 영역의 끝점을 현재 영역의 시작점으로 확장
    #             validated_regions[-1] = (validated_regions[-1][0], end)
    #         else:
    #             # 간격이 충분히 크면 누락된 부분을 별도 영역으로 추가
    #             validated_regions.append((last_end + 1, start - 1))
    #             validated_regions.append((start, end))
    #     else:
    #         validated_regions.append((start, end))
        
    #     last_end = end
    
    # 이미지 범위를 넘어가는 경우 조정 (이미 위에서 처리했지만 안전을 위해 재확인)
    # final_regions = []
    # for start, end in validated_regions:
    #     start = max(0, start)
    #     end = min(image_height - 1, end)
    #     if start <= end:  # 유효한 영역만 추가
    #         final_regions.append((start, end))
    
    return split_regions

def split_image(image_path, output_prefix, min_content_height=8, min_white_gap=8, padding=5):
    """
    이미지를 분할하여 저장하는 함수
    
    Parameters:
    - image_path: 분할할 이미지 경로
    - output_prefix: 저장할 이미지 파일명 접두사
    - min_content_height: 유효한 컨텐츠로 간주할 최소 높이
    - min_white_gap: 컨텐츠 영역을 분리하기 위한 최소 흰색 영역 높이
    - padding: 각 분할 영역에 추가할 상하 여백
    """
    # 이미지 로드
    image = Image.open(image_path)
    white_rows = get_white_rows(image)
    
    # 컨텐츠 영역 찾기
    content_regions = find_content_regions(white_rows)
    
    # 컨텐츠 영역 처리 및 분할 영역 계산
    split_regions = process_content_regions(
        content_regions, 
        image.height, 
        min_content_height, 
        min_white_gap, 
        padding
    )
    
    # 이미지 분할 및 저장
    for i, (start, end) in enumerate(split_regions):
        # 이미지 분할
        cropped = image.crop((0, start, image.width, end))
        
        # 저장 경로 생성
        output_path = f"{output_prefix}_{i+1}.png"
        
        # 이미지 저장
        cropped.save(output_path)
        print(f"Saved: {output_path} (Height: {end - start}px, Range: {start}-{end})")
    
    return len(split_regions)



# min_content_height : 컨텐츠 영역의 최소 높이 , 컨텐츠 영역의 높이가 이 값보다 작으면 무시
# min_white_gap : 컨텐츠 영역을 분리하기 위한 최소 흰색 영역 높이
# padding : 각 분할 영역에 추가할 상하 여백
split_image("./t.jpg", "./", min_content_height=10, min_white_gap=5, padding=5)

