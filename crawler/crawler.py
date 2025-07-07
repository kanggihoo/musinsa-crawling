from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import List , Dict , Tuple, Generator
from bs4 import BeautifulSoup
import time
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoAlertPresentException
import logging

COLUMNS = ["category_main" , "category_sub" , "gender" , "product_id" ,"product_name", "product_href" ,"product_price" , "product_original_price" , "product_discount_price" , "product_discount_rate", "product_brand_name" , "num_likes" , "avg_rating" , "review_count"]
class Crawler:
    def __init__(self, headless=False , base_url:str|None=None , time_out:int=3 , error_message:str = "failed"):
        self.base_url = base_url
        self.driver = None
        self.headless = headless
        self.error_message = error_message
        self.setup_driver(time_out)
        self.recommend_commercial_flag = True
    
    def setup_driver(self, time_out:int):
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
        self.wait = WebDriverWait(self.driver, time_out , poll_frequency=time_out/10)
    
    
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
        
    def is_exist_element(self,  css_selector:str , by = By.CSS_SELECTOR):
        try:
            elements = self.driver.find_elements(by, css_selector)
            return len(elements) > 0
        except:
            return False
        
    def click_popup_window(self):
        try:
            popup_window = self.driver.find_elements(By.CSS_SELECTOR , ".gtm-impression-popup")
            if len(popup_window):
                popup_window[0].find_element(By.CSS_SELECTOR , "button").click()
                print("팝업 창 닫기 성공")
        except Exception as e:
            print("팝업 창 체크 간 에러 발생")
    
    def click_recommend_commercial(self):
        try:
            recommend_commercial = self.wait_for_element_by_css_selector(".sc-7ea6a61a-0")
            if len(recommend_commercial):
                recommend_commercial[0].find_element(By.CSS_SELECTOR , "button.gtm-click-button").click()
                print("추천 상품 닫기 성공")
                self.recommend_commercial_flag = False
        except Exception as e:
            print("추천 상품 닫기간 에러 발생")
    
    def handle_alert(self):
        """
        페이지에 나타나는 경고창(alert)을 처리합니다.
        경고창이 있으면 텍스트를 반환하고 '확인'을 누르고, 없으면 None을 반환합니다.
        """
        try:
            alert = self.driver.switch_to.alert
            alert_text = alert.text
            print(f"경고창 감지: '{alert_text}'")
            alert.accept()  # 경고창의 '확인' 버튼을 누름
            return alert_text
        except NoAlertPresentException:
            # 처리할 경고창이 없는 경우
            return None

    def close(self):
        """웹드라이버를 안전하게 종료합니다."""
        try:
            if self.driver:
                self.driver.quit()
                print("웹드라이버가 안전하게 종료되었습니다.")
        except Exception as e:
            print(f"웹드라이버 종료 중 오류 발생: {e}")
    # def click_and_type(self, css_selector, text , enter=True):
    #     """
    #     특정 위치에 클릭한 후 텍스트를 입력하고 엔터 키를 누릅니다.
        
    #     Args:
    #         css_selector (str): 클릭할 요소의 CSS 셀렉터
    #         text (str): 입력할 텍스트
    #     """
    #     try:
    #         # 요소가 로드될 때까지 대기
    #         element = self.wait.until(
    #             EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))
    #         )
    #         # 요소 클릭
    #         element.click()
            
    #         # 텍스트 입력
    #         element.send_keys(text)
            
    #         if enter:
    #             # 엔터 키 입력
    #             element.send_keys(Keys.ENTER)
            
    #     except Exception as e:
    #         print(f"클릭 및 입력 중 오류 발생: {e}")
    #         return self.error_message

    
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
        image_section = item.select_one(".sc-bgpKpp a")   
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
        detail_section = item.select_one(".sc-oDVYc")
        product_name_element = detail_section.select_one("a:nth-child(2)")
        product_name = product_name_element.text if product_name_element else None
    
        # 요소가 없을 경우 None을 반환하는 함수 
        def get_text_or_default(selector, default=None):
            element = detail_section.select_one(selector)
            return element.text if element else default
        
        #REVIEW 추출을 하는데 None을 집어넣으면 진짜 없는건지 , 크롤링 실패한건지 구분이 안될거 같은데 
        # 각 요소 안전하게 가져오기
        num_likes = get_text_or_default(".sc-iayzNI:nth-of-type(1) span", None)
        avg_rating = get_text_or_default(".sc-iayzNI:nth-of-type(2) span:nth-child(1)", None)
        review_count = get_text_or_default(".sc-iayzNI:nth-of-type(2) span:nth-child(2)", None)
        review_count = review_count[1:-1] if review_count and len(review_count) > 2 else None
    
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
        for item in soup.select(".sc-igtioI"):
            product_data = get_one_product_info(item , **params)
            product_list.append(product_data)
             
        
        return product_list
    
