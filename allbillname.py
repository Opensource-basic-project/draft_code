import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import time

open_api_key = "API key 입력"

def get_all_bills_by_age(age):
    endpoint = "https://open.assembly.go.kr/portal/openapi/TVBPMBILL11"
    p_size = 1000  # Open API 최대 페이지 크기
    bill_names = []

    print(f"\n AGE = {age} 국회 법안 수집 시작")

    p_index = 1
    while True:
        params = {
            "KEY": open_api_key,
            "Type": "xml",
            "pIndex": p_index,
            "pSize": p_size,
            "AGE": age
        }

        query = urllib.parse.urlencode(params)
        url = f"{endpoint}?{query}"
        print(f" 요청 중... (AGE {age}, 페이지 {p_index})")

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            response = urllib.request.urlopen(req)
            data = response.read()

            root = ET.fromstring(data)

            rows = root.findall("row")
            if not rows:
                print(" 더 이상 데이터가 없습니다.")
                break

            for row in rows:
                name = row.find("BILL_NAME")
                if name is not None:
                    bill_names.append(name.text)

            print(f" 수집됨: {len(rows)}건 (누적: {len(bill_names)}건)")

            p_index += 1
            time.sleep(0.5)  # 과속 방지

        except Exception as e:
            print(f" 요청 실패 (AGE {age}, 페이지 {p_index}): {e}")
            break

    print(f"\n AGE {age} 전체 수집 완료: {len(bill_names)}건\n")
    return bill_names

# AGE 20, 21, 22 수집
all_bills_by_age = {}

for age in [20, 21, 22]:
    bills = get_all_bills_by_age(age)
    all_bills_by_age[age] = bills

# 결과 출력
for age, bills in all_bills_by_age.items():
    print(f"\n AGE {age} 법안 목록 (총 {len(bills)}건):\n")
    for i, name in enumerate(bills, start=1):
        print(f"{i}. {name}")
