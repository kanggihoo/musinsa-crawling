import _path_utils  
from crawler import get_product_detail_info, Crawler
import pandas as pd
from pymongo import MongoClient, UpdateOne , InsertOne
from datetime import datetime
from typing import List, Dict, Tuple
from pathlib import Path
from enum import Enum
from crawler.model.product_schema import create_product_document

class CrawlingStatus(Enum):
    NOT_FOUND = "not_found"
    SUCCESS = "success"
    FAILED = "failed"


class CrawlingProgressManager:
    batch_operations:List 
    
    def __init__(self, db_name="crawling_db", collection_name="products_detail", batch_size=50):
        # MongoDB 연결
        self.client = MongoClient('localhost', 27017)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        self.batch_size = batch_size
        
        # product_id에 대한 인덱스 생성
        self.collection.create_index("product_id", unique=True)
        
        # 배치 처리를 위한 임시 저장소
        self.batch_operations = []
        self.current_batch_size = 0
    
    def is_crawled(self, doc: dict) -> CrawlingStatus:
        
        if doc is None:
            return CrawlingStatus.NOT_FOUND
        else:
            if doc.get("success_status" , "") == "success":
                return   CrawlingStatus.SUCCESS
            elif doc.get("success_status" , "") == "failed":
                return CrawlingStatus.FAILED
            else:
                return CrawlingStatus.NOT_FOUND
    def find_one(self , product_id: str) -> Dict:
        return self.collection.find_one({"product_id": product_id})
    
    def prepare_update(self, current_doc: dict, result: Dict) -> UpdateOne:
        """MongoDB update 작업 준비"""
        current_time = datetime.now()
        
        # 현재 document 조회
        if not current_doc:
            return None
            
        # 업데이트가 필요한 필드 확인
        update_fields = {}
        current_crawling_status = current_doc["preprocessing_status"]["detail_crawling"].get("status", {})
        
        # 이미지 관련 업데이트 확인
        # if current_crawling_status.get("summary_images") != "success" and result.get("product_summary_images"):
        #     update_fields["product_summary_images"] = result["product_summary_images"]
        #     update_fields["crawling_status.summary_images"] = "success"
            
        # if current_crawling_status.get("detail_images") != "success" and result.get("product_detail_images"):
        #     update_fields["product_detail_images"] = result["product_detail_images"]
        #     update_fields["crawling_status.detail_images"] = "success"
            
        # # 텍스트 관련 업데이트 확인
        # if current_crawling_status.get("detail_text") != "success" and result.get("product_details_text"):
        #     update_fields["product_details_text"] = result["product_details_text"]
        #     update_fields["crawling_status.detail_text"] = "success"
            
        # # 리뷰 업데이트 확인
        # if current_crawling_status.get("reviews") != "success" and result.get("review_texts"):
        #     update_fields["review_texts"] = result["review_texts"]
        #     update_fields["crawling_status.reviews"] = "success"
            
        # # 컬러/사이즈 정보 업데이트 확인
        # if current_crawling_status.get("color_size") != "success" and result.get("color_size_info"):
        #     update_fields["color_size_info"] = result["color_size_info"]
        #     update_fields["crawling_status.color_size"] = "success"
            
        # # 모든 상태가 success인지 확인
        # if all(status == "success" for status in update_fields.get("crawling_status", {}).values()):
        #     update_fields["success_status"] = "success"
        
        # # 업데이트할 내용이 있는 경우에만 last_updated 추가
        # if update_fields:
        #     update_fields["last_updated"] = current_time
            
        #     return UpdateOne(
        #         {"product_id": current_doc.get("product_id")},
        #         {"$set": update_fields}
        #     )
        
        # return None
    def prepare_insert(self , product_id: str, result: Dict) -> InsertOne:
        return InsertOne(
           create_product_document(product_id, result, datetime.now())
        )
    def add_to_batch(self, product_id: str, result: Dict, doc: dict, crawling_status: CrawlingStatus) -> None:
        """배치에 작업 추가"""
        operation = None
        
        if crawling_status == CrawlingStatus.NOT_FOUND:
            operation = self.prepare_insert(product_id, result)
        elif crawling_status == CrawlingStatus.FAILED:
            operation = self.prepare_update(doc, result)
            
        if operation:  # None이 아닌 경우에만 배치에 추가
            self.batch_operations.append(operation)
            self.current_batch_size += 1
            
            if self.current_batch_size >= self.batch_size:
                self.execute_batch()
    
    def execute_batch(self) -> None:
        """배치 작업 실행"""
        if not self.batch_operations:
            return
            
        try:
            # bulk_write 실행
            result = self.collection.bulk_write(self.batch_operations, ordered=False)
            print(f"Batch update completed: {result.modified_count} modified, {result.upserted_count} inserted")
        except Exception as e:
            print(f"Error during batch update: {str(e)}")
        finally:
            # 배치 초기화
            self.batch_operations = []
            self.current_batch_size = 0
    
    def get_progress_stats(self) -> Dict:
        """진행 상황 통계 조회"""
        total = self.collection.count_documents({})
        completed = self.collection.count_documents({"preprocessing_status.detail_crawling_completed": True})
        # preprocessing_stats = {
        #     "detail_crawling": completed,
        #     "text_preprocessing": self.collection.count_documents({"preprocessing_status.text_preprocessing": True}),
        #     "image_preprocessing": self.collection.count_documents({"preprocessing_status.image_preprocessing": True}),
        #     "feature_extraction": self.collection.count_documents({"preprocessing_status.feature_extraction": True}),
        #     "sentiment_analysis": self.collection.count_documents({"preprocessing_status.sentiment_analysis": True})
        # }
        return {
            "total": total,
            "completed": completed,
            "remaining": total - completed,
        }
    
    def close(self):
        """남은 배치 처리 후 연결 종료"""
        self.execute_batch()  # 남은 배치 작업 처리
        self.client.close()

