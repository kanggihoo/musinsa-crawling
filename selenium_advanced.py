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

def advanced_browser_example():
    """
    셀레니움을 이용한 고급 브라우저 예제:
    - 브라우저 창 열기
    - 구글에서 검색 수행
    - 스크린샷 찍기
    - 특정 요소 대기 및 클릭
    """
    print("고급 브라우저 예제를 시작합니다...")
    
    # 스크린샷 저장할 디렉토리 확인 및 생성
    screenshots_dir = "./screenshots"
    if not os.path.exists(screenshots_dir):
        os.makedirs(screenshots_dir)
        print(f"'{screenshots_dir}' 디렉토리를 생성했습니다.")
    
    # Chrome 옵션 설정
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-notifications")  # 알림 차단
    
    # 자동화 감지 방지
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    
    try:
        # Chrome 드라이버 초기화
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # 명시적 대기 설정 (최대 10초)
        wait = WebDriverWait(driver, 10)
        
        # 구글 접속
        print("구글에 접속 중...")
        driver.get("https://www.google.com")
        
        # 첫 번째 스크린샷 저장
        driver.save_screenshot(f"{screenshots_dir}/google_home.png")
        print(f"홈페이지 스크린샷 저장: {screenshots_dir}/google_home.png")
        
        # 검색창 찾기 및 검색어 입력
        search_term = "Selenium WebDriver Python"
        print(f"검색어 입력: '{search_term}'")
        
        # 검색창 요소가 로드될 때까지 대기
        search_box = wait.until(
            EC.presence_of_element_located((By.NAME, "q"))
        )
        
        # 검색창에 텍스트 입력하고 검색
        search_box.clear()
        search_box.send_keys(search_term)
        search_box.send_keys(Keys.RETURN)
        
        # 검색 결과가 로드될 때까지 대기
        wait.until(
            EC.presence_of_element_located((By.ID, "search"))
        )
        
        print("검색 결과 페이지가 로드되었습니다.")
        
        # 검색 결과 페이지 스크린샷
        driver.save_screenshot(f"{screenshots_dir}/search_results.png")
        print(f"검색 결과 스크린샷 저장: {screenshots_dir}/search_results.png")
        
        # 첫 번째 검색 결과 클릭
        try:
            first_result = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div.g a"))
            )
    
            result_title = first_result.text
            print(f"첫 번째 검색 결과: '{result_title}'")
            
            # 결과 클릭
            print("첫 번째 검색 결과를 클릭합니다...")
            first_result.click()
            
            # 페이지 로드 대기
            time.sleep(3)
            
            # 이동한 페이지 스크린샷
            driver.save_screenshot(f"{screenshots_dir}/first_result_page.png")
            print(f"클릭한 페이지 스크린샷 저장: {screenshots_dir}/first_result_page.png")
            
            # 현재 URL 출력
            print(f"현재 페이지 URL: {driver.current_url}")
            
        except Exception as e:
            print(f"검색 결과 클릭 중 오류 발생: {e}")
        
        # 브라우저 탭/창 관리 예제
        print("\n브라우저 탭 관리 예제:")
        
        # 새 탭 열기
        driver.execute_script("window.open('');")
        
        # 탭 목록 확인
        tabs = driver.window_handles
        print(f"열린 탭 수: {len(tabs)}")
        
        # 두 번째 탭으로 전환
        driver.switch_to.window(tabs[1])
        print("새 탭으로 전환했습니다.")
        
        # 새 탭에서 다른 사이트 접속
        driver.get("https://www.python.org")
        print("Python 공식 사이트에 접속했습니다.")
        
        # Python 사이트 스크린샷
        driver.save_screenshot(f"{screenshots_dir}/python_org.png")
        print(f"Python.org 스크린샷 저장: {screenshots_dir}/python_org.png")
        
        # 원래 탭으로 돌아가기
        driver.switch_to.window(tabs[0])
        print("원래 탭으로 돌아왔습니다.")
        
        # 잠시 대기
        print("5초 동안 브라우저를 유지합니다...")
        time.sleep(5)
        
    except Exception as e:
        print(f"실행 중 오류 발생: {e}")
    
    finally:
        # 브라우저 종료
        print("브라우저를 종료합니다.")
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    advanced_browser_example() 