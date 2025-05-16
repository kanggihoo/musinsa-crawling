from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Optional , List , Dict
from bs4 import BeautifulSoup
import time
from selenium.webdriver.remote.webelement import WebElement

COLUMNS = ["category_main" , "category_sub" , "gender" , "product_id" ,"product_name", "product_href" ,"product_price" , "product_original_price" , "product_discount_price" , "product_discount_rate", "product_brand_name" , "num_likes" , "avg_rating" , "review_count"]
class Crawler:
    def __init__(self, headless=False , base_url:Optional[str]=None , error_message:str = "failed"):
        self.base_url = base_url
        self.driver = None
        self.headless = headless
        self.error_message = error_message
        self.setup_driver()
    
    def setup_driver(self):
        """웹드라이버 설정"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")
        
        # chrome_options.add_argument("--no-sandbox")
        # chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1600,1080")
        chrome_options.add_argument("--disable-notifications")
        
        # 자동화 감지 방지
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_argument("disable-blink-features=AutomationControlled")
        
        # User-Agent 설정
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36")
        
        # service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 5 , poll_frequency=0.5)
    
    def go(self , url:str):
        self.driver.get(url)
    
    def click_element_by_css_selector(self, css_selector):
        """
        CSS 셀렉터를 사용하여 요소를 검색한 후 클릭합니다.
        
        Args:
            css_selector (str): 클릭할 요소의 CSS 셀렉터
        """
        try:
            # 요소가 로드될 때까지 대기
            element = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))
            )
            # 요소 클릭
            element.click()
        except Exception as e:
            print(f"요소 클릭 중 오류 발생: {e}")
            return self.error_message
    
    def scroll_from_start_to_end(self, start:int , end:int):
        self.driver.execute_script(f"window.scrollTo({start}, {end});")
        
    def wait_for_element_by_css_selector(self, css_selector:str):
        try:
            element = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
            )
            # print("요소 로드 완료")
            return element
        except Exception as e:
            print(f"요소 로드 대기 중 오류 발생: {e}")
            return self.error_message
        
    def wait_for_element_by_xpath(self, xpath:str):
        try:
            element = self.wait.until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            return element
        except Exception as e:
            print(f"요소 로드 대기 중 오류 발생: {e}")
            return self.error_message
    def wait_for_attribute_change_in_parent(self, parent_element:WebElement, value:str=None, attribute:str="data-state", target_value:str="open"):
        try:
            # 먼저 요소를 찾음
            element = parent_element.find_element(By.CSS_SELECTOR, f":scope {value}")
            
            # 속성 변경을 기다림
            def condition(driver):
                try:
                    return element.get_attribute(attribute) == target_value
                except:
                    return False
            
            # 조건이 만족되면 element를 반환
            self.wait.until(condition)
            return element
            
        except Exception as e:
            print(f"요소 로드 대기 중 오류 발생: {e}")
            return self.error_message
    def wait_for_clickable_element(self, element:WebElement):
        
        self.wait.until(
            EC.element_to_be_clickable(element)
        )
        element.click()    
            
    def click_and_type(self, css_selector, text , enter=True):
        """
        특정 위치에 클릭한 후 텍스트를 입력하고 엔터 키를 누릅니다.
        
        Args:
            css_selector (str): 클릭할 요소의 CSS 셀렉터
            text (str): 입력할 텍스트
        """
        try:
            # 요소가 로드될 때까지 대기
            element = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))
            )
            # 요소 클릭
            element.click()
            
            # 텍스트 입력
            element.send_keys(text)
            
            if enter:
                # 엔터 키 입력
                element.send_keys(Keys.ENTER)
            
        except Exception as e:
            print(f"클릭 및 입력 중 오류 발생: {e}")
            return self.error_message

    def close(self):
        """웹드라이버를 안전하게 종료합니다."""
        try:
            if self.driver:
                self.driver.quit()
                print("웹드라이버가 안전하게 종료되었습니다.")
        except Exception as e:
            print(f"웹드라이버 종료 중 오류 발생: {e}")

def fill_default_value(product_data:Dict , columns:List[str] , crawling_status:str)->Dict:
    for column in columns:
        product_data[column] = crawling_status

def fill_value(product_data:Dict , **kwargs)->Dict:
    for key , value in kwargs.items():
        product_data[key] = value

def get_one_product_info(item :BeautifulSoup ,  **params)->Dict :
    product_data = {}
    product_data["crawling_status"] = {"image_section":"success" , "detail_section":"success"}
    try:
        # image section 추출 
        image_section = item.select_one(".sc-jPkiSJ a")   
         
        product_id = image_section.get("data-item-id")
        product_href = image_section.get("href")
        product_price = image_section.get("data-price")
        product_original_price = image_section.get("data-original-price")
        product_discount_price = image_section.get("data-discount")
        product_discount_rate = image_section.get("data-discount-rate")
        product_brand_name = image_section.get("data-brand-id")
        fill_value(product_data , product_id = product_id , product_href = product_href , product_price = product_price , product_original_price = product_original_price , product_discount_price = product_discount_price , product_discount_rate = product_discount_rate , product_brand_name = product_brand_name)
    except Exception as e:
        print(f"상품 정보 image section 추출 중 오류 발생: {e}")
        fill_default_value(product_data , ["product_id" , "product_href" , "product_price" , "product_original_price" , "product_discount_price" , "product_discount_rate" , "product_brand_name"] , "failed")
        product_data["crawling_status"]["image_section"] = "failed"
        
    try:
    # detail section 추출 
        detail_section = item.select_one(".sc-dZEakj.iDBPjO")
        product_name_element = detail_section.select_one(".sc-cNFqVt.dhrvja a:nth-child(2)")
        product_name = product_name_element.text if product_name_element else None
    
        # 요소가 없을 경우 None을 반환하는 함수 
        def get_text_or_default(selector, default=None):
            element = detail_section.select_one(selector)
            return element.text if element else default
        
        #REVIEW 추출을 하는데 None을 집어넣으면 진짜 없는건지 , 크롤링 실패한건지 구분이 안될거 같은데 
        # 각 요소 안전하게 가져오기
        num_likes = get_text_or_default(".sc-fpEFIB.fHfJGx div:nth-child(1) span", None)
        avg_rating = get_text_or_default(".sc-fpEFIB.fHfJGx div:nth-child(2) span:nth-child(1)", None)
        review_count = get_text_or_default(".sc-fpEFIB.fHfJGx div:nth-child(2) span:nth-child(2)", None)
    
    # 데이터 반환
        fill_value(product_data , product_name = product_name , num_likes = num_likes , avg_rating = avg_rating , review_count = review_count)
        fill_value(product_data , **params)
        product_data["crawling_status"]["detail_section"] = "success"
        if all([True if i == "success" else False for i in product_data["crawling_status"].values()]):
            product_data["success_status"] = "success"
        else:
            product_data["success_status"] = "failed"
            
    except Exception as e:
        print(f"상품 정보 detail section 추출 중 오류 발생: {e}")
        fill_default_value(product_data , ["product_name" , "num_likes" , "avg_rating" , "review_count"] , "failed")
        product_data["crawling_status"]["detail_section"] = "failed"
        product_data["success_status"] = "failed"

    return product_data

def get_row_product_info(soup:BeautifulSoup  , **params) -> List[Dict]:
        # target_element = soup.select_one(f'div[data-index="{page_index}"]')
        # assert target_element is not None , f"{page_index} 페이지 로드 실패"
        product_list = []
        for item in soup.select(".sc-jnflPq.kUzqzX"):
            product_data = get_one_product_info(item , **params)
            product_list.append(product_data)
        
        return product_list
    
def crawl_product_list(crawler:Crawler , num_scrolls:int=None , dy:int=462, infinite_scroll:bool=False, **params)->List[Dict]:
    start , end = 0 , dy
    scroll_count = 0
    crawled_data = []
    last_height = crawler.driver.execute_script("return document.body.scrollHeight")
    
    while True:
        try:
            target_element = crawler.wait_for_element_by_css_selector(f".sc-k7xv49-0.hRlVQI div[data-index='{scroll_count}']")
        except:
            print(f"더 이상 크롤링할 상품이 없습니다. 총 {scroll_count}번의 스크롤 진행.")
            break
            
        soup = BeautifulSoup(target_element.get_attribute("innerHTML"), "html.parser")
        
        product_list = get_row_product_info(soup, **params)
        crawled_data.extend(product_list)
        
        crawler.scroll_from_start_to_end(start , end)
        time.sleep(0.2)
        # 스크롤 후 새로운 컨텐츠가 로드될 때까지 대기
        new_height = crawler.driver.execute_script("return document.body.scrollHeight") 
        
        # 다음 인덱스의 요소가 나타날 때까지 대기
        next_element = crawler.wait_for_element_by_css_selector(f".sc-k7xv49-0.hRlVQI div[data-index='{scroll_count+1}']")
        if next_element != crawler.error_message:
            pass
        else:
            print("다음 인덱스 요소 없음")
            if new_height == last_height:
                print(f"페이지 끝에 도달했습니다. 총 {scroll_count + 1}번의 스크롤 진행.")
                break
            else:
                print(new_height , last_height , product_list)
                print(f"페이지 끝에 도달하지 않았습니다. 총 {scroll_count + 1}번의 스크롤 진행.")
        
        time.sleep(0.1)
        start , end = end , end + dy
        scroll_count += 1
        last_height = new_height
        
        # 무한 스크롤이 아니고 지정된 스크롤 수에 도달한 경우
        if not infinite_scroll and num_scrolls is not None and scroll_count >= num_scrolls:
            break
        
    return crawled_data

#FIXME : 코드 가동성 필요(리팩토링)
#TODO : 의류 사이즈 정보 추출하는 코드 작성 필요.
def get_product_detail_info(crawler:Crawler , product_id:str, is_process:bool = False ):
    test_url = f"https://www.musinsa.com/products/{product_id}"
    crawler.go(test_url)

    # Initialize data variables and status
    summary_images = []
    detail_text = {}
    detail_images = []
    review_texts = None
    color_size_info = {}
    crawling_status = {
        "summary_images": "failed",
        "detail_text": "failed",
        "detail_images": "failed",
        "reviews": "failed",
        "color_size": "failed"
    }

    # 1. 제품 preview 이미지 url 추출
    try:
        product_summary = crawler.wait_for_element_by_css_selector(".sc-366fl4-1.hJTemd.scroll-container .sc-366fl4-2.dYGXwS")
        if product_summary != crawler.error_message:
            product_summary_soup = BeautifulSoup(product_summary.get_attribute("innerHTML") , "html.parser")
            for image in product_summary_soup.select("img"):
                summary_images.append(image.get("src"))
            crawling_status["summary_images"] = "success"
        else:
            summary_images = crawler.error_message # Ensure failed status propagates
            print(f"크롤링 실패 [Section 1]: 제품 preview 이미지 url 추출 실패 (wait_for_element)")
    except Exception as e:
        print(f"크롤링 실패 [Section 1]: 제품 preview 이미지 url 추출 중 오류 발생 - {e}")
        summary_images = crawler.error_message

    # 2. 제품 detail 영역에서 text 정보 추출(성별 , 시즌 , 조회수 등)
    try:
        product_details_element = crawler.wait_for_element_by_css_selector("#root .sc-1bn3xag-2.uTRuH")
        if product_details_element != crawler.error_message:
            product_details_soup = BeautifulSoup(product_details_element.get_attribute("innerHTML") , "html.parser")
            
            for e in product_details_soup.select(".sc-2ll6b5-1.dhVuFE:not(:first-child)"):
                key_element = e.select_one("dt")
                value_element = e.select_one("dd")
                if key_element and value_element:
                    key = key_element.text
                    value = value_element.text
                    detail_text[key]= value
            crawling_status["detail_text"] = "success"
        else:
             print(f"크롤링 실패 [Section 2]: 제품 detail 영역 추출 실패 (wait_for_element)")
             detail_text = crawler.error_message # Ensure failed status propagates
    except Exception as e:
        print(f"크롤링 실패 [Section 2]: 제품 detail 영역에서 text 정보 추출 중 오류 발생 - {e}")
        detail_text = crawler.error_message

    # 3. 제품과 관련된 자세한 image url 추출
    try:
        # Reuse product_details_soup if available and Section 2 succeeded
        if crawling_status["detail_text"] == "success" and product_details_element != crawler.error_message:
             # Re-parse just in case, although ideally reuse product_details_soup
            product_details_soup_for_images = BeautifulSoup(product_details_element.get_attribute("innerHTML") , "html.parser")
            for image in product_details_soup_for_images.select("div:last-child img"):
                 image_url = image.get("src")
                 detail_images.append(image_url)
            crawling_status["detail_images"] = "success"
        elif product_details_element == crawler.error_message:
             print(f"크롤링 실패 [Section 3]: 제품 상세 이미지 추출 실패 (Section 2 실패로 인한 의존성)")
             detail_images = crawler.error_message
        else: # Attempt to refetch if section 2 failed but element might be available
            product_details_refetch = crawler.wait_for_element_by_css_selector("#root .sc-1bn3xag-2.uTRuH")
            if product_details_refetch != crawler.error_message:
                product_details_soup_refetch = BeautifulSoup(product_details_refetch.get_attribute("innerHTML") , "html.parser")
                for image in product_details_soup_refetch.select("div:last-child img"):
                     image_url = image.get("src")
                     detail_images.append(image_url)
                crawling_status["detail_images"] = "success"
            else:
                 print(f"크롤링 실패 [Section 3]: 제품 상세 이미지 추출 실패 (Refetch 실패)")
                 detail_images = crawler.error_message

    except Exception as e:
        print(f"크롤링 실패 [Section 3]: 제품과 관련된 자세한 image url 추출 중 오류 발생 - {e}")
        detail_images = crawler.error_message


    # 4. 제품 리뷰 내용 추출
    try:
        product_reviews = crawler.wait_for_element_by_css_selector("#root > div.sc-3weaze-0.gwbpgC .goods-reviewpage__Container-sc-1iio9o6-0.bzkkZg")
        if product_reviews != crawler.error_message:
            product_reviews_soup = BeautifulSoup(product_reviews.get_attribute("innerHTML") , "html.parser")
            is_review_exist = len(product_reviews_soup.find_all("div", recursive=False)) >= 3

            if is_review_exist:
                review_text_list = []
                review_items = product_reviews_soup.select(".GoodsReviewListSection__Container-sc-1x35scp-0 .review-list-item__Container-sc-13zantg-0")
                max_reviews_to_crawl = min(10, len(review_items))

                for idx, review in enumerate(review_items):
                    if idx >= max_reviews_to_crawl:
                        break
                    review_text_area = review.select_one(".ReviewImageContentSection__Container-sc-1lff2fc-0 > .ExpandableContent__Container-sc-gj5b23-0 .Truncate__MeasureContainer-sc-5dnpga-0")
                    if review_text_area:
                        first_span = review_text_area.select_one("span:first-child")
                        if first_span and "class" in first_span.attrs:
                             is_month_label = "MonthLabel" in first_span["class"][0]
                        else:
                             is_month_label = False # Default if structure is unexpected

                        if is_month_label:
                            review_text = []
                            spans = review_text_area.find_all("span", recursive=False)
                            for span_idx, span in enumerate(spans):
                                review_text.append(span.text.strip())
                                if span_idx >= 1: # Get first two spans (month label + review)
                                    break
                            review_text_list.append(" ".join(review_text))
                        elif first_span: # Regular review text
                            review_text_list.append(first_span.text.strip())
                        # else: Skip if structure doesn't match
                    # else: Skip review if text area not found
                review_texts = "\n".join(review_text_list) if review_text_list else None
                crawling_status["reviews"] = "success"
            else:
                review_texts = None # No reviews exist
                crawling_status["reviews"] = "success" # Mark as success since no reviews is not an error
        else:
             print(f"크롤링 실패 [Section 4]: 제품 리뷰 영역 추출 실패 (wait_for_element)")
             review_texts = crawler.error_message
    except Exception as e:
        print(f"크롤링 실패 [Section 4]: 제품 리뷰 내용 추출 중 오류 발생 - {e}")
        review_texts = crawler.error_message
    #REVIEW : 굳이 제품 색상별 사이즈 정보를 추출해야 하나??? (어차피 나중에 재고 있는지 여부는 나중에 매번 확인해야 하는데?)
    #TODO 색상이 어떤게 있는지와 사이즈 정보만 추출 하는게 좋아보이는데 
    # 5. 제품 색상 및 색상별 사이즈 정보 추출
    try:
        
        select_area = crawler.wait_for_element_by_css_selector(".sc-1puoja0-0.fZdNIF .gtm-impression-content .pt-1.pb-2")
        if select_area != crawler.error_message:
            # Use find_elements which returns a list, empty if not found
            child_divs = select_area.find_elements(By.CSS_SELECTOR, ":scope > div")
            is_one_color = len(child_divs) <= 1 # Check if 0 or 1 child div

            # 누르는 버튼이 2개 이상인경우 (사이즈 , 색상 정보 모두 있음.)
            if not is_one_color and len(child_divs) >= 2: # Need at least 2 divs for multiple colors scenario
                first_select_area = child_divs[0] # Use the found elements
                second_select_area = child_divs[1]

                crawler.wait_for_clickable_element(first_select_area) # Wait and click
                
                colors_element = crawler.wait_for_attribute_change_in_parent(first_select_area , value=".static-dropdown-menu > div:nth-child(2)" , attribute="data-state" , target_value="open")
                if colors_element != crawler.error_message:
                    color_soup = BeautifulSoup(colors_element.get_attribute("innerHTML") , "html.parser")
                    color_names = []

                    for color in color_soup.select(".sc-102tdfw-1"):
                        color_name_span = color.select_one("span")
                        if color_name_span:
                            color_name = color_name_span.text.strip()
                            color_size_info[color_name] = {}
                            color_names.append(color_name)

                    # Get size info for each color
                    for idx in range(len(color_names)):
                        crawler.wait_for_clickable_element(select_area.find_elements(By.CSS_SELECTOR , f".sc-102tdfw-1:nth-child({idx+1})")[0])
                        crawler.wait_for_clickable_element(second_select_area)
                        
                        sizes = crawler.wait_for_attribute_change_in_parent(second_select_area , value=".static-dropdown-menu > div:nth-child(2)" , attribute="data-state" , target_value="open")
                        if sizes != crawler.error_message:
                            size_soup = BeautifulSoup(sizes.get_attribute("innerHTML") , "html.parser")
                            current_color_name = color_names[idx]
                            for size in size_soup.select(".sc-102tdfw-1"):
                                text = size.select_one("span").text.strip()
                                text_split = text.split()
                                if text_split: # Ensure there's text
                                    size_key = text_split[0] if text_split[0] not in ["기모", "노기모"] else (text_split[1] if len(text_split) > 1 else text_split[0])
                                    color_size_info[current_color_name][size_key] = "soldout" if len(text_split) >= 2 and text_split[-1] == "(품절)" else "available"
                    
                        else:
                             print(f"크롤링 실패 [Section 5]: '{color_names[idx]}' 색상의 사이즈 정보 추출 실패 (wait_for_attribute_change)")
                             # Mark this color's sizes as failed, but continue if possible
                             color_size_info[color_names[idx]] = crawler.error_message


                        # Click first select area again to close size dropdown and maybe open color dropdown? Or just close?
                        # Check if this is necessary and doesn't cause issues if the next color is already selected
                        if idx != len(color_names) - 1:
                             crawler.wait_for_clickable_element(first_select_area)
                             time.sleep(0.2) # Delay after closing/opening dropdowns
                    crawling_status["color_size"] = "success" # Mark overall success if loop completes
                else:
                    print(f"크롤링 실패 [Section 5]: 색상 선택 영역 로드 실패 (wait_for_attribute_change)")
                    color_size_info = crawler.error_message
                    
            # 누르는 버튼이 1개 인경우 (사이즈 정보만 있음.)
            elif is_one_color and child_divs: # Handle one color product (or structure with 1 child)
                 first_select_area = child_divs[0]
                 crawler.wait_for_clickable_element(first_select_area)

                 # Check the structure here, the original code assumes the dropdown is the second child of the parent `select_area`
                 # Let's adjust the selector for wait_for_attribute_change_in_parent
                 # Assuming the dropdown is inside the `first_select_area` when clicked
                 sizes_element = crawler.wait_for_attribute_change_in_parent(first_select_area, value=".static-dropdown-menu > div:nth-child(2)" , attribute="data-state" , target_value="open")

                 if sizes_element != crawler.error_message:
                     color_size_info = {"one_color": {}} # Reset/Initialize
                     size_soup = BeautifulSoup(sizes_element.get_attribute("innerHTML") , "html.parser")
                     for size_button in size_soup.select(".sc-102tdfw-1"):
                         text = size_button.select_one("span").text.strip()
                         text_split = text.split()
                         if text_split:
                             is_available = True if "품절" not in text_split[-1] else False
                             size_key = "".join(text_split) if is_available else "".join(text_split[:-1])
                             color_size_info["one_color"][size_key] = "available" if is_available else "soldout"
                     crawling_status["color_size"] = "success"
                 else:
                     print(f"크롤링 실패 [Section 5]: 단일 색상 제품 사이즈 정보 추출 실패 (wait_for_attribute_change)")
                     color_size_info = crawler.error_message
            else: # No child divs found or unexpected structure
                 print(f"크롤링 실패 [Section 5]: 색상/사이즈 선택 영역 구조를 찾을 수 없음.")
                 color_size_info = crawler.error_message

        else:
            print("색상/사이즈 선택 영역 예외 처리 진행")
            area = crawler.wait_for_element_by_css_selector(".sc-1puoja0-0.fZdNIF")
            if area.find_element(By.CSS_SELECTOR , ".sc-16dm5t2-0.ixCeVZ button span").text == "품절":
                color_size_info = "품절"    
                crawling_status["color_size"] = "success"
            elif len(area.find_elements(By.CSS_SELECTOR , ".gtm-impression-content")) >= 1:
                color_size_info = "one_size"        
                crawling_status["color_size"] = "success"
            else:
                print(f"크롤링 실패 [Section 5]: 색상/사이즈 선택 영역 로드 실패 (wait_for_element)")
                color_size_info = crawler.error_message

    except Exception as e:
        print(f"크롤링 실패 [Section 5]: 제품 색상/사이즈 정보 추출 중 오류 발생 - {e}")
        color_size_info = crawler.error_message
        
    # 6. 제품 실제 사이즈 정보 추출

    
    
    
    # Process images only if crawling was successful
    # if is_process:
    #     if crawling_status["summary_images"] == "success" and isinstance(product_summary_images, list):
    #         processor(product_summary_images ,is_crop=False, is_save=True , save_single_dir=True,save_dir=f"./{product_id}" )
    #     if crawling_status["detail_images"] == "success" and isinstance(product_detail_images, list):
    #         processor(product_detail_images ,is_crop=True, is_save=True , save_single_dir=True, save_dir=f"./{product_id}" )
    success_status = "success" if all([status == "success" for status in crawling_status.values()]) else "failed"
    result = {
        "product_id": product_id,
        "summary_images": summary_images,
        "detail_images": detail_images,
        "detail_text": detail_text,
        "review_texts": review_texts,
        "color_size_info": color_size_info,
        "crawling_status": crawling_status, # Include the status dictionary
        "success_status" : success_status
    }
    return result