def crawl_product_list(crawler:Crawler, num_scrolls:int=None, infinite_scroll:bool=False, **params) -> Generator[Dict, None, None]:
    scroll_count = 0
    
    while True:
        # 1. Wait for the current row to be present
        try:
            target_element = crawler.wait_for_element_by_css_selector(f".sc-k7xv49-0 div[data-index='{scroll_count}']")
        except:
            print(f"더 이상 크롤링할 상품이 없습니다. 총 {scroll_count}번의 스크롤 진행.")
            break

        # Check if we should stop based on user-defined scroll limit
        if not infinite_scroll and num_scrolls is not None and scroll_count >= num_scrolls:
            print(f"지정된 스크롤 횟수({num_scrolls})에 도달했습니다.")
            break
            
        # 2. Process the element
        soup = BeautifulSoup(target_element.get_attribute("innerHTML"), "html.parser")
        product_list = get_row_product_info(soup, **params)
        yield product_list
        
        # 3. Find the next element and scroll to it to trigger loading the next one
        try:
            # We look for scroll_count + 1 to scroll to it.
            next_element_to_scroll = crawler.wait_for_element_by_css_selector(f".sc-k7xv49-0 div[data-index='{scroll_count + 1}']")
            
            # Use scrollIntoView to bring the next element into the viewport.
            crawler.driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", next_element_to_scroll)
            
            # Give a brief moment for any JS to fire after scrolling
            time.sleep(0.5) 

        except Exception:
            # This can happen if we've truly reached the end of the list.
            print(f"다음 상품 목록(data-index: {scroll_count + 1})을 찾을 수 없어 스크롤을 중단합니다.")
            
            # Before breaking, let's try one last scroll to the bottom of the page
            last_height = crawler.driver.execute_script("return document.body.scrollHeight")
            crawler.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1) # Wait for content to load
            new_height = crawler.driver.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height:
                print("페이지의 끝에 도달했습니다.")
                break # Exit the loop
            else:
                print("추가 스크롤 후 새로운 콘텐츠를 감지했습니다. 계속 진행합니다.")


        # 4. Increment scroll count for the next iteration
        scroll_count += 1
        if scroll_count % 10 == 0:
            print(f"현재 scroll_count : {scroll_count}")
            
        
    

# 1. 제품 preview 이미지 url 추출
def get_product_preview_image_url(crawler:Crawler , product_id:str , logger:logging.Logger) -> Tuple[str , List[str]]:
    status = "failed"
    summary_images = []
    try:
        # product_summary = crawler.wait_for_element_by_xpath("//*[@id='root']/div[1]/div[1]/div[1]/div[1]/div[1]/div")
        product_summary = crawler.wait_for_element_by_css_selector("#root .sc-366fl4-1")
        
        if product_summary != crawler.error_message:
            product_summary_soup = BeautifulSoup(product_summary.get_attribute("innerHTML") , "html.parser")
            for image in product_summary_soup.select("img"):
                summary_images.append(image.get("src"))
            status = "success"
        else:
            logger.error(f"[Section 1] 제품 preview 이미지 url 요소 p탐색 실패 (wait_for_element) : {product_id} ")
            # if crawler.recommend_commercial_flag:
            #     crawler.click_recommend_commercial()
            #     crawler.go(f"{crawler.base_url}/{product_id}")
                
    except Exception as e:
        logger.error(f"[Section 1] 제품 preview 이미지 url 추출 중 오류 발생 : {product_id} ")
        

    return status , summary_images

