# models/product_schema.py
from datetime import datetime
from typing import Dict, Any, Optional # 타입 힌트를 위해 임포트

def create_product_document(
    product_id: str,
    result_data: Dict[str, Any], # 크롤링 등의 결과를 담은 딕셔너리
    current_time: datetime # 현재 시간
) -> Dict[str, Any]:
    """
    MongoDB product 문서 구조를 생성하여 반환하는 함수.

    Args:
        product_id: 제품의 고유 ID (_id로 사용됨).
        result_data: 크롤링 등 외부에서 얻은 제품 상세 데이터 딕셔너리.
        current_time: 문서 생성/업데이트 시각.

    Returns:
        MongoDB에 삽입할 문서 구조를 담은 딕셔너리.
    """
    document = {
        # _id를 product_id 값으로 설정
        "_id": product_id,
        "product_id": product_id,

        # result_data에서 데이터 가져오기. .get()을 사용하여 키가 없어도 오류 방지
        "category_main": result_data.get("category_main"),
        "category_sub": result_data.get("category_sub"),
        "product_summary_images": result_data.get("product_summary_images", []), # 기본값 빈 리스트
        "product_detail_images": result_data.get("product_detail_images", []),   # 기본값 빈 리스트
        "product_details_text": result_data.get("product_details_text", ""),   # 기본값 빈 문자열
        "review_texts": result_data.get("review_texts", []),                 # 기본값 빈 리스트
        "color_size_info": result_data.get("color_size_info", {}),           # 기본값 빈 딕셔너리
        # preprocessing_status 필드 추가 및 초기 상태 설정
        "preprocessing_status": {
            "detail_crawling": {
                # result_data의 success_status 사용
                "status": result_data.get("success_status", ""),
                "date": current_time
            },
            # 나머지 전처리 단계는 초기 상태로 설정
            "processing_color_info": {
                "status": "not_started",
                "date": None
            },
            "classifying_image": {
                "status": "not_started",
                "date": None
            },
            "merging_text_image": { # 오타 수정 반영
                "status": "not_started",
                "date": None
            },
            "parsing_text_info": { # 변수명 논의 고려하여 필요시 변경 가능
                "status": "not_started",
                "date": None
            },
            "selecting_image": { # 변수명 논의 고려하여 필요시 변경 가능
                "status": "not_started",
                "date": None
            },
            "captioning_image": { # 변수명 논의 고려하여 필요시 변경 가능
                "status": "not_started",
                "date": None
            }
        },
        "last_updated": current_time # 문서 생성/업데이트 시각
    }

    return document