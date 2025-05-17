
import urllib.request
import urllib.parse
import json
from collections import Counter, defaultdict
import time
import datetime

### AGE 20~22 법안 처리결과별 건수
#json 파싱, 총 정제, 데이터 검수 완료


open_api_key = "API key 입력"
pSize = 1000


def get_bills_by_age_json(age):
    endpoint = "https://open.assembly.go.kr/portal/openapi/TVBPMBILL11"
    bill_list = []
    p_index = 1

    while True:
        params = {
            "KEY": open_api_key,
            "Type": "json",
            "pIndex": p_index,
            "pSize": pSize,
            "AGE": age
        }

        query = urllib.parse.urlencode(params)
        url = f"{endpoint}?{query}"

        for attempt in range(100):  # 최대 100회 재시도 (네트워크 문제 최소화)
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=10) as response:
                    data = response.read()
                json_data = json.loads(data)

                items = json_data.get("TVBPMBILL11", [])
                if len(items) < 2 or "row" not in items[1]:
                    return bill_list

                rows = items[1]["row"]
                if isinstance(rows, dict):
                    rows = [rows]

                for row in rows:
                    bill = {
                        "name": row.get("BILL_NAME", ""),
                        "propose_dt": row.get("PROPOSE_DT", ""),
                        "proc_result": row.get("PROC_RESULT_CD", "")
                    }
                    bill_list.append(bill)

                if len(rows) < pSize:
                    return bill_list  # 마지막 페이지

                p_index += 1
                time.sleep(0.3)
                break  # 성공했으므로 재시도 루프 종료

            except Exception as e:
                wait_time = min(2 * (attempt + 1), 30)
                print(f" AGE {age}, pIndex {p_index}, 시도 {attempt + 1}회 실패: {e}. {wait_time}초 대기 후 재시도")
                time.sleep(wait_time)
        else:
            print(f" AGE {age} 페이지 {p_index} 수집 실패. 다음 페이지로 건너뜀")
            p_index += 1
            continue


def get_age_by_year_range(start_year, end_year):
    """
    주어진 연도 범위(start_year~end_year)에 해당하는 국회 대수를 반환.
    기준:
        - 20대: 2016.05 ~ 2020.05
        - 21대: 2020.05 ~ 2024.05
        - 22대: 2024.05 ~ 2028.05 (진행 중 가능성)
    """
    age_to_range = {
        20: (2016, 2020),
        21: (2020, 2024),
        22: (2024, 2028),
    }
    return [age for age, (start, end) in age_to_range.items() if end > start_year and start <= end_year]


# === 실행부 ===
start_year = 2016 #시작년도
end_year = 2024 #끝 년도

ages_to_check = get_age_by_year_range(start_year, end_year)
print(f"\n {start_year}년 ~ {end_year}년 사이 대수 추출: {ages_to_check}")

all_bills_by_age = {}
for age in ages_to_check:
    print(f"\n AGE {age} 법안 수집 중...")
    bills = get_bills_by_age_json(age)
    # 연도 필터링
    filtered_bills = []
    for bill in bills:
        try:
            y = int(bill["propose_dt"][:4])
            if start_year <= y <= end_year:
                filtered_bills.append(bill)
        except:
            continue
    all_bills_by_age[age] = filtered_bills
    print(f" AGE {age} 총 {len(filtered_bills)}건 수집 완료.")

# === 처리결과 분석 ===
print("\n 처리결과별 건수 (대수별)")

total_proc_counter = Counter()

for age, bills in all_bills_by_age.items():
    print(f"\n AGE {age}")
    age_proc_counter = Counter()

    for bill in bills:
        result = (bill.get("proc_result") or "").strip()
        if not result:
            result = "미확정"
        age_proc_counter[result] += 1
        total_proc_counter[result] += 1

    for result, count in age_proc_counter.items():
        print(f"- {result}: {count}건")
    print(f" AGE {age} 합계: {sum(age_proc_counter.values())}건")

# === 전체 합계 ===
print("\n 전체 합계")
for result, count in total_proc_counter.items():
    print(f"- {result}: {count}건")
print(f" 전체 총합: {sum(total_proc_counter.values())}건")

