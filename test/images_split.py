import _path_utils
from crawler.preprocess import image_preprocess_new ,save_segments , get_pil_image_from_url , save_image_as_jpg , make_dir
import json
from tqdm import tqdm 
from crawler.constants import MIN_CONTENT_HEIGHT , MIN_WHITE_GAP , PADDING
from pathlib import Path

# 사용 예시:
# split_rows = get_split_rows("긴_이미지.jpg")
# split_indices = np.where(split_rows)[0]  # True 값의 인덱스 가져오기

#TODO : 실제 JSON 파일 읽어서 여러개의 이미지 분리 해보기, 저장하는 파일 위치는 images/{main_category}/{sub_category}/{product_id} 폴더 안에 저장 
if __name__ == "__main__":
    # JSON 파일을 읽은뒤 진행
    with open("./data/musinsa_product_detail_info.json" , "r" , encoding="utf-8") as f:
        data = json.load(f)
    iterator = tqdm(data[:3] , desc = "image_preprocess")
    for idx2 , data in enumerate(iterator):
        image_detail_url = data["product_detail_images"]
        image_summary_url = data["product_summary_images"]
        product_id = data["product_id"]
        category_main = data["category_main"]
        category_sub = data["category_sub"]
        
        

        save_dir = Path(f"./images/{category_main}/{category_sub}/{product_id}/").absolute()
        make_dir(str(save_dir))
        # 상세  이미지 분리 및 저장
        detail_image_seg = image_preprocess_new(image_detail_url ,min_content_height=MIN_CONTENT_HEIGHT,min_white_gap=MIN_WHITE_GAP,padding=PADDING)
        save_segments(detail_image_seg , save_dir=f"./images/{category_main}/{category_sub}/{product_id}")
        
        # 요약 이미지 처리
        for idx , url in enumerate(image_summary_url):
            summary_image = get_pil_image_from_url(url)
            save_image_as_jpg(summary_image , str(save_dir/ "images" / f"summary_{idx}.jpg"))
        
        
        # save_dir = f"./{product_id}"
        # save_segments(results , save_dir=save_dir)
        # iterator.write(f"product_id : {product_id} 완료")
        
        # 원본 이미지 저장
        # for idx , test_image_url in enumerate(image_url):
        #     test_orgin_image = get_pil_image_from_url(test_image_url)
        #     test_orgin_image_path = f"./test/test_orgin_image_{product_id}_{idx}.jpg"
        #     save_image_as_jpg(test_orgin_image , test_orgin_image_path)
        #     if test_orgin_image.mode =="L":
        #         test_orgin_image = test_orgin_image.convert("RGB")            
            # points = np.array([(test_orgin_image.width//2, idx) for idx, i in enumerate(final) if i])
            # draw_points(test_orgin_image, points)
            # test_orgin_image.save(f"./test_orgin_image_visualize_{product_id}_{idx2}_{idx}.png")
            
            # save_dir = f"./splited_image_{idx2}_{idx}"
            # make_dir(save_dir)
            
    
        
    



    


