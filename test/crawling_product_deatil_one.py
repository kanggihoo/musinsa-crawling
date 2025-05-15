import _path_utils  
from crawler import get_product_detail_info, Crawler

if __name__ == "__main__":
    crawler = Crawler()
    product_id = "2456993"
    result = get_product_detail_info(crawler, product_id)
    print(result)
    crawler.close()