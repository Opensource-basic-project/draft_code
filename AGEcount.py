import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import time
import json
from collections import defaultdict, Counter
from datetime import datetime

open_api_key = "API key 입력"

def get_bills_by_age(age):
    endpoint = "https://open.assembly.go.kr/portal/openapi/TVBPMBILL11"
    p_size = 1000
    bill_list = []

    p_index = 1
    while True:
        params = {
            "KEY": open_api_key,
            "Type": "json",
            "pIndex": p_index,
            "pSize": p_size,
            "AGE": age
        }

        query = urllib.parse.urlencode(params)
        url = f"{endpoint}?{query}"

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            response = urllib.request.urlopen(req)
            data = json.loads(response.read())

            rows = data.get("TVBPMBILL11", [])
            if len(rows) < 2:
                break

            rows = rows[1].get("row", [])
            if not rows:
                break

            for row in rows:
                bill = {
                    "name": row.get("BILL_NAME", ""),
                    "propose_dt": row.get("PROPOSE_DT", ""),
                    "proc_result": row.get("PROC_RESULT_CD", ""),
                }
                bill_list.append(bill)

            p_index += 1
            time.sleep(1)

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

# (1) 대수별 발의 건수 집계
print("\n (1) 대수별 발의 건수")
for age, bills in all_bills_by_age.items():
    print(f"- AGE {age}: {len(bills)}건")


