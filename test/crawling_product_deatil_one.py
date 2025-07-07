import _path_utils  
from crawler import get_product_detail_info, Crawler
from crawler.utils import setup_logger
from selenium.common.exceptions import NoAlertPresentException


if __name__ == "__main__":
    logger = setup_logger(file_name="crawling_product_deatil_one.log")
    crawler = Crawler(base_url = "https://www.musinsa.com/products")
    product_id = "3085938"
    
    
    try:
        result = get_product_detail_info(crawler, product_id , logger)
        if result['success_status'] != 'success':
            logger.error("\n")
        else:
            logger.info(result)
    except Exception as e:
        logger.error(f"Error while crawling product ID {product_id}: {str(e)}")
    finally:
        crawler.close()
