from urllib.parse import urlencode
import pandas as pd
from crawler import Crawler , crawl_product_list 
from crawler.utils import add_data_to_dataframe , save_dataframe_to_csv

MUSINSA_BASE_URL = "https://www.musinsa.com/"
params = {
    "gf": "M",
    "sortCode":"POPULAR"
}
CATEGORY_SUB = {
    "맨투맨/스웨트": "001005",
}
CATEGORY_MAIN = {
    "상의": "TOP",
    "하의": "BOTTOM",
}
GENDER = {
    "남성": "M",
    "여성": "F",
}

columns = ["category_main" , "category_sub" , "gender" , "product_id" ,"product_name", "product_href" , "product_price" , "product_original_price" , "product_discount_price" , "product_discount_rate", "product_brand_name" , "num_likes" , "avg_rating" , "review_count"]

df = pd.DataFrame(columns=columns)

url = f"{MUSINSA_BASE_URL}category/{CATEGORY_SUB['맨투맨/스웨트']}?{urlencode(params)}"
crawler = Crawler(headless=False)
crawler.go(url)
_ = crawler.wait_for_element_by_css_selector(".sc-k7xv49-0.hRlVQI")

crawled_data = crawl_product_list(crawler , num_scrolls = 5 , **{"category_main":CATEGORY_MAIN["상의"],"category_sub":"맨투맨/스웨트","gender":GENDER["남성"]})
result_df = add_data_to_dataframe(crawled_data , df)
save_dataframe_to_csv(result_df , "musinsa_product_summary_.csv" , index_column="product_id")