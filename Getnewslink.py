import json
import urllib.request
import urllib.parse # URL 인코딩 모듈
import time

client_id = "API key 입력"
client_secret = "w8FtGreOKb"
# 네이버 API key 

query = urllib.parse.quote('"최저임금법"')
# URL에 맞게 인코딩

for start in range(1, 1000, 10):  # start는 최대 1000까지 가능
    url = f"https://openapi.naver.com/v1/search/news?query={query}&display=10&start={start}"
    # 인코딩된 검색어 포함한 뉴스검색 API URL
    
    request = urllib.request.Request(url)  # API 호출 객체 request
    request.add_header("X-Naver-Client-Id", client_id) 
    request.add_header("X-Naver-Client-Secret", client_secret) 
    # ID, secret 정보 입력
    request.add_header("User-Agent", "Mozilla/5.0") # UserAgent설정 (차단방지)
	
    try:
        response = urllib.request.urlopen(request) # 응답받는거
        data = json.loads(response.read().decode("utf-8")) 
        # 응답(json)을 파이썬객체로 변환하여 읽음 data.
        

        for item in data["items"]:
            title = item["title"].replace("<b>", "").replace("</b>", "")
            link = item["link"]
            # 아이템추출..

            # "최저임금법" 포함 + n.news.naver.com 도메인만 출력
            if "최저임금법" in title and "n.news.naver.com" in link:
                print(title, link) #제목과 링크 출력
               

    except urllib.error.HTTPError as e:
        print(f"[HTTPError] {e.code}: {e.reason}")
        break
    except Exception as e:
        print(f"[Error] {e}")
        break

    time.sleep(0.3)  # 과도한 호출 방지