# 2. 제품 detail 영역에서 text 정보 추출(성별 , 시즌 , 조회수 등)
def get_product_detail_text(crawler:Crawler , product_id:str , logger:logging.Logger) -> Tuple[str , Dict[str , str]]:
    status = "failed"
    detail_text = {}
    try:
        # product_details_element = crawler.wait_for_element_by_xpath("//*[@id='root']/div[1]/div[1]/div[3]/div[1]/div[1]/div")
        product_details_element = crawler.wait_for_element_by_css_selector("#root .sc-g3hx4t-4 .sc-2ll6b5-0")
        if product_details_element != crawler.error_message:
            product_details_soup = BeautifulSoup(product_details_element.get_attribute("innerHTML") , "html.parser")
            for e in product_details_soup.select(".sc-2ll6b5-1")[1:]:
                key = e.dt.text
                value = e.dd
                detail_text[key]= value.text.strip() if not value.find("ol") else ", ".join([li.text.strip() for li in value.find_all("li")])
            status = "success"
        else:
            logger.error(f"[Section 2] 제품 detail 영역 요소 탐색 실패 (wait_for_element) : {product_id} ")
    except Exception as e:
        logger.error(f"[Section 2] 제품 detail 영역에서 text 정보 추출 중 오류 발생 : {product_id} ")
        
        
    return status , detail_text

# 3. 제품과 관련된 자세한 image url 추출
def get_product_detail_images_url(crawler:Crawler , product_id:str , logger:logging.Logger) -> Tuple[str , List[str]]:
    status = "failed"
    detail_images = []
    try:
        # Reuse product_details_soup if available and Section 2 succeeded
        # product_details_element = crawler.wait_for_element_by_xpath("//*[@id='root']/div[1]/div[1]/div[3]/div[1]/div[1]/div")
        
        # 제품의 상세 이미지가 없는 경우 확인 
        if not crawler.is_exist_element(".sc-g3hx4t-4 .sc-1ikk4lv-4"):
            status = "not_exist"
            return status , detail_images
        
        product_details_element = crawler.wait_for_element_by_css_selector(".sc-g3hx4t-4 .sc-1ikk4lv-4")
        if product_details_element != crawler.error_message:
            product_details_soup = BeautifulSoup(product_details_element.get_attribute("innerHTML") , "html.parser")
            for image in product_details_soup.select("img"):
                    image_url = image.get("src")
                    detail_images.append(image_url)
            status = "success"
            # print(len(detail_images))
        else:
            logger.error(f"크롤링 실패 [Section 3] 제품 상세 이미지 요소 탐색 실패 (wait_for_element) : {product_id} ")
    except Exception as e:
        logger.error(f"크롤링 실패 [Section 3] 제품과 관련된 자세한 image url 추출 중 오류 발생 : {product_id} ")
    return status , detail_images

