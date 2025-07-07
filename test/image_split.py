import _path_utils
from crawler.preprocess import  save_summary_images , ImageData , image_segmentation , save_detail_images , merge_segmented_images
from crawler.utils import setup_logger
from crawler.constants import MIN_CONTENT_HEIGHT , MIN_WHITE_GAP , PADDING
import os
import json
from PIL import Image



    

if __name__ == "__main__":
    # JSON 파일을 읽은뒤 진행
    logger = setup_logger(name ="image_split" , file_name="image_split.log")
    with open("./data/musinsa_product_detail_상의_후드티셔츠_.json" , "r" , encoding="utf-8") as f:
        data = json.load(f)
    
    # data = next(iter(d for d in data if d["product_id"] == "4946821"))
    
    print(len(data))
    # process = ImageData(
    #     product_id=data["product_id"],
    #     summary_images_url=data["summary_images"],
    #     detail_images_url=data["detail_images"],
    #     category_main=data["category_main"],
    #     category_sub=data["category_sub"],
    # )
    
    
    # #TODO : 에러 처리 안되어 있음. 
    # # 요약 이미지 처리
    # save_summary_images(process , logger=logger)

    # # 상세 이미지 처리
    # image_segmentation(process ,logger=logger,min_content_height=MIN_CONTENT_HEIGHT,min_white_gap=MIN_WHITE_GAP,padding=PADDING)
    # save_detail_images(process , logger=logger)
    
    # # # text merged 
    # merge_segmented_images(process.TEXT_IMAGE_DIR)
    
    # 추가 메타 정보도 .json 파일로 저장 
    # meta = {}
    # with open(f"{process.BASE_DIR}/meta.json" , "w" , encoding="utf-8") as f:
    #     meta["product_id"] = data["product_id"]
    #     meta["category_main"] = data["category_main"]
    #     meta["category_sub"] = data["category_sub"]
    #     meta["product_name"] = data["product_name"]
    #     meta["brand_name"] = data["product_brand_name"]
    #     meta["color"] = data["color_size_info"]["color"]
    #     json.dump(meta , f , ensure_ascii=False , indent=4)
    
    
    
    

       
    
        
    



    


