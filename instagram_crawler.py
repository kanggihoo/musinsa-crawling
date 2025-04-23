from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import json
import re
import csv
from datetime import datetime
import getpass  # 비밀번호를 안전하게 입력받기 위한 모듈

class InstagramCrawler:
    def __init__(self, headless=False):
        """
        인스타그램 크롤러 초기화
        
        Args:
            headless (bool): 헤드리스 모드 사용 여부
        """
        self.base_url = "https://www.instagram.com"
        self.driver = None
        self.headless = headless
        
        # 결과 저장 디렉토리 생성
        self.results_dir = os.path.join(os.getcwd(), "instagram_data")
        if not os.path.exists(self.results_dir):
            os.makedirs(self.results_dir)
            print(f"'{self.results_dir}' 디렉토리를 생성했습니다.")
    
    def setup_driver(self):
        """웹드라이버 설정"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-notifications")
        
        # # 자동화 감지 방지
        # chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        # chrome_options.add_experimental_option("useAutomationExtension", False)
        # chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        # User-Agent 설정
        # chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36")
        
        # service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        
        # 쿠키 디렉토리 생성
        self.cookies_dir = os.path.join(self.results_dir, "cookies")
        if not os.path.exists(self.cookies_dir):
            os.makedirs(self.cookies_dir)
    
    def login(self, username=None, password=None):
        """
        인스타그램에 로그인
        
        Args:
            username (str): 인스타그램 사용자명 (이메일 또는 전화번호)
            password (str): 인스타그램 비밀번호
        
        Returns:
            bool: 로그인 성공 여부
        """
        if not self.driver:
            self.setup_driver()
        
        # # 쿠키 파일 경로
        # cookies_file = os.path.join(self.cookies_dir, f"{username}_cookies.json")
        
        # # 쿠키가 있으면 로드하여 로그인 시도
        # if os.path.exists(cookies_file):
        #     self.driver.get(self.base_url)
            
        #     # 쿠키 로드
        #     with open(cookies_file, 'r') as f:
        #         cookies = json.load(f)
            
        #     for cookie in cookies:
        #         # Selenium에서는 쿠키의 expiry 값이 float이어야 함
        #         if 'expiry' in cookie:
        #             cookie['expiry'] = int(cookie['expiry'])
        #         self.driver.add_cookie(cookie)
            
        #     # 페이지 새로고침으로 로그인 상태 확인
        #     self.driver.refresh()
            
        #     # 로그인 상태 확인
        #     try:
        #         WebDriverWait(self.driver, 5).until(
        #             EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Search')]"))
        #         )
        #         print("쿠키를 사용하여 로그인되었습니다.")
        #         return True
        #     except:
        #         print("쿠키가 만료되었습니다. 다시 로그인합니다.")
        
        # 사용자명과 비밀번호가 없으면 입력받기
        if not username:
            username = input("인스타그램 사용자명을 입력하세요: ")
        if not password:
            password = getpass.getpass("인스타그램 비밀번호를 입력하세요: ")
        
        try:
            # 인스타그램 로그인 페이지로 이동
            self.driver.get(f"{self.base_url}/accounts/login/")
            
            # 쿠키 정책 동의 버튼 클릭 (있을 경우)
            try:
                cookie_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'Allow')]"))
                )
                cookie_button.click()
            except:
                pass
            
            # 로그인 폼 찾기 및 입력
            username_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='username']"))
            )
            password_input = self.driver.find_element(By.CSS_SELECTOR, "input[name='password']")
            
            # 입력 필드 클리어 및 텍스트 입력
            username_input.clear()
            username_input.send_keys(username)
            password_input.clear()
            password_input.send_keys(password)
            
            # 로그인 버튼 클릭
            login_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
            )
            login_button.click()
            
            # 로그인 후 페이지 로딩 대기
            try:
                # 다양한 로그인 후 화면 처리
                
                # 가능한 경우 1: 정보 저장 묻는 팝업
                save_info_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Not Now')]"))
                )
                save_info_button.click()
            except:
                pass
            
            try:
                # 가능한 경우 2: 알림 설정 묻는 팝업
                notifications_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Not Now')]"))
                )
                notifications_button.click()
            except:
                pass
            
            # 성공적으로 로그인되었는지 확인
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Search')]"))
                )
                print("로그인 성공!")
                
                # 쿠키 저장
                cookies = self.driver.get_cookies()
                with open(cookies_file, 'w') as f:
                    json.dump(cookies, f)
                
                return True
            except:
                print("로그인에 실패했습니다. 사용자명과 비밀번호를 확인하세요.")
                return False
                
        except Exception as e:
            print(f"로그인 중 오류 발생: {e}")
            return False
    
    def search_hashtag(self, hashtag):
        """
        해시태그 검색
        
        Args:
            hashtag (str): 검색할 해시태그 (# 제외)
            
        Returns:
            bool: 검색 성공 여부
        """
        if not self.driver:
            print("드라이버가 초기화되지 않았습니다. 먼저 로그인하세요.")
            return False
        
        try:
            # 검색 URL로 직접 이동
            search_url = f"{self.base_url}/explore/tags/{hashtag}/"
            self.driver.get(search_url)
            
            # 해시태그 페이지 로딩 대기
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "article div a"))
            )
            
            print(f"#{hashtag} 해시태그 검색 결과 페이지 로드 완료")
            return True
            
        except Exception as e:
            print(f"해시태그 검색 중 오류 발생: {e}")
            return False
    
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
        initial_posts = set(self.driver.find_elements(By.CSS_SELECTOR, "article div a"))
        print(f"초기 포스트 수: {len(initial_posts)}")
        
        # 스크롤 수행
        for i in range(scroll_count):
            # 페이지 끝으로 스크롤
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            print(f"스크롤 {i+1}/{scroll_count} 완료")
            
            # 새 콘텐츠 로드 대기
            time.sleep(scroll_pause)
        
        # 최종 포스트 링크 수
        final_posts = set(self.driver.find_elements(By.CSS_SELECTOR, "article div a"))
        print(f"최종 포스트 수: {len(final_posts)}")
        
        return len(final_posts)
    
    def collect_posts(self, max_posts=10):
        """
        포스트 정보 수집
        
        Args:
            max_posts (int): 수집할 최대 포스트 수
            
        Returns:
            list: 수집된 포스트 정보 목록
        """
        if not self.driver:
            print("드라이버가 초기화되지 않았습니다.")
            return []
        
        posts = []
        post_links = []
        
        try:
            # 포스트 링크 수집
            elements = self.driver.find_elements(By.CSS_SELECTOR, "article div a")
            
            for element in elements:
                if len(post_links) >= max_posts:
                    break
                
                try:
                    href = element.get_attribute("href")
                    if href and "/p/" in href and href not in post_links:
                        post_links.append(href)
                except:
                    continue
            
            print(f"수집된 포스트 링크 수: {len(post_links)}")
            
            # 각 포스트 정보 수집
            for i, link in enumerate(post_links[:max_posts]):
                print(f"포스트 {i+1}/{len(post_links[:max_posts])} 수집 중...")
                
                try:
                    # 포스트 페이지로 이동
                    self.driver.get(link)
                    
                    # 포스트 로딩 대기
                    self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "time"))
                    )
                    
                    # 포스트 정보 수집
                    post_info = self._extract_post_info()
                    post_info['url'] = link
                    posts.append(post_info)
                    
                    # 속도 제한 방지를 위한 딜레이
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"포스트 정보 수집 중 오류 발생: {e}")
                    continue
            
            return posts
            
        except Exception as e:
            print(f"포스트 수집 중 오류 발생: {e}")
            return posts
    
    def _extract_post_info(self):
        """
        현재 열린 포스트에서 정보를 추출
        
        Returns:
            dict: 추출된 포스트 정보
        """
        post_info = {
            'username': 'unknown',
            'date': 'unknown',
            'likes': 0,
            'caption': '',
            'hashtags': [],
            'image_url': '',
            'comments': []
        }
        
        try:
            # 사용자명 추출
            try:
                username_elem = self.driver.find_element(By.CSS_SELECTOR, "a.notranslate")
                post_info['username'] = username_elem.text
            except:
                pass
            
            # 날짜 추출
            try:
                date_elem = self.driver.find_element(By.CSS_SELECTOR, "time")
                post_info['date'] = date_elem.get_attribute("datetime")
            except:
                pass
            
            # 좋아요 수 추출
            try:
                likes_text = self.driver.find_element(By.CSS_SELECTOR, "section span").text
                post_info['likes'] = self._parse_count(likes_text)
            except:
                pass
            
            # 캡션 추출
            try:
                caption_elem = self.driver.find_element(By.CSS_SELECTOR, "div._a9zs span")
                post_info['caption'] = caption_elem.text
                
                # 해시태그 추출
                hashtags = re.findall(r"#(\w+)", post_info['caption'])
                post_info['hashtags'] = hashtags
            except:
                pass
            
            # 이미지 URL 추출
            try:
                img_elem = self.driver.find_element(By.CSS_SELECTOR, "article img")
                post_info['image_url'] = img_elem.get_attribute("src")
            except:
                pass
            
            # 댓글 추출 (최대 5개)
            try:
                comments = self.driver.find_elements(By.CSS_SELECTOR, "ul div._a9zs")[:5]
                for comment in comments:
                    post_info['comments'].append(comment.text)
            except:
                pass
            
        except Exception as e:
            print(f"포스트 정보 추출 중 오류 발생: {e}")
        
        return post_info
    
    def _parse_count(self, count_text):
        """
        좋아요, 팔로워 등의 텍스트 수를 정수로 변환
        
        Args:
            count_text (str): 변환할 텍스트 (예: "1,234", "1.2k", "1.2m")
            
        Returns:
            int: 변환된 수
        """
        try:
            count_text = count_text.lower().replace(',', '')
            if 'k' in count_text:
                return int(float(count_text.replace('k', '')) * 1000)
            elif 'm' in count_text:
                return int(float(count_text.replace('m', '')) * 1000000)
            else:
                return int(count_text)
        except:
            return 0
    
    def save_to_csv(self, posts, filename=None):
        """
        수집한 포스트 정보를 CSV 파일로 저장
        
        Args:
            posts (list): 저장할 포스트 정보 목록
            filename (str): 저장할 파일명 (기본값: None)
            
        Returns:
            str: 저장된 파일 경로
        """
        if not filename:
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"instagram_posts_{current_time}.csv"
        
        file_path = os.path.join(self.results_dir, filename)
        
        try:
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                # 필드명 결정
                fieldnames = ['username', 'date', 'likes', 'caption', 'hashtags', 'image_url', 'url', 'comments']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for post in posts:
                    # 해시태그와 댓글은 리스트이므로 문자열로 변환
                    post_row = post.copy()
                    post_row['hashtags'] = ', '.join(post_row['hashtags'])
                    post_row['comments'] = '\n'.join(post_row['comments'])
                    
                    writer.writerow(post_row)
            
            print(f"포스트 정보가 {file_path} 파일에 저장되었습니다.")
            return file_path
            
        except Exception as e:
            print(f"CSV 파일 저장 중 오류 발생: {e}")
            return None
    
    def search_user(self, username):
        """
        사용자 프로필 검색
        
        Args:
            username (str): 검색할 사용자명
            
        Returns:
            bool: 검색 성공 여부
        """
        if not self.driver:
            print("드라이버가 초기화되지 않았습니다. 먼저 로그인하세요.")
            return False
        
        try:
            # 사용자 프로필 URL로 직접 이동
            profile_url = f"{self.base_url}/{username}/"
            self.driver.get(profile_url)
            
            # 프로필 페이지 로딩 대기
            try:
                self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "header section"))
                )
                print(f"{username} 사용자의 프로필 페이지 로드 완료")
                return True
            except:
                print(f"{username} 사용자를 찾을 수 없습니다.")
                return False
            
        except Exception as e:
            print(f"사용자 검색 중 오류 발생: {e}")
            return False
    
    def get_user_info(self):
        """
        현재 열린 사용자 프로필에서 정보 추출
        
        Returns:
            dict: 사용자 프로필 정보
        """
        if not self.driver:
            print("드라이버가 초기화되지 않았습니다.")
            return {}
        
        user_info = {
            'username': '',
            'name': '',
            'bio': '',
            'posts_count': 0,
            'followers': 0,
            'following': 0,
            'profile_image_url': ''
        }
        
        try:
            # 사용자명 추출
            try:
                username_elem = self.driver.find_element(By.CSS_SELECTOR, "header h2")
                user_info['username'] = username_elem.text
            except:
                pass
            
            # 이름 추출
            try:
                name_elem = self.driver.find_element(By.CSS_SELECTOR, "header h1")
                user_info['name'] = name_elem.text
            except:
                pass
            
            # 프로필 이미지 URL 추출
            try:
                img_elem = self.driver.find_element(By.CSS_SELECTOR, "header img")
                user_info['profile_image_url'] = img_elem.get_attribute("src")
            except:
                pass
            
            # 게시물, 팔로워, 팔로잉 수 추출
            try:
                counts = self.driver.find_elements(By.CSS_SELECTOR, "header li span")
                if len(counts) >= 3:
                    user_info['posts_count'] = self._parse_count(counts[0].text)
                    user_info['followers'] = self._parse_count(counts[1].text)
                    user_info['following'] = self._parse_count(counts[2].text)
            except:
                pass
            
            # 바이오 추출
            try:
                bio_elem = self.driver.find_element(By.CSS_SELECTOR, "header div > span")
                user_info['bio'] = bio_elem.text
            except:
                pass
            
        except Exception as e:
            print(f"사용자 정보 추출 중 오류 발생: {e}")
        
        return user_info
    
    def close(self):
        """브라우저 종료"""
        if self.driver:
            self.driver.quit()
            print("브라우저가 종료되었습니다.")


# 사용 예시
if __name__ == "__main__":
    crawler = InstagramCrawler(headless=False)
    
    # 로그인 (사용자명과 비밀번호를 직접 입력할 수도 있습니다)
    logged_in = crawler.login()
    
    if logged_in:
        # 해시태그 검색 예시
        print("\n=== 해시태그 검색 예시 ===")
        hashtag = input("검색할 해시태그를 입력하세요(#제외): ")
        
        if crawler.search_hashtag(hashtag):
            # 스크롤하여 더 많은 포스트 로드
            crawler.scroll_to_load_more(scroll_count=3)
            
            # 포스트 정보 수집
            max_posts = int(input("수집할 최대 포스트 수를 입력하세요: "))
            posts = crawler.collect_posts(max_posts=max_posts)
            
            # 결과 저장
            crawler.save_to_csv(posts, f"{hashtag}_posts.csv")
        
        # 사용자 검색 예시
        print("\n=== 사용자 검색 예시 ===")
        username = input("검색할 사용자명을 입력하세요: ")
        
        if crawler.search_user(username):
            # 사용자 정보 추출
            user_info = crawler.get_user_info()
            print(f"사용자 정보: {user_info}")
            
            # 스크롤하여 사용자의 포스트 로드
            crawler.scroll_to_load_more(scroll_count=2)
            
            # 사용자의 포스트 정보 수집
            user_posts = crawler.collect_posts(max_posts=5)
            
            # 결과 저장
            crawler.save_to_csv(user_posts, f"{username}_posts.csv")
    
    # 크롤러 종료
    crawler.close() 