#REVIEW : 제품에 대한 리뷰추출시 최대한 다 끌어오고 사용자에게 맞는걸 선택해서 주는 방안 고려 해보기 
# 4. 제품 리뷰 내용 추출
def get_product_reviews_text(crawler:Crawler , product_id:str,logger:logging.Logger, num_reviews:int=10) -> Tuple[str , List[str]]:
    status = "failed"
    review_texts = []
    try:
        product_reviews = crawler.wait_for_element_by_css_selector("#root > div.sc-3weaze-0 .goods-reviewpage__Container-sc-1iio9o6-0")
        if product_reviews != crawler.error_message:
            product_reviews_soup = BeautifulSoup(product_reviews.get_attribute("innerHTML") , "html.parser")
            is_review_exist = len(product_reviews_soup.find_all("div", recursive=False)) >= 3

            if is_review_exist:
                review_items = product_reviews_soup.select(".GoodsReviewListSection__Container-sc-1x35scp-0 .review-list-item__Container-sc-13zantg-0")
                max_reviews_to_crawl = min(num_reviews, len(review_items))

                for idx, review in enumerate(review_items):
                    if idx >= max_reviews_to_crawl:
                        break
                    review_text_area = review.select_one(".ReviewImageContentSection__Container-sc-1lff2fc-0 > .ExpandableContent__Container-sc-gj5b23-0 .Truncate__MeasureContainer-sc-5dnpga-0")
                    if review_text_area:
                        first_span = review_text_area.select_one("span:first-child")
                        
                        # 리뷰 내용 중 한달 사용 후기 인 경우 존재 
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
                            review_texts.append(" ".join(review_text))
                        
                        elif first_span: # Regular review text
                            review_texts.append(first_span.text.strip())
                        # else: Skip if structure doesn't match
                    # else: Skip review if text area not found
                status = "success"
            else:
                status = "not_exist" 
        else:
            logger.error(f"크롤링 실패 [Section 4] 제품 리뷰 영역 요소 탐색 실패 (wait_for_element) : {product_id} ")
    except Exception as e:
        logger.error(f"크롤링 실패 [Section 4] 제품 리뷰 내용 추출 중 오류 발생 : {product_id} ")
        

    return status , review_texts

# 5. 상품 사이즈 디테일 정보 
def get_product_size_detail_info(crawler:Crawler , product_id:str , logger:logging.Logger) -> Tuple[str , List[dict]]:
    status = "failed"
    size_detail_info = []
    try:    
        # size_section = crawler.wait_for_element_by_xpath("//*[@id='root']/div[1]/div[1]/div[4]")
        size_section = crawler.wait_for_element_by_css_selector("#root > .sc-3weaze-0 > .sc-4n9q35-0 > .sc-g3hx4t-4[data-index='1']")
        #root > div.sc-3weaze-0.cBNetp > div.sc-4n9q35-0.cAlKzU > div:nth-child(5)
        # size_section = crawler.wait_for_element_by_css_selector("#root .sc-g3hx4t-4 .sc-1ikk4lv-4")
        if size_section != crawler.error_message:
            size_soup = BeautifulSoup(size_section.get_attribute("innerHTML") , "html.parser")
            if len(size_soup.select("div.sc-1jg999i-0")):
                size_element = size_soup.select_one(".sc-1jg999i-0 > .sc-1jg999i-1")
                first_column = [ li.text.strip() for li in size_element.select("ul > li")[2:] ]
                    
                size_table = size_element.select_one("table")
                title = [ th.text.strip() for th in size_table.select("thead >tr> th ")]

                for idx , tr in enumerate(size_table.select("tbody > tr ")[1:]):
                    row = {}
                    row[first_column[idx]] = {}
                    for col_idx , td in enumerate(tr.select("td")):
                        row[first_column[idx]][title[col_idx]] = td.text.strip()
                    size_detail_info.append(row)
                status = "success"
            else:
                status = "not_exist"
        else:
            logger.error(f"크롤링 실패 [Section 5] 세부 사이즈 정보 영역 요소 탐색 실패 (wait_for_element): {product_id} ")
    except Exception as e:  
        logger.error(f"크롤링 실패 [Section 5] 세부 사이즈 정보 추출 중 오류 발생 : {product_id} ")
     
    return status , size_detail_info

