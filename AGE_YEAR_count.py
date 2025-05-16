import urllib.request
import urllib.parse
import json
import time
from collections import defaultdict, Counter
from datetime import datetime
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
import platform
import numpy as np

open_api_key = "API key 입력"

#  한국어 폰트 설정
if platform.system() == 'Windows':
    plt.rc('font', family='Malgun Gothic')
elif platform.system() == 'Darwin':
    plt.rc('font', family='AppleGothic')
else:
    plt.rc('font', family='NanumGothic')
plt.rcParams['axes.unicode_minus'] = False

# 국회 임기 정보
AGE_PERIODS = {
    20: (datetime(2016, 5, 30), datetime(2020, 5, 29)),
    21: (datetime(2020, 5, 30), datetime(2024, 5, 29)),
    22: (datetime(2024, 5, 30), datetime(2028, 5, 29)),  # 22대 임시 종료일
}

def get_bills_by_age(age):
    endpoint = "https://open.assembly.go.kr/portal/openapi/TVBPMBILL11"
    p_size = 1000
    bills = []
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
            data = response.read()
            json_data = json.loads(data)

            items = json_data.get("TVBPMBILL11", [])
            if len(items) < 2 or "row" not in items[1]:
                break

            rows = items[1]["row"]
            if isinstance(rows, dict):
                rows = [rows]

            for row in rows:
                propose_dt = row.get("PROPOSE_DT", "")
                bill_name = row.get("BILL_NAME", "")
                if propose_dt and bill_name:
                    bills.append((propose_dt, bill_name, age))

            if len(rows) < p_size:
                break

            p_index += 1
            time.sleep(0.5)

        except Exception as e:
            print(f"❌ AGE {age} 페이지 {p_index} 실패: {e}")
            break

    return bills

def collect_bills(start_age, end_age):
    all_bills = []
    for age in range(start_age, end_age + 1):
        print(f" {age}대 국회 법안 수집 중...")
        bills = get_bills_by_age(age)
        print(f" {age}대 국회: {len(bills)}건 수집 완료.")
        all_bills.extend(bills)
    return all_bills

def process_bills(bills, start_year, end_year):
    if not bills:
        raise ValueError("입력된 법안 데이터가 없습니다.")

    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 1)
    months = []
    current = start_date
    while current <= end_date:
        months.append(current.strftime("%Y-%m"))
        current += relativedelta(months=1)

    month_counts = Counter()
    month_bills = defaultdict(list)
    age_counts = Counter()

    for propose_dt, name, age in bills:
        try:
            dt = datetime.strptime(propose_dt, "%Y-%m-%d")
            month_str = dt.strftime("%Y-%m")
            if months[0] <= month_str <= months[-1]:
                month_counts[month_str] += 1
                month_bills[month_str].append(name)
                age_counts[age] += 1
        except ValueError:
            continue

    vertical_lines = {}
    for age, (start_dt, _) in AGE_PERIODS.items():
        month_str = start_dt.strftime("%Y-%m")
        if months[0] <= month_str <= months[-1]:
            idx = months.index(month_str)
            vertical_lines[age] = idx

    return months, month_counts, month_bills, vertical_lines, age_counts

def plot_bills(months, month_counts, vertical_lines):
    x = np.arange(len(months))
    y = np.array([month_counts.get(m, 0) for m in months])

    fig, ax = plt.subplots(figsize=(16, 6))

    # 꺾은선 그래프
    ax.plot(x, y, color='blue', linewidth=2, marker='o', markersize=5)

    # 각 점 위에 수치 표시
    for i, val in enumerate(y):
        if val > 0:
            ax.text(i, val + 0.5, str(val), ha='center', va='bottom', fontsize=8, color='black')

    ax.set_ylabel("법안 수")
    ax.grid(True)

    # 하단: 월 레이블
    ax.set_xticks(x)
    ax.set_xticklabels([m[5:] for m in months], fontsize=9)
    ax.set_xlabel("월")

    # 상단: 연도 레이블 (별도 축)
    ax2 = ax.twiny()
    ax2.set_xlim(ax.get_xlim())

    year_positions = []
    year_labels = []
    prev_year = None
    for i, m in enumerate(months):
        year = m[:4]
        if year != prev_year:
            year_positions.append(i + 5.5)
            year_labels.append(year)
            prev_year = year

    ax2.set_xticks(year_positions)
    ax2.set_xticklabels(year_labels, fontsize=10)
    ax2.xaxis.set_ticks_position('top')
    ax2.xaxis.set_label_position('top')
    ax2.set_xlabel("연도", labelpad=10)

    # AGE 수직선 및 텍스트
    for age, idx in vertical_lines.items():
        ax.axvline(x=idx, color='lightblue', linestyle='--', alpha=0.8)
        ax.text(idx + 0.5, max(y) * 0.95, f"{age}대", rotation=90,
                verticalalignment='top', color='skyblue', fontsize=10)

    plt.tight_layout()
    plt.show()

def print_monthly_info(months, month_counts, month_bills, age_counts):
    print(" 국회 대수별 총 발의 법안 수:")
    for age in sorted(age_counts):
        print(f" {age}대 국회 총 발의 법안: {age_counts[age]}건")

    print("\n 월별 법안 발의 현황:")
    for m in months:
        count = month_counts.get(m, 0)
        print(f"\n {m} - 총 {count}건")
        for title in month_bills.get(m, []):
            print(f"  - {title}")


# 실행
if __name__ == "__main__":

    #2016~2025 조회가능 (20대수 이전 == 2016 5월 이전 데이터는 조회불가)
    #갱신되는 대로 2025년도 법안 조회 모두가능

    start_year = 2024
    end_year = 2024
    start_age = 20
    end_age = 22

    
    # 2024 5월~12월 (21대 국회부터 24년 끝까지) >> 7028 확인완료
    # 2016~2025 대수별 대조 완료 >> 24141  25858  10269 확인완료

    bills = collect_bills(start_age, end_age)
    months, month_counts, month_bills, vertical_lines, age_counts = process_bills(bills, start_year, end_year)
    print_monthly_info(months, month_counts, month_bills, age_counts)
    plot_bills(months, month_counts, vertical_lines)


