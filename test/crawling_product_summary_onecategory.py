import _path_utils  
from urllib.parse import urlencode
import pandas as pd
from crawler import Crawler, crawl_product_list
from crawler.utils import save_dataframe_to_csv
from pathlib import Path
import shutil

MUSINSA_BASE_URL = "https://www.musinsa.com"
params = {
    "gf": "M",
    "sortCode": "POPULAR"
}
CATEGORY_MAIN_TO_STR = {
    "TOP": "상의",
    "BOTTOM": "하의",
}

CATEGORY_SUB_CODE_TO_STR = {
    "001001": "반소매티셔츠",
    "001002": "셔츠-블라우스",
    "001003": "피케-카라티셔츠",
    "001004": "후드티셔츠",
    "001005": "맨투맨-스웨트",
    "001006": "니트-스웨터",
    "001008": "기타상의",
    "001010": "긴소매티셔츠",
    "001011": "민소매티셔츠",

    "003002": "데님팬츠",
    "003004": "트레이닝-조거팬츠",
    "003005": "레깅스",
    "003006": "기타하의",
    "003007": "코튼팬츠",
    "003008": "슈트팬츠-슬랙스",
    "003009": "숏팬츠",
    "003010": "점프슈트-오버울",
}

CATEGORY = [
    {"category_main": "TOP", "category_sub": "001001"}, # 반소매티셔츠 (실제 무신사랑 13000개 정도 부족) - 73646 - 
    {"category_main": "TOP", "category_sub": "001002"}, # 셔츠-블라우스 (실제 무신사랑 데이터 수 일치) - 21228 - 
    {"category_main": "TOP", "category_sub": "001003"}, # 피케-카라티셔츠 (실제 무신사랑 데이터 수 일치) - 10127 - 
    {"category_main": "TOP", "category_sub": "001004"}, # 후드티셔츠 (실제 무신사랑 데이터 수 일치) - 25372 - 
    {"category_main": "TOP", "category_sub": "001005"}, # 맨투맨-스웨트 (실제 무신사랑 데이터 수 일치) -29758-
    {"category_main": "TOP", "category_sub": "001006"}, # 니트-스웨터 (실제 무신사랑 데이터 수 일치) - 16242 - 
    {"category_main": "TOP", "category_sub": "001008"}, # 기타상의 (실제 무신사랑 데이터 수 일치) - 1869 -
    {"category_main": "TOP", "category_sub": "001010"}, # 긴소매-티셔츠 (실제 무신사랑 데이터 수 일치) - 14369 - 
    {"category_main": "TOP", "category_sub": "001011"}, # 민소매-티셔츠 (실제 무신사랑 데이터 수 일치) - 3381 - 
    {"category_main": "BOTTOM", "category_sub": "003002"}, # 데님팬츠 (실제 무신사랑 3000개 데이터 수 부족) -14115 - 
    {"category_main": "BOTTOM", "category_sub": "003004"}, # 트레이닝-조거팬츠 (실제 무신사랑 데이터 수 일치) -17760-
    {"category_main": "BOTTOM", "category_sub": "003005"}, # 레깅스
    {"category_main": "BOTTOM", "category_sub": "003006"}, # 기타하의
    {"category_main": "BOTTOM", "category_sub": "003007"}, # 코튼팬츠
    {"category_main": "BOTTOM", "category_sub": "003008"}, # 슈트팬츠-슬랙스
    {"category_main": "BOTTOM", "category_sub": "003009"}, # 숏팬츠
    {"category_main": "BOTTOM", "category_sub": "003010"}, # 점프슈트-오버울
]


GENDER = {
    "남성": "M",
    "여성": "F",
    "공용": "U",
}

columns = ["category_main", "category_sub", "gender", "product_id", "product_name", "product_href", "product_price", "product_original_price", "product_discount_price", "product_discount_rate", "product_brand_name", "num_likes", "avg_rating", "review_count", "crawling_status", "success_status"]

crawler = Crawler(headless=False, time_out=15)

SAVE_DIR = Path("./data")
CHUNK_SIZE = 100  # 한 번에 처리할 데이터 수

try:
    category = CATEGORY[10]
    main_code , sub_code = category.get("category_main") , category.get("category_sub")
    
            
    # 1. 임시 청크 폴더 생성
    chunk_dir = SAVE_DIR / "temp_chunks" / f"{main_code}_{sub_code}"
    chunk_dir.mkdir(parents=True, exist_ok=True)

    url = f"{MUSINSA_BASE_URL}/category/{sub_code}?{urlencode(params)}"
    crawler.go(url)
    _ = crawler.wait_for_element_by_css_selector(".sc-k7xv49-0")

    product_generator = crawl_product_list(crawler, infinite_scroll=True, **{"category_main": main_code, "category_sub": sub_code, "gender": GENDER["남성"]})

    chunk_data = []
    chunk_count = 1
    for product_data in product_generator:
        chunk_data.extend(product_data)
        if len(chunk_data) >= CHUNK_SIZE*6:
            chunk_df = pd.DataFrame(chunk_data)
            chunk_file = chunk_dir / f"{chunk_count}.csv"
            save_dataframe_to_csv(chunk_df, chunk_file)
            print(f"Saved chunk {chunk_count} for {main_code}/{sub_code}")
            chunk_data = []
            chunk_count += 1
    
    # 2. 마지막 남은 데이터 저장
    if chunk_data:
        chunk_df = pd.DataFrame(chunk_data)
        chunk_file = chunk_dir / f"{chunk_count}.csv"
        save_dataframe_to_csv(chunk_df, chunk_file)
        print(f"Saved final chunk {chunk_count} for {main_code}/{sub_code}")

    # 3. 청크 파일들 병합
    print(f"Merging chunks for {main_code}/{sub_code}...")
    chunk_files = sorted(chunk_dir.glob("*.csv"))
    if not chunk_files:
        raise Exception(f"No data crawled for {main_code}/{sub_code}. Skipping merge.")

    dfs = [pd.read_csv(f) for f in chunk_files]
    merged_df = pd.concat(dfs, ignore_index=True)
    
    # 4. 최종 파일 저장 및 임시 폴더 삭제
    final_output_file = SAVE_DIR / f"musinsa_product_summary_{CATEGORY_MAIN_TO_STR[main_code]}_{CATEGORY_SUB_CODE_TO_STR[sub_code]}.csv"
    save_dataframe_to_csv(merged_df, final_output_file)
    print(f"Successfully merged and saved data to {final_output_file}")

    shutil.rmtree(chunk_dir)
    print(f"Removed temporary directory: {chunk_dir}")

except Exception as e:
    print(f"크롤링 중 오류 발생: {e}")
    print("오류 발생 지점까지의 데이터는 개별 CSV 또는 임시 청크 파일로 저장되어 있을 수 있습니다.")

finally:
    crawler.close()
    print("크롤러가 안전하게 종료되었습니다.")