# 6. 핏/계절성 정보 
def get_product_fit_info(crawler:Crawler , product_id:str , logger:logging.Logger) -> Tuple[str , Dict[str , List[str]]]:
    status = "failed"
    fit_info = {}
    try:
        # size_section = crawler.wait_for_element_by_xpath("//*[@id='root']/div[1]/div[1]/div[4]")
        size_section = crawler.wait_for_element_by_css_selector("#root > .sc-3weaze-0 > .sc-4n9q35-0 > .sc-g3hx4t-4[data-index='1']")
        if size_section != crawler.error_message:
            size_soup = BeautifulSoup(size_section.get_attribute("innerHTML") , "html.parser")
            if len(size_soup.select(".sc-36xiah-0.gtm-impression-content .sc-36xiah-2")):
                fit_element = size_soup.select_one(".sc-36xiah-0.gtm-impression-content .sc-36xiah-2")
                first_column = [ li.text.strip() for li in fit_element.select("ul > li") ]
                fit_table = fit_element.select_one("table > tbody")

                for idx , tr in enumerate(fit_table.select("tr")):
                    fit_info[first_column[idx]] = []
                    for col_idx , td in enumerate(tr.select("td")):
                        #REVIEW : 해당 제품의 핏/계절성 정보 클래스인 eviTcu가 변하지 않는지 확인 필요
                        if "eviTcu" in td["class"]:
                            fit_info[first_column[idx]].append(td.text.strip())
                status = "success"
            else:
                status = "not_exist"
        else:
            logger.error(f"크롤링 실패 [Section 6] 제품 핏/계절성 정보 영역 요소 탐색 실패 (wait_for_element) : {product_id} ")
    except Exception as e:
        logger.error(f"크롤링 실패 [Section 6] 제품 핏/계절성 정보 추출 중 오류 발생 : {product_id} ")

    return status , fit_info

#7. 제품 색상 및 색상별 사이즈 정보 추출
#TODO : 제품 선택 버튼이 없는 건지(Free 사이즈), 재고가 없어서 선택 버튼이 없는 건지 확인 필요 
def get_product_color_size_info(crawler:Crawler , product_id:str , logger:logging.Logger) -> Tuple[str , dict[str , list[str]]]:
    #REVIEW : 팝업 창이 잘 닫히는지 확인 필요 
    crawler.click_popup_window()
    status = "failed"
    color_size_info = {}
    color_info = []
    size_info = []
    try:
        select_area = crawler.wait_for_element_by_css_selector(".sc-1puoja0-0 .gtm-impression-content .pt-1.pb-2")
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
                    # 색상 정보 추출
                    for color in color_soup.select(".sc-102tdfw-1"):
                        color_name_span = color.select_one("span")
                        if color_name_span:
                            color_name = color_name_span.text.strip()
                            color_info.append(color_name)
                            
                    
                    crawler.wait_for_clickable_element(select_area.find_elements(By.CSS_SELECTOR , ".sc-102tdfw-1:nth-child(1)")[0])
                    crawler.wait_for_clickable_element(second_select_area)
                    
                    # 사이즈 정보 추출
                    sizes = crawler.wait_for_attribute_change_in_parent(second_select_area , value=".static-dropdown-menu > div:nth-child(2)" , attribute="data-state" , target_value="open")
                    if sizes != crawler.error_message:
                        size_soup = BeautifulSoup(sizes.get_attribute("innerHTML") , "html.parser")
                        for size in size_soup.select(".sc-102tdfw-1"):
                            text = size.select_one("span").text.strip()
                            text_split = text.split()
                            if text_split: # Ensure there's text
                                if len(text_split) >=2:
                                    size_info.append(" ".join(text_split[:-1]))
                                else:
                                    size_info.append(" ".join(text_split))
                        status = "success"
                        color_size_info["color"] = color_info
                        color_size_info["size"] = size_info
                    else:
                        print(f"크롤링 실패 [Section 7]: 색상은 정보 추출, 사이즈 정보 요소 탐색 실패 (wait_for_element) : {product_id} ")
                        # Mark this color's sizes as failed, but continue if possible
                else:
                    print(f"크롤링 실패 [Section 7]: 색상 선택 영역 요소 탐색 실패 (wait_for_attribute_change) : {product_id} ")
                    
            # 누르는 버튼이 1개 인경우 (사이즈 정보만 있음.)
            elif is_one_color and child_divs: # Handle one color product (or structure with 1 child)
                first_select_area = child_divs[0]
                crawler.wait_for_clickable_element(first_select_area)
                sizes_element = crawler.wait_for_attribute_change_in_parent(first_select_area, value=".static-dropdown-menu > div:nth-child(2)" , attribute="data-state" , target_value="open")

                if sizes_element != crawler.error_message:
                    size_info = []
                    # # 사이즈 별 품절 여부 확인 코드 
                    size_soup = BeautifulSoup(sizes_element.get_attribute("innerHTML") , "html.parser")
                    for size_button in size_soup.select(".sc-102tdfw-1"):
                        text = size_button.select_one("span").text.strip()
                        text_split = text.split()
                        if text_split: # Ensure there's text
                            if len(text_split) >=2:
                                size_info.append(" ".join(text_split[:-1]))
                            else:
                                size_info.append(" ".join(text_split))

                    color_size_info["color"] = "one_color"
                    color_size_info["size"] = size_info
                    status = "success"
                else:
                    logger.error(f"크롤링 실패 [Section 7] 단일 색상 제품 사이즈 영역 탐색 실패 (wait_for_attribute_change) : {product_id} ")
            else: # No child divs found or unexpected structure
                logger.error(f"크롤링 실패 [Section 7] 색상/사이즈 선택 영역의 예외 케이스로 다시 확인 필요 : {product_id} ")
        else:
            if crawler.wait_for_element_by_css_selector(".sc-1puoja0-0 .gtm-impression-content"):
                status = "not_exist"
            else:
                logger.error(f"크롤링 실패 [Section 7] 색상/사이즈 선택 영역 로드 실패 (wait_for_element) : {product_id} ")
    except Exception as e:
        logger.error(f"크롤링 실패 [Section 7] 제품 색상/사이즈 정보 추출 중 오류 발생 : {product_id} ")
    
    return status , color_size_info

