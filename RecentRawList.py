from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from datetime import datetime
import time


today = datetime.today().strftime("%Y%m%d")
max_count = 10  # 최대 출력 개수

# Selenium 설정
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
driver = webdriver.Chrome(options=options)

url = f"https://www.law.go.kr/LSW/nwRvsLsPop.do?p_epubdt={today}"
driver.get(url)
time.sleep(2)


try:
    rows = driver.find_elements(By.CSS_SELECTOR, "table.tbl3 tbody tr")

    results = []
    for i, row in enumerate(rows):
        if i >= max_count:
            break
        tds = row.find_elements(By.TAG_NAME, "td")
        if len(tds) >= 7:
            results.append({
                "소관부처": tds[1].text.strip(),
                "제/개정 구분": tds[2].text.strip(),
                "공포일자": tds[6].text.strip(),
                "실행일자": tds[7].text.strip()
            })

    print(f"\n 공포일자: {today} 기준 법령 목록 (최대 {max_count}건)\n")
    for i, item in enumerate(results, start=1):
        print(f"[{i}]")
        print(f"  소관부처     : {item['소관부처']}")
        print(f"  제/개정 구분 : {item['제/개정 구분']}")
        print(f"  공포일자     : {item['공포일자']}")
        print(f"  실행일자    : {item['실행일자']}\n")

except Exception as e:
    print(" 에러 발생:", e)

finally:
    driver.quit()
