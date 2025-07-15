# import _path_utils  
# from crawler import get_product_detail_info, Crawler
# import pandas as pd
# from pymongo import MongoClient, UpdateOne , InsertOne
# from datetime import datetime
# from typing import List, Dict, Tuple
# from pathlib import Path
# from enum import Enum
# from crawler.model.product_schema import create_product_document

# class CrawlingStatus(Enum):
#     NOT_FOUND = "not_found"
#     SUCCESS = "success"
#     FAILED = "failed"


# class CrawlingProgressManager:
#     batch_operations:List 
    
#     def __init__(self, db_name="crawling_db", collection_name="products_detail", batch_size=50):
#         # MongoDB 연결
#         self.client = MongoClient('localhost', 27017)
#         self.db = self.client[db_name]
#         self.collection = self.db[collection_name]
#         self.batch_size = batch_size
        
#         # product_id에 대한 인덱스 생성
#         self.collection.create_index("product_id", unique=True)
        
#         # 배치 처리를 위한 임시 저장소
#         self.batch_operations = []
#         self.current_batch_size = 0
    
#     def is_crawled(self, doc: dict) -> CrawlingStatus:
        
#         if doc is None:
#             return CrawlingStatus.NOT_FOUND
#         else:
#             if doc.get("success_status" , "") == "success":
#                 return   CrawlingStatus.SUCCESS
#             elif doc.get("success_status" , "") == "failed":
#                 return CrawlingStatus.FAILED
#             else:
#                 return CrawlingStatus.NOT_FOUND
#     def find_one(self , product_id: str) -> Dict:
#         return self.collection.find_one({"product_id": product_id})
    
#     def prepare_update(self, current_doc: dict, result: Dict) -> UpdateOne:
#         """MongoDB update 작업 준비"""
#         current_time = datetime.now()
        
#         # 현재 document 조회
#         if not current_doc:
#             return None
            
#         # 업데이트가 필요한 필드 확인
#         update_fields = {}
#         current_crawling_status = current_doc["preprocessing_status"]["detail_crawling"].get("status", {})
        
#         # 이미지 관련 업데이트 확인
#         # if current_crawling_status.get("summary_images") != "success" and result.get("product_summary_images"):
#         #     update_fields["product_summary_images"] = result["product_summary_images"]
#         #     update_fields["crawling_status.summary_images"] = "success"
            
#         # if current_crawling_status.get("detail_images") != "success" and result.get("product_detail_images"):
#         #     update_fields["product_detail_images"] = result["product_detail_images"]
#         #     update_fields["crawling_status.detail_images"] = "success"
            
#         # # 텍스트 관련 업데이트 확인
#         # if current_crawling_status.get("detail_text") != "success" and result.get("product_details_text"):
#         #     update_fields["product_details_text"] = result["product_details_text"]
#         #     update_fields["crawling_status.detail_text"] = "success"
            
#         # # 리뷰 업데이트 확인
#         # if current_crawling_status.get("reviews") != "success" and result.get("review_texts"):
#         #     update_fields["review_texts"] = result["review_texts"]
#         #     update_fields["crawling_status.reviews"] = "success"
            
#         # # 컬러/사이즈 정보 업데이트 확인
#         # if current_crawling_status.get("color_size") != "success" and result.get("color_size_info"):
#         #     update_fields["color_size_info"] = result["color_size_info"]
#         #     update_fields["crawling_status.color_size"] = "success"
            
#         # # 모든 상태가 success인지 확인
#         # if all(status == "success" for status in update_fields.get("crawling_status", {}).values()):
#         #     update_fields["success_status"] = "success"
        
#         # # 업데이트할 내용이 있는 경우에만 last_updated 추가
#         # if update_fields:
#         #     update_fields["last_updated"] = current_time
            
#         #     return UpdateOne(
#         #         {"product_id": current_doc.get("product_id")},
#         #         {"$set": update_fields}
#         #     )
        
#         # return None
#     def prepare_insert(self , product_id: str, result: Dict) -> InsertOne:
#         return InsertOne(
#            create_product_document(product_id, result, datetime.now())
#         )
#     def add_to_batch(self, product_id: str, result: Dict, doc: dict, crawling_status: CrawlingStatus) -> None:
#         """배치에 작업 추가"""
#         operation = None
        
#         if crawling_status == CrawlingStatus.NOT_FOUND:
#             operation = self.prepare_insert(product_id, result)
#         elif crawling_status == CrawlingStatus.FAILED:
#             operation = self.prepare_update(doc, result)
            
#         if operation:  # None이 아닌 경우에만 배치에 추가
#             self.batch_operations.append(operation)
#             self.current_batch_size += 1
            
