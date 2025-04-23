from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

def open_browser():
    """
    셀레니움을 이용하여 기본 브라우저 창을 열고 웹사이트에 접속하는 기본 예제
    """
    print("브라우저를 초기화하는 중...")
    
    # Chrome 옵션 설정
    chrome_options = Options()
    # 브라우저가 보이게 하기 위해 headless 모드는 사용하지 않음
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--start-maximized")  # 브라우저 창 최대화
    chrome_options.add_argument("--disable-popup-blocking")  # 팝업 차단 해제
    
    # 자동화 감지 방지 (일부 웹사이트에서 필요할 수 있음)
    # chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # chrome_options.add_experimental_option("useAutomationExtension", False)
    
    try:
        # Chrome 드라이버 초기화 (자동으로 적절한 버전의 ChromeDriver 다운로드)
        # service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(options=chrome_options)
        
        print("브라우저가 성공적으로 열렸습니다.")
        
        # 웹사이트 방문
        url = "https://www.google.com"
        print(f"{url}에 접속 중...")
        driver.get(url)
        
        # 페이지 제목 출력
        print(f"페이지 제목: {driver.title}")
        
        # 잠시 대기 (브라우저 창 확인용)
        print("10초 동안 브라우저 창을 유지합니다...")
        time.sleep(10)
        
        # 브라우저 닫기
        print("브라우저를 종료합니다.")
        driver.quit()
        
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    open_browser() 