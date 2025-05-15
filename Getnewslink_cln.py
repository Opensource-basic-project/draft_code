import json
import urllib.request
import urllib.parse
import time
from sentence_transformers import SentenceTransformer, util

client_id = "네이버 API id"
client_secret = "네이버 API secret"

query = urllib.parse.quote('"국민연금법"')

#  문장 임베딩 모델 로드
model = SentenceTransformer('all-MiniLM-L6-v2')

#  이미 출력한 제목 리스트 (중복 유사성 검사용)
printed_titles = []

for start in range(1, 1000, 10):
    url = f"https://openapi.naver.com/v1/search/news?query={query}&display=10&start={start}"
    
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)
    request.add_header("User-Agent", "Mozilla/5.0")
    
    try:
        response = urllib.request.urlopen(request)
        data = json.loads(response.read().decode("utf-8"))
        
        for item in data["items"]:
            title = item["title"].replace("<b>", "").replace("</b>", "")
            link = item["link"]

            if "국민연금법" in title and "n.news.naver.com" in link:
                #  현재 제목 임베딩
                current_embedding = model.encode(title, convert_to_tensor=True)

                is_similar = False
                for prev_title in printed_titles:
                    prev_embedding = model.encode(prev_title, convert_to_tensor=True)
                    similarity = util.pytorch_cos_sim(current_embedding, prev_embedding).item()

                    if similarity > 0.7:
                        is_similar = True
                        break

                if not is_similar:
                    print(title, link)
                    printed_titles.append(title)

    except urllib.error.HTTPError as e:
        print(f"[HTTPError] {e.code}: {e.reason}")
        break
    except Exception as e:
        print(f"[Error] {e}")
        break

    time.sleep(0.3)
