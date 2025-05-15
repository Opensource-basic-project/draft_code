from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from transformers import pipeline
import matplotlib.pyplot as plt
import matplotlib
import time

# 댓글 내용과 해당 댓글의 부정/긍정 판별여부까지 같이 출력하도록 함

matplotlib.rc('font', family='NanumGothic')

# 크롬 드라이버 설정
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

# 뉴스 댓글 페이지 접속
url = "https://n.news.naver.com/mnews/article/comment/417/0001065535?sid=100"
driver.get(url)
time.sleep(4)

# '댓글 더보기' 버튼 클릭
while True:
    try:
        more_btn = driver.find_element(By.CLASS_NAME, "u_cbox_btn_more")
        more_btn.click()
        time.sleep(1)
    except:
        break

# 댓글 수집
comments = driver.find_elements(By.CSS_SELECTOR, "span.u_cbox_contents")
texts = [c.text.strip() for c in comments if c.text.strip() != ""]

driver.quit()

# 감정 분석 모델 로딩
classifier = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")

# 결과 초기화
result_counts = {"긍정적 인식": 0, "부정적 인식": 0, "중립": 0}

# 감정 라벨 매핑
label_map = {
    "1 star": "부정적 인식",
    "2 stars": "부정적 인식",
    "3 stars": "중립",
    "4 stars": "긍정적 인식",
    "5 stars": "긍정적 인식"
}

# 댓글별 분석 및 출력
print("\n 댓글 감정 분석 결과:\n")
for text in texts:
    result = classifier(text)[0]
    label = result["label"]
    sentiment = label_map.get(label, "중립")

    print(f"{text} [{sentiment}]")

    result_counts[sentiment] += 1

# 파이 차트 시각화
labels = list(result_counts.keys())
sizes = list(result_counts.values())
colors = ['#ff9999', '#ffc000', '#8fd9b6']

plt.figure(figsize=(6, 6))
plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
plt.title("댓글 감정 분석 결과 (긍정/부정/중립)")
plt.axis('equal')
plt.show()