#             if self.current_batch_size >= self.batch_size:
#                 self.execute_batch()
    
#     def execute_batch(self) -> None:
#         """배치 작업 실행"""
#         if not self.batch_operations:
#             return
            
#         try:
#             # bulk_write 실행
#             result = self.collection.bulk_write(self.batch_operations, ordered=False)
#             print(f"Batch update completed: {result.modified_count} modified, {result.upserted_count} inserted")
#         except Exception as e:
#             print(f"Error during batch update: {str(e)}")
#         finally:
#             # 배치 초기화
#             self.batch_operations = []
#             self.current_batch_size = 0
    
#     def get_progress_stats(self) -> Dict:
#         """진행 상황 통계 조회"""
#         total = self.collection.count_documents({})
#         completed = self.collection.count_documents({"preprocessing_status.detail_crawling_completed": True})
#         # preprocessing_stats = {
#         #     "detail_crawling": completed,
#         #     "text_preprocessing": self.collection.count_documents({"preprocessing_status.text_preprocessing": True}),
#         #     "image_preprocessing": self.collection.count_documents({"preprocessing_status.image_preprocessing": True}),
#         #     "feature_extraction": self.collection.count_documents({"preprocessing_status.feature_extraction": True}),
#         #     "sentiment_analysis": self.collection.count_documents({"preprocessing_status.sentiment_analysis": True})
#         # }
#         return {
#             "total": total,
#             "completed": completed,
#             "remaining": total - completed,
#         }
    
#     def close(self):
#         """남은 배치 처리 후 연결 종료"""
#         self.execute_batch()  # 남은 배치 작업 처리
#         self.client.close()

# crawler = Crawler()
# progress_manager = CrawlingProgressManager(batch_size=50)  # 배치 크기 50으로 설정

# def get_product_detail_generator(df, start_idx:int=0, end_idx:int=None, batch_size:int=None):
#     end_idx = len(df) if end_idx is None else end_idx
#     processed_count = 0
    
#     for idx in range(start_idx, end_idx):
#         if batch_size and processed_count >= batch_size:
#             break
            
#         product_id = df.iloc[idx]["product_id"]
        
#         # Skip if already crawled
#         doc = progress_manager.find_one(product_id)
#         crawling_status = progress_manager.is_crawled(doc)
#         if crawling_status == CrawlingStatus.SUCCESS:
#             print(f"Skipping already crawled product: {product_id}")
#             continue
            
#         category_main = df.iloc[idx]["category_main"]
#         category_sub = df.iloc[idx]["category_sub"]
        
        
#         result = get_product_detail_info(crawler, product_id)
#         result["category_main"] = category_main 
#         result["category_sub"] = category_sub
            
#         # 배치에 추가
#         progress_manager.add_to_batch(product_id, result ,doc , crawling_status)
#         processed_count += 1
            
#         yield result


 
import _path_utils
from crawler import get_product_detail_info, Crawler
from crawler.utils import setup_logger
import pandas as pd
from pathlib import Path
import json
from tqdm import tqdm


def merge_summary_into_detail(detail_info: dict, product_summary: tuple) -> dict:
    """제품 요약 정보를 상세 정보 딕셔너리에 병합합니다."""
    summary_keys_to_merge = [
        "product_id", "product_price", "product_original_price", "product_discount_price",
        "product_discount_rate", "product_brand_name", "product_name",
        "num_likes", "avg_rating", "review_count", "category_main",
        "category_sub", "gender"
    ]
    product_summary_dict = product_summary._asdict()
    for key in summary_keys_to_merge:
        detail_info[key] = product_summary_dict[key]
    return detail_info


