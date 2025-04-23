from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from typing import List , Dict 
from bs4 import BeautifulSoup
import time
from datetime import datetime 
import pandas as pd
class Crawler:
    def __init__(self, headless=False , base_url="https://x.com/"):
        """
        X 크롤러 초기화
        
        Args:
            headless (bool): 헤드리스 모드 사용 여부
        """
        self.base_url = base_url
        self.driver = None
        self.headless = headless
        self.setup_driver()
        
        # 결과 저장 디렉토리 생성
        # self.results_dir = os.path.join(os.getcwd(), "instagram_data")
        # if not os.path.exists(self.results_dir):
        #     os.makedirs(self.results_dir)
        #     print(f"'{self.results_dir}' 디렉토리를 생성했습니다.")
    
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
        self.wait = WebDriverWait(self.driver, 10)
        
        # 쿠키 디렉토리 생성
        # self.cookies_dir = os.path.join(self.results_dir, "cookies")
        # if not os.path.exists(self.cookies_dir):
        #     os.makedirs(self.cookies_dir)
    
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
    def scroll_to_load_more(self, scroll_count=5, scroll_pause=2.0):
        """
        페이지를 스크롤하여 더 많은 콘텐츠 로드
        
        Args:
            scroll_count (int): 스크롤할 횟수
            scroll_pause (float): 스크롤 사이 대기 시간(초)
            
        Returns:
            int: 로드된 포스트 수
        """
        if not self.driver:
            print("드라이버가 초기화되지 않았습니다.")
            return 0
        
        print(f"스크롤을 시작합니다. 스크롤 횟수: {scroll_count}")
        
        # 초기 포스트 링크 수
        # initial_posts = set(self.driver.find_elements(By.CSS_SELECTOR, "article div a"))
        # print(f"초기 포스트 수: {len(initial_posts)}")
        
        
       
        # 페이지 끝으로 스크롤
        self.driver.execute_script("""
                                    window.scrollTo(0, document.body.scrollHeight);
                                    """
                                    )

        # print(f"스크롤 {i+1}/{scroll_count} 완료")
            
        # 새 콘텐츠 로드 대기
        time.sleep(scroll_pause)
        
        # 최종 포스트 링크 수
        # final_posts = set(self.driver.find_elements(By.CSS_SELECTOR, "article div a"))
        # print(f"최종 포스트 수: {len(final_posts)}")
        
        # return len(final_posts)
    def wait_for_element_by_css_selector(self, css_selector:str):
        try:
            element = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
            )
            print("요소 로드 완료")
            return element
        except Exception as e:
            print(f"요소 로드 대기 중 오류 발생: {e}")
            return None
    # def login(self, username=None, password=None):
    #     """
    #     X에 로그인
        
    #     Args:
    #         username (str): X 사용자명 (이메일 또는 전화번호)
    #         password (str): X 비밀번호
        
    #     Returns:
    #         bool: 로그인 성공 여부
    #     """
    #     if not self.driver:
    #         self.setup_driver()
        
    #     self.driver.get(self.base_url)
    #     login_button_selector = "div.css-175oi2r.r-1f2l425.r-13qz1uu.r-417010 > main > div > div > div.css-175oi2r.r-tv6buo > div > div > div.css-175oi2r > div.css-175oi2r.r-2o02ov > a > div"
    #     self.click_element_by_css_selector(login_button_selector)
    #     login_button_selector = "#layers > div:nth-child(2) > div > div > div > div > div > div.css-175oi2r.r-1ny4l3l.r-18u37iz.r-1pi2tsx.r-1777fci.r-1xcajam.r-ipm5af.r-g6jmlv.r-1awozwy > div.css-175oi2r.r-1wbh5a2.r-htvplk.r-1udh08x.r-1867qdf.r-kwpbio.r-rsyp9y.r-1pjcn9w.r-1279nm1 > div > div > div.css-175oi2r.r-1ny4l3l.r-6koalj.r-16y2uox.r-kemksi.r-1wbh5a2 > div.css-175oi2r.r-16y2uox.r-1wbh5a2.r-f8sm7e.r-13qz1uu.r-1ye8kvj > div > div > div > div.css-175oi2r.r-1mmae3n.r-1e084wi.r-13qz1uu > label > div > div.css-175oi2r.r-18u37iz.r-16y2uox.r-1wbh5a2.r-1wzrnnt.r-1udh08x.r-xd6kpl.r-is05cd.r-ttdzmv > div > input"
    #     self.click_and_type(login_button_selector, self.id)
    #     time.sleep(1)
    #     login_button_selector = "#layers > div:nth-child(2) > div > div > div > div > div > div.css-175oi2r.r-1ny4l3l.r-18u37iz.r-1pi2tsx.r-1777fci.r-1xcajam.r-ipm5af.r-g6jmlv.r-1awozwy > div.css-175oi2r.r-1wbh5a2.r-htvplk.r-1udh08x.r-1867qdf.r-kwpbio.r-rsyp9y.r-1pjcn9w.r-1279nm1 > div > div > div.css-175oi2r.r-1ny4l3l.r-6koalj.r-16y2uox.r-kemksi.r-1wbh5a2 > div.css-175oi2r.r-16y2uox.r-1wbh5a2.r-f8sm7e.r-13qz1uu.r-1ye8kvj > div.css-175oi2r.r-16y2uox.r-1wbh5a2.r-1dqxon3 > div > div > div.css-175oi2r.r-1e084wi.r-13qz1uu > div > label > div > div.css-175oi2r.r-18u37iz.r-16y2uox.r-1wbh5a2.r-1wzrnnt.r-1udh08x.r-xd6kpl.r-is05cd.r-ttdzmv > div.css-146c3p1.r-bcqeeo.r-1ttztb7.r-qvutc0.r-37j5jr.r-135wba7.r-16dba41.r-1awozwy.r-6koalj.r-1inkyih.r-13qz1uu > input"
    #     self.click_and_type(login_button_selector, self.pw)
    #     print("로그인 성공")
    
    
