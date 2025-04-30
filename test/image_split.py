import _path_utils
from crawler.preprocess import image_preprocess ,save_segments 
import json
from tqdm import tqdm 

# 사용 예시:
# split_rows = get_split_rows("긴_이미지.jpg")
# split_indices = np.where(split_rows)[0]  # True 값의 인덱스 가져오기


if __name__ == "__main__":
    with open("musinsa_product_detail_info.json" , "r" , encoding="utf-8") as f:
        data = json.load(f)
    iterator = tqdm(data[0:1] , desc = "image_preprocess" )
    for idx2 , data in enumerate(iterator):
        image_url = data["product_detail_images"]
        product_id = data["product_id"]
        results = image_preprocess(image_url ,min_white_band=5,min_segment_height=10)
        
        save_dir = f"./{product_id}"
        save_segments(results , save_dir=save_dir)
        iterator.write(f"product_id : {product_id} 완료")
        # 원본 이미지 저장
        # for idx , test_image_url in enumerate(image_url):
            # test_orgin_image = get_pil_image_from_url(test_image_url)
            # test_orgin_image_path = f"./test/test_orgin_image_{product_id}_{idx}.jpg"
            # save_image_as_jpg(test_orgin_image , test_orgin_image_path)
            # if test_orgin_image.mode =="L":
            #     test_orgin_image = test_orgin_image.convert("RGB")            
            # points = np.array([(test_orgin_image.width//2, idx) for idx, i in enumerate(final) if i])
            # draw_points(test_orgin_image, points)
            # test_orgin_image.save(f"./test_orgin_image_visualize_{product_id}_{idx2}_{idx}.png")
            
            # save_dir = f"./splited_image_{idx2}_{idx}"
            # make_dir(save_dir)
            
    
        
    



    