#REVIEW : 각 크롤링 함수에서 클래스명이 바뀌어 오류 날 수 있느니 주의!
def get_product_detail_info(crawler:Crawler , product_id:str, logger:logging.Logger , is_process:bool = False ):
    test_url = f"{crawler.base_url}/{product_id}"
    crawler.go(test_url)
    
    # 유효하지 않은 상품 처리
    if crawler.handle_alert() != None:
        logger.error(f"크롤링 실패 유효하지 않은 상품 id : {product_id} ")
        return {
            "success_status" : "error_product_id"
        }
        
    
    # 각 기능별 크롤링 함수 정의 
    crawling_functions = {
        "summary_images": lambda : get_product_preview_image_url(crawler , product_id, logger),
        "detail_text": lambda : get_product_detail_text(crawler , product_id, logger),
        "detail_images": lambda : get_product_detail_images_url(crawler , product_id, logger),
        "review_texts": lambda : get_product_reviews_text(crawler , product_id , logger , num_reviews=10),
        "size_detail_info": lambda : get_product_size_detail_info(crawler , product_id, logger),
        "fit_info": lambda : get_product_fit_info(crawler , product_id, logger),
        "color_size_info": lambda : get_product_color_size_info(crawler , product_id, logger),
    }
    
    result = {k: f() for k , f in crawling_functions.items()}
    crawling_status = {}
    data = {}
    for k , (status , value) in result.items():
        crawling_status[k] = status
        data[k] = value

    success_status = "success" if all([status in ("success", "not_exist") for status in crawling_status.values()]) else "failed"
    result = {
        "product_id": product_id,
        **data,
        "crawling_status": crawling_status,
        "success_status": success_status
    }

    return result