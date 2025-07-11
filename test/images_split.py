import _path_utils
from crawler.preprocess import save_summary_images , ImageData , image_segmentation , save_detail_images , merge_segmented_images
import json
from crawler.constants import MIN_CONTENT_HEIGHT , MIN_WHITE_GAP , PADDING
from crawler.utils import setup_logger
from tqdm import tqdm
import os


if __name__ == "__main__":
    # JSON 파일을 읽은뒤 진행
    logger = setup_logger(name ="image_split" , file_name="image_split.log")
    with open("./data/musinsa_product_detail_상의_셔츠-블라우스.json" , "r" , encoding="utf-8") as f:
        data = json.load(f)
    
    # data = next(iter(d for d in data if d["product_id"] == "4946821"))
    idx = 1
    for d in tqdm(data, desc="Processing products"):
        product_name = d["product_name"]
        if "set" in product_name.lower() or "package" in product_name.lower():
            continue
        process = ImageData(
            product_id=d["product_id"],            summary_images_url=d["summary_images"],
            detail_images_url=d["detail_images"],
            category_main=d["category_main"],
            category_sub=d["category_sub"],
            target_size=720
        )
        
        
        #TODO : 에러 처리 안되어 있음. 
        # 요약 이미지 처리
        save_summary_images(process , logger=logger)

        # 상세 이미지 처리t
        image_segmentation(process ,logger=logger,min_content_height=MIN_CONTENT_HEIGHT,min_white_gap=MIN_WHITE_GAP,padding=PADDING)
        save_detail_images(process , logger=logger)
        
        # # text merged 
        merge_segmented_images(process.TEXT_IMAGE_DIR , process.target_size)
        
        #TODO : 색상 메타 정보 더 추가 (사람이 확인하는 과정에서 제외할 데이터 판단 여부?)
        # 제품 메타 정보 저장(json)
        meta_data = {
            "product_id": d["product_id"],
            "product_name" : d["product_name"],
            "brand_name" : d["product_brand_name"],
            "category_main": d["category_main"],
            "category_sub": d["category_sub"],
            "color_info" : d["color_size_info"].get("color" , "No 'color' key"),
            "size_info" : d["color_size_info"].get("size" , "No 'size' key"),
            "price" : d["product_price"],
            "num_likes" : d["num_likes"],
            "review_count" : d["review_count"],
            "avg_rating" : d["avg_rating"],
            "description" : d["detail_text"],
            "is_size_detail_info" : True if d["size_detail_info"] else False,
            "recommendation_order" : idx
        }
        
        file_path = os.path.join(process.BASE_DIR , "meta.json")
        with open(file_path , "w" , encoding="utf-8") as f:
            json.dump(meta_data , f , ensure_ascii=False , indent=4)
        
        idx+=1  



    