def crawl_product_details(summary_df: pd.DataFrame, crawler: Crawler, logger):
    """요약 정보를 기반으로 제품 상세 정보를 크롤링합니다."""
    crawled_details = []
    unavailable_products = []

    # tqdm을 사용하여 진행상황 표시
    for product_summary in tqdm(summary_df.itertuples(), 
                               total=len(summary_df), 
                               desc="제품 상세정보 크롤링", 
                               unit="개"):
        
        try:
            if product_summary.success_status != "success":
                logger.error(f"summary 크롤링 실패 : {product_summary.product_id}")
                continue

            product_id = product_summary.product_id
            
            # 상세 정보 크롤링
            detail_info = get_product_detail_info(crawler, product_id, logger)
            
            # 기존의 요약 정보로 부터 상세 정보 크롤링 결과 병합
            detail_info = merge_summary_into_detail(detail_info, product_summary)

            if detail_info.get("success_status") == "success":
                crawled_details.append(detail_info)
            elif detail_info.get("crawling_status", {}).get("color_size_info") == "not_exist":
                unavailable_products.append(detail_info)
            else:
                logger.warning(f"크롤링 결과 상태를 알 수 없습니다: {product_id}")
                
        except KeyboardInterrupt:
            # Ctrl+C로 강제 종료한 경우 지금까지 수집한 데이터를 반환
            logger.info(f"사용자에 의해 크롤링이 중단되었습니다. 지금까지 수집된 데이터: 성공 {len(crawled_details)}개, 품절/정보없음 {len(unavailable_products)}개")
            return crawled_details, unavailable_products
        except Exception as e:
            # 다른 예외는 로그에 기록 후 계속 진행
            logger.error(f"상세 정보 크롤링 간 예기치 못한 예외 발생  {product_summary.product_id} , 에러 : {e}")
            continue
        

    return crawled_details, unavailable_products


def save_results_to_json(save_dir: Path, file_name_prefix: str, crawled_details: list, unavailable_products: list):
    """크롤링된 데이터를 JSON 파일로 저장합니다."""
    if crawled_details:
        output_path = save_dir / f"{file_name_prefix}.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(crawled_details, f, ensure_ascii=False, indent=4)
        print(f"성공한 상품 {len(crawled_details)}개를 {output_path}에 저장했습니다.")
    else:
        print("저장할 크롤링 성공 결과가 없습니다.")

    if unavailable_products:
        output_path = save_dir / f"{file_name_prefix}_unavailable.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(unavailable_products, f, ensure_ascii=False, indent=4)
        print(f"품절/정보 없는 상품 {len(unavailable_products)}개를 {output_path}에 저장했습니다.")

CATEGORY = [
    {"category_main": "TOP", "category_sub": "001001"}, # 반소매티셔츠 
    {"category_main": "TOP", "category_sub": "001002"}, # 셔츠-블라우스 
    {"category_main": "TOP", "category_sub": "001003"}, # 피케-카라티셔츠 
    {"category_main": "TOP", "category_sub": "001004"}, # 후드티셔츠 
    {"category_main": "TOP", "category_sub": "001005"}, # 맨투맨-스웨트 
    {"category_main": "TOP", "category_sub": "001006"}, # 니트-스웨터 
    {"category_main": "TOP", "category_sub": "001008"}, # 기타상의 
    {"category_main": "TOP", "category_sub": "001010"}, # 긴소매-티셔츠 
    {"category_main": "TOP", "category_sub": "001011"}, # 민소매-티셔츠 OK
    {"category_main": "BOTTOM", "category_sub": "003002"}, # 데님팬츠 
    {"category_main": "BOTTOM", "category_sub": "003004"}, # 트레이닝-조거팬츠 
    {"category_main": "BOTTOM", "category_sub": "003005"}, # 레깅스
    {"category_main": "BOTTOM", "category_sub": "003006"}, # 기타하의
    {"category_main": "BOTTOM", "category_sub": "003007"}, # 코튼팬츠
    {"category_main": "BOTTOM", "category_sub": "003008"}, # 슈트팬츠-슬랙스
    {"category_main": "BOTTOM", "category_sub": "003009"}, # 숏팬츠
    {"category_main": "BOTTOM", "category_sub": "003010"}, # 점프슈트-오버울
]

def main():
    """메인 실행 함수"""
    logger = setup_logger(file_name="crawling_product_detail.log")
    crawler = Crawler(base_url="https://www.musinsa.com/products", headless=True)
    
    BASE_DIR = Path("./")
    DATA_DIR = BASE_DIR / "data"
    main_category , sub_category = "하의" , "데님팬츠"
    CSV_FILE_NAME = f"musinsa_product_summary_{main_category}_{sub_category}.csv"
    INPUT_CSV_FILE_NAME = DATA_DIR / CSV_FILE_NAME
    OUTPUT_FILE_PREFIX = f"musinsa_product_detail_{main_category}_{sub_category}"
    

    try:
        summary_df = pd.read_csv(INPUT_CSV_FILE_NAME, dtype={'product_id': str})
    except FileNotFoundError:
        logger.error(f"입력 파일을 찾을 수 없습니다: {INPUT_CSV_FILE_NAME}")
        return

    crawled_details, unavailable_products = [], []
    

    crawled_details, unavailable_products = crawl_product_details(summary_df, crawler, logger)

    crawler.close()
    save_results_to_json(DATA_DIR, OUTPUT_FILE_PREFIX, crawled_details, unavailable_products)


if __name__ == "__main__":
    main()