crawler = Crawler()
progress_manager = CrawlingProgressManager(batch_size=50)  # 배치 크기 50으로 설정

def get_product_detail_generator(df, start_idx:int=0, end_idx:int=None, batch_size:int=None):
    end_idx = len(df) if end_idx is None else end_idx
    processed_count = 0
    
    for idx in range(start_idx, end_idx):
        if batch_size and processed_count >= batch_size:
            break
            
        product_id = df.iloc[idx]["product_id"]
        
        # Skip if already crawled
        doc = progress_manager.find_one(product_id)
        crawling_status = progress_manager.is_crawled(doc)
        if crawling_status == CrawlingStatus.SUCCESS:
            print(f"Skipping already crawled product: {product_id}")
            continue
            
        category_main = df.iloc[idx]["category_main"]
        category_sub = df.iloc[idx]["category_sub"]
        
        
        result = get_product_detail_info(crawler, product_id)
        result["category_main"] = category_main 
        result["category_sub"] = category_sub
            
        # 배치에 추가
        progress_manager.add_to_batch(product_id, result ,doc , crawling_status)
        processed_count += 1
            
        yield result


if __name__ == "__main__":
    BASE_DIR = Path(__file__).parent.parent
    
    # .csv 파일로 부터 제품 detail 정보 크롤링
    df = pd.read_csv("musinsa_product_summary_final_.csv", dtype={'product_id': str, 'category_sub': str})
    
    # 한 번에 처리할 제품 수 설정
    BATCH_SIZE = 100  # 예시로 100개씩 처리
    
    # 크롤링 시작 전 진행 상황 출력
    stats = progress_manager.get_progress_stats()
    print("\nInitial progress:")
    print(f"- Total products: {stats['total']}")
    print(f"- Completed: {stats['completed']}")
    print(f"- Remaining: {stats['remaining']}")
    
    try:
        results = []
        for idx, result in enumerate(get_product_detail_generator(df, batch_size=BATCH_SIZE)):
            results.append(result)
            if (idx + 1) % progress_manager.batch_size == 0:
                print(f"Processed {idx + 1}/{BATCH_SIZE} products")
                
    except KeyboardInterrupt:
        print("\nCrawling interrupted by user. Saving current batch...")
        progress_manager.execute_batch()
    except Exception as e:
        print(f"\nUnexpected error occurred: {str(e)}")
        print("Attempting to save current batch...")
        progress_manager.execute_batch()
    finally:
        # 최종 진행 상황 출력
        stats = progress_manager.get_progress_stats()
        print("\nFinal progress:")
        print(f"- Total products: {stats['total']}")
        print(f"- Completed: {stats['completed']}")
        print(f"- Remaining: {stats['remaining']}")
        print("\nPreprocessing status:")
        for step, count in stats['preprocessing_stats'].items():
            print(f"- {step}: {count}")
        
        # 연결 종료
        progress_manager.close()
        crawler.close()