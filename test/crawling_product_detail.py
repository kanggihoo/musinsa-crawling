
import _path_utils  
from crawler import get_product_detail_info, Crawler
import pandas as pd
import json
if __name__ == "__main__":
    crawler = Crawler()
    df = pd.read_csv("musinsa_product_summary.csv")
    columns = ["product_id" ,"product_category_main" , "product_category_sub" , "product_summary_images" ,"product_detail_images","product_details_text","review_texts","color_size_info","crawling_status","success_status"]
    results = []
    for idx , id in enumerate(df["product_id"].tolist()[:10]):
        product_category_main = df.iloc[idx]["product_category_main"]
        product_category_sub = df.iloc[idx]["product_category_sub"]
        result = get_product_detail_info(crawler,id)
        result["product_category_main"] = product_category_main
        result["product_category_sub"] = product_category_sub
        results.append(result)
        
    results_df = pd.DataFrame(results , columns=columns)
    json_data = results_df.to_dict(orient="records")
    with open("musinsa_product_detail_info.json" , "w",encoding="utf-8") as f:
        json.dump(json_data , f , ensure_ascii=False , indent=4)
    
