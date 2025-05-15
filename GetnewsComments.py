from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

# 크롬 드라이버 설정
options = Options()
options.add_argument("--headless")  # 창 없이 실행하려면 주석 해제
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome()

#  네이버 뉴스 URL (댓글 있는 기사)
url = "https://n.news.naver.com/mnews/article/comment/417/0001065535?sid=100"
driver.get(url)
time.sleep(2) # 웹사이트 네트워크상태 고려 : 기다릴시간 조정 2~4

#  '댓글 더보기' 버튼 반복 클릭 (최대 수집 위해)
while True:
    try:
        more_btn = driver.find_element(By.CLASS_NAME, "u_cbox_btn_more")
        more_btn.click()
        time.sleep(1)
    except:
        break  # 버튼 없으면 종료

#  댓글 추출
comments = driver.find_elements(By.CSS_SELECTOR, "span.u_cbox_contents")
for idx, comment in enumerate(comments, 1):
    print(f"[{idx}] {comment.text}")

driver.quit()
