import _path_utils
from crawler.preprocess import image_preprocess,image_preprocess_new ,save_segments , get_pil_image_from_url , save_image_as_jpg
from crawler.visualize.utils import draw_points
from crawler.constants import MIN_CONTENT_HEIGHT , MIN_WHITE_GAP , PADDING
import os
import json
from tqdm import tqdm 
from PIL import Image


if __name__ == "__main__":
    # JSON 파일을 읽은뒤 진행
    with open("./data/musinsa_product_detail_info.json" , "r" , encoding="utf-8") as f:
        data = json.load(f)
    
    data = next(iter(d for d in data if d["product_id"] == "4946821"))
    image_summary_url = data["product_summary_images"]
    image_detail_url = data["product_detail_images"]
    product_id = data["product_id"]
    category_main = data["category_main"]
    category_sub = data["category_sub"]
    save_dir = f"./images/{category_main}/{category_sub}/{product_id}/images/"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    # 요약 이미지 처리
    for idx , url in enumerate(image_summary_url):
        print(product_id)
        summary_image = get_pil_image_from_url(url)
        save_image_as_jpg(summary_image , save_dir+f"summary_{idx}.jpg")
        
    # 상세 이미지 처리
    detail_image_seg = image_preprocess_new(image_detail_url ,min_content_height=MIN_CONTENT_HEIGHT,min_white_gap=MIN_WHITE_GAP,padding=PADDING)
    save_segments(detail_image_seg , save_dir=f"./images/{category_main}/{category_sub}/{product_id}/")
    
    
    
        # img = get_pil_image_from_url(url)
        # segments = split_image(img , min_content_height=8, min_white_gap=8, padding=0)
        # white_rows = get_white_rows(img)
        # content_regions = find_content_regions(white_rows)
        # segments = process_content_regions(content_regions , img.height , min_content_height=8, min_white_gap=8, padding=5)
        # segments = split_image_by_white_rows(img , white_rows , min_white_band=5, min_image_height=10)
        # for i, seg in enumerate(segments):
        #     is_text = is_wide_image(seg)
        #     segment_obj = ProcessedImageSegment(
        #         pil_image=seg,
        #         original_url=image_detail_url,
        #         segment_index=i,
        #         is_text_segment=is_text,
        #         segment_id=idx
        #             )
        #     processed_segments.append(segment_obj)
    # save_dir = f"./{product_id}"
    # save_segments(processed_segments , save_dir=save_dir)
    
       
    
        
    



    