def get_one_product_info(item :BeautifulSoup , columns:List[str], **params)->Dict :
    image_section = item.select_one(".sc-fsjlER.jYcDQz a")
    product_id = image_section.get("data-item-id")
    product_href = image_section.get("href")
    product_original_price = image_section.get("data-original-price")
    product_discount_price = image_section.get("data-discount")
    product_discount_rate = image_section.get("data-discount-rate")
    product_brand_name = image_section.get("data-brand-id")
    
    detail_section = item.select_one(".sc-dZEakj.iDBPjO")
    product_name = detail_section.select_one(".sc-cNFqVt.dhrvja a:nth-child(2)").text
    
    # 요소가 없을 경우 None을 반환하는 함수 
    def get_text_or_default(selector, default=None):
        element = detail_section.select_one(selector)
        return element.text if element else default
    
    # 각 요소 안전하게 가져오기
    num_likes = get_text_or_default(".sc-fpEFIB.fHfJGx div:nth-child(1) span", None)
    avg_rating = get_text_or_default(".sc-fpEFIB.fHfJGx div:nth-child(2) span:nth-child(1)", None)
    review_count = get_text_or_default(".sc-fpEFIB.fHfJGx div:nth-child(2) span:nth-child(2)", None)
    
    # 데이터 반환
    # columns = ["category_main" , "category_sub" , "gender" , "product_id" ,"product_name", "product_href" , "product_original_price" , "product_discount_price" , "product_discount_rate", "product_brand_name" , "num_likes" , "avg_rating" , "review_count"]
    
    return {column:value for column , value in zip(columns , [*params.values() , product_id , product_name , product_href , product_original_price , product_discount_price , product_discount_rate , product_brand_name , num_likes , avg_rating , review_count])}

def get_row_product_info(page_index:int , soup:BeautifulSoup , columns:List[str] , **params) -> List[Dict]:
        # target_element = soup.select_one(f'div[data-index="{page_index}"]')
        # assert target_element is not None , f"{page_index} 페이지 로드 실패"
        product_list = []
        for item in soup.select("div.sc-dNpohg.jKFuqW"):
            product_data = get_one_product_info(item , columns , **params)
            product_list.append(product_data)
            
        return product_list
            


def crawl_product_list(crawler:Crawler , num_scrolls:int , dy:int=470,**params)->List[Dict]:
    start , end = 0 , dy
    page_index = 0
    columns = ["category_main" , "category_sub" , "gender" , "product_id" ,"product_name", "product_href" , "product_original_price" , "product_discount_price" , "product_discount_rate", "product_brand_name" , "num_likes" , "avg_rating" , "review_count"]
    crawled_data = []
    for _ in range(num_scrolls):
        time.sleep(0.2)
        target_element = crawler.wait_for_element_by_css_selector(f".sc-k7xv49-0.hRlVQI div[data-index='{page_index}']")
        soup = BeautifulSoup(target_element.get_attribute("innerHTML"), "html.parser")
        product_list = get_row_product_info(page_index , soup, columns , **params)
        crawled_data.extend(product_list)
        crawler.driver.execute_script(f"window.scrollTo({start}, {end});")
        start , end = end , end + dy
        page_index += 1
        
    return crawled_data


def add_data_to_dataframe(data:List[Dict], df:pd.DataFrame):
    result_df = pd.concat([df , pd.DataFrame(data)])
    return result_df

def save_dataframe_to_csv(df:pd.DataFrame , csv_path:str):
    df.to_csv(csv_path , index=False)

def load_dataframe_from_csv(csv_path:str)->pd.DataFrame:
    return pd.read_csv(csv_path,encoding="utf-8")



from urllib.parse import urlencode
import pandas as pd
base_url = "https://www.musinsa.com/"
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

columns = ["category_main" , "category_sub" , "gender" , "product_id" ,"product_name", "product_href" , "product_original_price" , "product_discount_price" , "product_discount_rate", "product_brand_name" , "num_likes" , "avg_rating" , "review_count"]
df = pd.DataFrame(columns=columns)

url = f"{base_url}category/{CATEGORY_SUB['맨투맨/스웨트']}?{urlencode(params)}"
crawler = Crawler(headless=False)
crawler.go(url)
_ = crawler.wait_for_element_by_css_selector(".sc-k7xv49-0.hRlVQI")

crawled_data = crawl_product_list(crawler , num_scrolls = 5 , **{"category_main":CATEGORY_MAIN["상의"],"category_sub":"맨투맨/스웨트","gender":GENDER["남성"]})
result_df = add_data_to_dataframe(crawled_data , df)
save_dataframe_to_csv(result_df , "musinsa_.csv")
