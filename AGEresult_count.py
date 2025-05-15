import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import time
from collections import defaultdict, Counter
from datetime import datetime

### AGE 20~22 법안 처리결과별 건수 (아마 표시는 22대수만 할 것으로 예상)
### AGE 별 법안발의개수와 함께 처리한 테스트 코드 (초안)

open_api_key = "API key 입력"

def get_bills_by_age(age):
    endpoint = "https://open.assembly.go.kr/portal/openapi/TVBPMBILL11"
    p_size = 1000
    bill_list = []

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

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            response = urllib.request.urlopen(req)
            data = response.read()

            root = ET.fromstring(data)
            rows = root.findall("row")
            if not rows:
                break

            for row in rows:
                bill = {
                    "name": row.findtext("BILL_NAME", ""),
                    "propose_dt": row.findtext("PROPOSE_DT", ""),  # 발의일
                    "proc_result": row.findtext("PROC_RESULT_CD", ""),  # 처리결과코드
                }
                bill_list.append(bill)

            p_index += 1
            time.sleep(0.5)

        except Exception as e:
            print(f" AGE {age} 페이지 {p_index} 실패: {e}")
            break

    return bill_list

# 모든 AGE 수집
all_bills_by_age = {}
for age in [20, 21, 22]:
    print(f"\n AGE {age} 법안 수집 중...")
    bills = get_bills_by_age(age)
    all_bills_by_age[age] = bills
    print(f" AGE {age} 총 {len(bills)}건 수집 완료.")



# (2) 미확정, 폐기, 부결, 원안가결, 수정가결 수치

print("\n🧾 (2) 처리결과별 건수")
proc_counter = Counter()
for age, bills in all_bills_by_age.items():
    for bill in bills:
        result = bill["proc_result"].strip()
        if not result:
            result = "미확정"
        proc_counter[result] += 1

# 처리결과코드 예시: '가결', '부결', '폐기', '철회', '미확정'
for result, count in proc_counter.items():
    print(f"- {result}: {count}건")
