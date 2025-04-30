import _path_utils  
from urllib.parse import urlencode
import pandas as pd
from crawler import Crawler , crawl_product_list 
from crawler.utils import add_data_to_dataframe , save_dataframe_to_csv

MUSINSA_BASE_URL = "https://www.musinsa.com"
params = {
    "gf": "M",
    "sortCode":"POPULAR"
}
CATEGORY_MAIN = {
    "상의": "TOP",
    "하의": "BOTTOM",
}
CATEGORY = {
    "상의":{
    # 상의 
        "반소매 티셔츠": "001001",
        "셔츠/블라우스": "001002",
        "피케/카라 티셔츠": "001003",
        "후드 티셔츠": "001004",
        "맨투맨/스웨트": "001005",
        "니트/스웨터": "001006",
        "기타 상의": "001008",
        "긴소매 티셔츠": "001010",
        "민소매 티셔츠": "001011",
    },
    "하의":{
    # 하의 
        "데님팬츠" : "003002",
        "트레이닝/조거팬츠" : "003004",
        "레깅스" : "003005",
        "기타하의" : "003006",
        "코튼팬츠" : "003007",
        "슈트 팬츠/슬랙스" : "003008",
        "숏 팬츠" : "003009",
        "점프슈트/오버울" : "003010",
    }
}



GENDER = {
    "남성": "M",
    "여성": "F",
    "공용": "U",
}

columns = ["category_main" , "category_sub" , "gender" , "product_id" ,"product_name", "product_href" , "product_price" , "product_original_price" , "product_discount_price" , "product_discount_rate", "product_brand_name" , "num_likes" , "avg_rating" , "review_count" , "crawling_status" , "success_status"]

df = pd.DataFrame(columns=columns)
crawler = Crawler(headless=False)

#TODO : 무한 스크롤시 오류 인지 아니면 다른 오류 처리를 못한건지(아마 무한 스크롤리 문제 생기거 같은데)
try:
    for main_key in CATEGORY.keys():
        main_category_data = []  # 각 메인 카테고리의 데이터를 임시 저장
        
        for sub_key in CATEGORY[main_key].keys():
            print(f"crawling {main_key} , {sub_key}")
            url = f"{MUSINSA_BASE_URL}/category/{CATEGORY[main_key][sub_key]}?{urlencode(params)}"
            crawler.go(url)
            _ = crawler.wait_for_element_by_css_selector(".sc-k7xv49-0.hRlVQI")

            crawled_data = crawl_product_list(crawler, infinite_scroll=True, **{"category_main": CATEGORY_MAIN[main_key],"category_sub": CATEGORY[main_key][sub_key],"gender": GENDER["남성"]})
            
            # 소분류 데이터를 바로 저장
            print(f"crawling {main_key} , {sub_key} 완료. 데이터 저장 중...")
            sub_category_df = pd.DataFrame(crawled_data)
            save_dataframe_to_csv(
                sub_category_df, 
                f"musinsa_product_summary_{main_key}_{sub_key}_.csv", 
                index_column="product_id"
            )
            del sub_category_df  # 메모리 해제
            print(f"{main_key} - {sub_key} 카테고리 데이터 저장 완료")
            
            # 파일 경로 저장
            main_category_data.append(f"musinsa_product_summary_{main_key}_{sub_key}_.csv")
            break
        break
        # 메인 카테고리의 모든 CSV 파일을 병합
        print(f"{main_key} 카테고리 전체 데이터 병합 중...")
        main_dfs = []
        for csv_file in main_category_data:
            temp_df = pd.read_csv(csv_file)
            main_dfs.append(temp_df)
            del temp_df  # 메모리 해제
        
        main_category_df = pd.concat(main_dfs, ignore_index=True)
        save_dataframe_to_csv(
            main_category_df, 
            f"musinsa_product_summary_{main_key}_all_.csv", 
            index_column="product_id"
        )
        del main_dfs, main_category_df  # 메모리 해제
        print(f"{main_key} 카테고리 전체 데이터 저장 완료")

    # 최종적으로 모든 메인 카테고리 CSV 파일을 병합
    print("전체 데이터 병합 중...")
    final_dfs = []
    for main_key in CATEGORY.keys():
        temp_df = pd.read_csv(f"musinsa_product_summary_{main_key}_all_.csv")
        final_dfs.append(temp_df)
        del temp_df  # 메모리 해제
    
    final_df = pd.concat(final_dfs, ignore_index=True)
    save_dataframe_to_csv(final_df, "musinsa_product_summary_final_.csv", index_column="product_id")
    del final_dfs, final_df  # 메모리 해제
    print("전체 데이터 저장 완료")

except Exception as e:
    print(f"크롤링 중 오류 발생: {e}")
    # 현재 진행 중이던 작업 상태 저장
    print("오류 발생 지점까지의 데이터는 개별 CSV 파일로 저장되어 있습니다.")

finally:
    crawler.close()
    print("크롤러가 안전하게 종료되었습니다.")