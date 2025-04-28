
import _path_utils  
from crawler import get_product_detail_info, Crawler
import pandas as pd
import json
if __name__ == "__main__":
    crawler = Crawler()
    df = pd.read_csv("musinsa_product_summary_.csv")
    columns = ["product_id" , "product_summary_images" ,"product_detail_images","product_details_text","review_texts","color_size_info","crawling_status","success_status"]
    results = []
    for id in df["product_id"].tolist()[:10]:
        result = get_product_detail_info(crawler,id)
        results.append(result)
    results_df = pd.DataFrame(results , columns=columns)
    json_data = results_df.to_dict(orient="records")
    with open("musinsa_product_detail_info.json" , "w",encoding="utf-8") as f:
        json.dump(json_data , f , ensure_ascii=False , indent=4)
    
