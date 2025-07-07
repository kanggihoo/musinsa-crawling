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
CATEGORY_MAIN = {
    "상의": "TOP",
    "하의": "BOTTOM",
}

CATEGORY = {
    "상의": {
        # "반소매티셔츠": "001001",
        # "셔츠-블라우스": "001002",
        # "피케-카라티셔츠": "001003",
        # "후드티셔츠": "001004", # 여기 부터 시작하면됨.
        # "맨투맨-스웨트": "001005",
        # "니트-스웨터": "001006",
        # "기타상의": "001008",
        # "긴소매-티셔츠": "001010",
        # "민소매-티셔츠": "001011",
    },
    # "하의":{
    # # 하의 
    #     "데님팬츠" : "003002",
    #     "트레이닝-조거팬츠" : "003004",
    #     "레깅스" : "003005",
    #     "기타하의" : "003006",
    #     "코튼팬츠" : "003007",
    #     "슈트팬츠-슬랙스" : "003008",
    #     "숏팬츠" : "003009",
    #     # "점프슈트-오버울" : "003010",
    # }
}


GENDER = {
    "남성": "M",
    "여성": "F",
    "공용": "U",
}

columns = ["category_main", "category_sub", "gender", "product_id", "product_name", "product_href", "product_price", "product_original_price", "product_discount_price", "product_discount_rate", "product_brand_name", "num_likes", "avg_rating", "review_count", "crawling_status", "success_status"]

crawler = Crawler(headless=False, time_out=10)

SAVE_DIR = Path("./data/")
CHUNK_SIZE = 100  # 한 번에 처리할 데이터 수

try:
    for main_key, sub_categories in CATEGORY.items():
        for sub_key, sub_code in sub_categories.items():
            print(f"crawling {main_key} , {sub_key}")
            
            # 1. 임시 청크 폴더 생성
            chunk_dir = SAVE_DIR / "temp_chunks" / f"{main_key}_{sub_key}"
            chunk_dir.mkdir(parents=True, exist_ok=True)

            url = f"{MUSINSA_BASE_URL}/category/{sub_code}?{urlencode(params)}"
            crawler.go(url)
            _ = crawler.wait_for_element_by_css_selector(".sc-k7xv49-0")

            product_generator = crawl_product_list(crawler, infinite_scroll=True, **{"category_main": CATEGORY_MAIN[main_key], "category_sub": sub_code, "gender": GENDER["남성"]})

            chunk_data = []
            chunk_count = 1
            for product_data in product_generator:
                chunk_data.extend(product_data)
                if len(chunk_data) >= CHUNK_SIZE*6:
                    chunk_df = pd.DataFrame(chunk_data)
                    chunk_file = chunk_dir / f"{chunk_count}.csv"
                    save_dataframe_to_csv(chunk_df, chunk_file)
                    print(f"Saved chunk {chunk_count} for {main_key}/{sub_key}")
                    chunk_data = []
                    chunk_count += 1
            
            # 2. 마지막 남은 데이터 저장
            if chunk_data:
                chunk_df = pd.DataFrame(chunk_data)
                chunk_file = chunk_dir / f"{chunk_count}.csv"
                save_dataframe_to_csv(chunk_df, chunk_file)
                print(f"Saved final chunk {chunk_count} for {main_key}/{sub_key}")

            # 3. 청크 파일들 병합
            print(f"Merging chunks for {main_key}/{sub_key}...")
            chunk_files = sorted(chunk_dir.glob("*.csv"))
            if not chunk_files:
                print(f"No data crawled for {main_key}/{sub_key}. Skipping merge.")
                continue

            dfs = [pd.read_csv(f) for f in chunk_files]
            merged_df = pd.concat(dfs, ignore_index=True)
            
            # 4. 최종 파일 저장 및 임시 폴더 삭제
            final_output_file = SAVE_DIR / f"musinsa_product_summary_{main_key}_{sub_key}_.csv"
            save_dataframe_to_csv(merged_df, final_output_file)
            print(f"Successfully merged and saved data to {final_output_file}")

            shutil.rmtree(chunk_dir)
            print(f"Removed temporary directory: {chunk_dir}")
            break
        break
    # 최종 파일 저장 및 임시 폴더 삭제
    print("모든 크롤링 작업 완료.")

except Exception as e:
    print(f"크롤링 중 오류 발생: {e}")
    print("오류 발생 지점까지의 데이터는 개별 CSV 또는 임시 청크 파일로 저장되어 있을 수 있습니다.")

finally:
    crawler.close()
    print("크롤러가 안전하게 종료되었습니다.")