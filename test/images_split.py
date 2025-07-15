import _path_utils
from crawler.preprocess import save_summary_images_async , ImageData , image_segmentation_async , save_detail_images_async , merge_segmented_images
import json
from crawler.constants import MIN_CONTENT_HEIGHT , MIN_WHITE_GAP , PADDING
from crawler.utils import setup_logger
from tqdm import tqdm
import os
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import logging
import asyncio

logger = setup_logger(name="image_split", file_name="image_split.log")

async def process_single_product(product_data,  idx ):
    try:
        product_name = product_data["product_name"]
        if "set" in product_name.lower() or "package" in product_name.lower():
            return None
        
        process = ImageData(
            product_id=product_data["product_id"],
            summary_images_url=product_data["summary_images"],
            detail_images_url=product_data["detail_images"],
            category_main=product_data["category_main"],
            category_sub=product_data["category_sub"],
            target_size=720
        )
        
        # 디렉토리 생성 
        await process.create_all_directories()
        
        # 요약 이미지 처리
        await save_summary_images_async(process)

        # 상세 이미지 처리
        await image_segmentation_async(process, min_content_height=MIN_CONTENT_HEIGHT, min_white_gap=MIN_WHITE_GAP, padding=PADDING)
        await save_detail_images_async(process)
        
        # text merged 
        merge_segmented_images(process.TEXT_IMAGE_DIR, process.target_size)
        
        # 제품 메타 정보 저장(json)
        meta_data = {
            "product_id": product_data["product_id"],
            "product_name": product_data["product_name"],
            "brand_name": product_data["product_brand_name"],
            "category_main": product_data["category_main"],
            "category_sub": product_data["category_sub"],
            "color_info": product_data["color_size_info"].get("color", "No 'color' key"),
            "size_info": product_data["color_size_info"].get("size", "No 'size' key"),
            "price": product_data["product_price"],
            "num_likes": product_data["num_likes"],
            "review_count": product_data["review_count"],
            "avg_rating": product_data["avg_rating"],
            "description": product_data["detail_text"],
            "is_size_detail_info": True if product_data["size_detail_info"] else False,
            "recommendation_order": idx
        }
        
        file_path = os.path.join(process.BASE_DIR, "meta.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(meta_data, f, ensure_ascii=False, indent=4)
        
        return f"Success: {product_data['product_id']}"
        
    except Exception as e:
        logger.error(f"제품 {product_data['product_id']} 처리 중 오류: {str(e)}")
        return f"Failed: {product_data['product_id']}"
    
async def process_batch(batch_data, start_idx, semaphore):
    """배치 단위로 제품들을 처리"""
    async def process_single_product_with_limit(product_data, idx):
        async with semaphore:
            try:
                return await process_single_product(product_data, idx)
            except Exception as e:
                error_msg = f"Failed: {product_data.get('product_id', 'unknown')} - {str(e)}"
                logger.error(error_msg)
                return error_msg
    
    # 배치 내 태스크들 생성 및 실행
    tasks = [
        process_single_product_with_limit(product_data, start_idx + idx + 1)
        for idx, product_data in enumerate(batch_data)
    ]
    
    results = await asyncio.gather(*tasks)
    return results

async def main():
    """메인 실행 함수"""
    # 로거 설정
    
    # 데이터 로드
    with open("./data/musinsa_product_detail_상의_민소매티셔츠.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    logger.info(f"총 데이터 개수: {len(data)}")
    
    # 설정
    max_concurrent = 10  # 동시 처리 수
    batch_size = 100      # 배치 크기
    semaphore = asyncio.Semaphore(max_concurrent)
    
    all_results = []
    total_batches = (len(data) - 1) // batch_size + 1
    
    # 배치별로 처리
    with tqdm(total=len(data), desc="Processing products") as pbar:
        for i in range(0, len(data), batch_size):
            batch_data = data[i:i+batch_size]
            batch_num = i // batch_size + 1
            
            logger.info(f"배치 {batch_num}/{total_batches} 처리 중... ({len(batch_data)}개 제품)")
            
            # 배치 처리
            batch_results = await process_batch(batch_data, i, semaphore)
            all_results.extend(batch_results)
            
            # 진행률 업데이트
            pbar.update(len(batch_data))
            
            # 배치 간 잠깐 대기 (시스템 안정화)
            await asyncio.sleep(0.1)
    
    # 결과 분석 및 출력
    success_count = sum(1 for r in all_results if isinstance(r, str) and r.startswith("Success"))
    failed_count = len(all_results) - success_count
    
    print(f"\n=== 처리 완료 ===")
    print(f"총 처리된 제품: {len(all_results)}개")
    print(f"성공: {success_count}개")
    print(f"실패: {failed_count}개")
    # print(f"처리 시간: {elapsed_time:.2f}초")
    
    if failed_count > 0:
        print(f"\n실패한 제품들:")
        for result in all_results:
            if isinstance(result, str) and result.startswith("Failed"):
                logger.error(result)

if __name__ == "__main__":
    # asyncio.run()을 한 번만 호출
    asyncio.run(main())

# if __name__ == "__main__":
#     # JSON 파일을 읽은뒤 진행
#     logger = setup_logger(name ="image_split" , file_name="image_split.log")
#     with open("./data/musinsa_product_detail_하의_데님팬츠.json" , "r" , encoding="utf-8") as f:
#         data = json.load(f)

#     max_num_workers = 4
#     batch_size = 50
#     total_data = len(data)
#     logger.info(f"총 데이터 개수 : {len(data)}")
#     results = []
    
#     for i in range(0, len(data) , batch_size):
#         batch_data = data[i:i+batch_size]
#         batch_num = i // batch_size + 1
#         total_batches = (total_data-1) // batch_size + 1
#         logger.info(f"\n배치 {batch_num}/{total_batches} 처리 중... ({len(batch_data)}개 제품)")
        
#         with ThreadPoolExecutor(max_workers=max_num_workers) as executor:
#             # 현재 배치의 future들을 저장
#             future_to_idx = {}
            
#             #각 제품에 대한 작업 제출
#             for j , product_data in enumerate(batch_data):
#                 idx = i+j+ 1
#                 future = executor.submit(process_single_product, product_data, idx)
#                 future_to_idx[future] = idx
                
#             # 진행률 표시 tqdm
#             with tqdm(total=len(batch_data) , desc = "Batch {batch_num}") as pbar:
#                 # 완료한 작업들을 처리
#                 for future in concurrent.futures.as_completed(future_to_idx.keys()):
#                     try:
#                         result = future.result()
#                         if result:
#                             results.append(result)
#                     except Exception as e:
#                         idx = future_to_idx[future]
#                         logger.error(f"제품 인덱스 {idx} 처리 중 오류: {str(e)}")
#                     finally:
#                         pbar.update(1)
                    
                
#     # 최종 결과 출력
#     success_count = sum(1 for r in results if r.startswith("Success"))
#     failed_count = sum(1 for r in results if r.startswith("Failed"))
    
    
#     print(f"\n=== 처리 완료 ===")
#     print(f"총 처리된 제품: {len(results)}개")
#     print(f"성공: {success_count}개")
#     print(f"실패: {failed_count}개")
    
#     if failed_count > 0:
#         print(f"\n실패한 제품들:")
#         for result in results:
#             if result.startswith("Failed"):
#                 logger.error(result)
    
    
    # # 실패한 제품 정보 출력
    # failed_products = [r for r in results if r.startswith("Failed")]
    # if failed_products:
    # idx = 1
    # for d in tqdm(data, desc="Processing products"):
    #     product_name = d["product_name"]
    #     if "set" in product_name.lower() or "package" in product_name.lower():
    #         continue
    #     process = ImageData(
    #         product_id=d["product_id"],
    #         summary_images_url=d["summary_images"],
    #         detail_images_url=d["detail_images"],
    #         category_main=d["category_main"],
    #         category_sub=d["category_sub"],
    #         target_size=720
    #     )
        
        
    #     #TODO : 에러 처리 안되어 있음. 
    #     # 요약 이미지 처리
    #     save_summary_images(process , logger=logger)

    #     # 상세 이미지 처리t
    #     image_segmentation(process ,logger=logger,min_content_height=MIN_CONTENT_HEIGHT,min_white_gap=MIN_WHITE_GAP,padding=PADDING)
    #     save_detail_images(process , logger=logger)
        
    #     # # text merged 
    #     merge_segmented_images(process.TEXT_IMAGE_DIR , process.target_size)
        
    #     #TODO : 색상 메타 정보 더 추가 (사람이 확인하는 과정에서 제외할 데이터 판단 여부?)
    #     # 제품 메타 정보 저장(json)
    #     meta_data = {
    #         "product_id": d["product_id"],
    #         "product_name" : d["product_name"],
    #         "brand_name" : d["product_brand_name"],
    #         "category_main": d["category_main"],
    #         "category_sub": d["category_sub"],
    #         "color_info" : d["color_size_info"].get("color" , "No 'color' key"),
    #         "size_info" : d["color_size_info"].get("size" , "No 'size' key"),
    #         "price" : d["product_price"],
    #         "num_likes" : d["num_likes"],
    #         "review_count" : d["review_count"],
    #         "avg_rating" : d["avg_rating"],
    #         "description" : d["detail_text"],
    #         "is_size_detail_info" : True if d["size_detail_info"] else False,
    #         "recommendation_order" : idx
    #     }
        
    #     file_path = os.path.join(process.BASE_DIR , "meta.json")
    #     with open(file_path , "w" , encoding="utf-8") as f:
    #         json.dump(meta_data , f , ensure_ascii=False , indent=4)
        
    #     idx+=1  



    


