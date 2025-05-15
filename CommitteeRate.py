import urllib.request
import urllib.parse
import json
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# ====== 한글 폰트 설정 (자동 OS 감지) ======
import platform
if platform.system() == "Windows":
    plt.rc("font", family="Malgun Gothic")
elif platform.system() == "Darwin":
    plt.rc("font", family="AppleGothic")
plt.rcParams["axes.unicode_minus"] = False  # 마이너스 깨짐 방지

# ====== 공통 상수 ======
open_api_key = "API key 입력"
pSize = 1000


# 총 제출건수 수집
def get_total_submission_count(ages=[18, 19, 20]):
    endpoint = "https://open.assembly.go.kr/portal/openapi/nzivskufaliivfhpb"
    total = 0
    page = 1

    while True:
        params = {
            "KEY": open_api_key,
            "Type": "json",
            "pIndex": page,
            "pSize": 100
        }
        query = urllib.parse.urlencode(params)
        url = f"{endpoint}?{query}"

        try:
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0'}
            ) #user-agent 포함, 오류방지
            response = urllib.request.urlopen(req)
            data = response.read()
            json_data = json.loads(data)

            items = json_data.get("nzivskufaliivfhpb", [])
            if len(items) < 2 or "row" not in items[1]:
                break

            rows = items[1]["row"]
            if isinstance(rows, dict):
                rows = [rows]

            for row in rows:
                age_text = row.get("ERACO", "")
                if "대" in age_text:
                    age_num = age_text.split("대")[0].strip()
                    if age_num.isdigit() and int(age_num) in ages:
                        submit = row.get("SBM")
                        total += int(submit)

            if len(rows) < 100:
                break
            page += 1

        except Exception as e:
            print(f"❌ 요청 실패: {e}")
            break

    return total


# 위원회별 제출 건수 수집
def get_committee_submission_counts(ages=[18, 19, 20]):
    endpoint = "https://open.assembly.go.kr/portal/openapi/TVBPMBILL11"
    committee_counts = defaultdict(int)

    for age in ages:
        page = 1
        while True:
            params = {
                "KEY": open_api_key,
                "Type": "json",
                "pIndex": page,
                "pSize": pSize,
                "AGE": age
            }
            query = urllib.parse.urlencode(params)
            url = f"{endpoint}?{query}"

            try:
                req = urllib.request.Request(
                    url, 
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
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
                    committee = row.get("CURR_COMMITTEE", "미지정")
                    committee_counts[committee] += 1

                if len(rows) < pSize:
                    break
                page += 1

            except Exception as e:
                print(f"❌ 요청 실패 (AGE={age}, page={page}): {e}")
                break

    return dict(committee_counts)


# 시각화 및 비율 정리
def plot_committee_distribution(committee_counts, total_count, max_sections=10, threshold=0.03):
    """
    비율이 `threshold` 이하이거나 top-N 초과 항목은 '기타'로 묶어서 막대그래프로 시각화
    """
    labeled_counts = dict(committee_counts)
    committee_sum = sum(labeled_counts.values())
    etc_count = total_count - committee_sum  # 누락 오차

    # 비율 계산
    ratio_items = [(k, v, v / total_count) for k, v in labeled_counts.items()]
    ratio_items.sort(key=lambda x: x[1], reverse=True)

    major_items = []
    etc_total = etc_count
    for i, (k, v, ratio) in enumerate(ratio_items):
        if ratio >= threshold:
            major_items.append((k, v))
        else:
            etc_total += v

    if etc_total > 0:
        major_items.append(("기타/미지정", etc_total))

    labels = [k for k, _ in major_items]
    counts = [v for _, v in major_items]
    sizes = [v / total_count * 100 for v in counts]

    # 출력
    print("\n📊 위원회별 제출 비율 (상위 + 기타 통합):")
    for label, size in zip(labels, sizes):
        print(f"- {label}: {size:.2f}%")

    # 색상 (막대그래프용)
    colors = plt.cm.Paired(range(len(labels)))

    # 막대그래프
    plt.figure(figsize=(12, 8))
    bars = plt.barh(labels, sizes, color=colors)
    plt.xlabel("제출 비율 (%)")
    plt.title("위원회별 법안 제출 비율")
    plt.gca().invert_yaxis()  # 높은 비율이 위로 오게
    plt.grid(axis='x', linestyle='--', alpha=0.7)

    # 비율 텍스트 표시
    for bar, size in zip(bars, sizes):
        plt.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                 f"{size:.1f}%", va='center')

    plt.tight_layout()
    plt.show()



# 실행
if __name__ == "__main__":
    ages = [18, 19, 20]
    total = get_total_submission_count(ages)
    print(f"\n 총 제출건수: {total}건")

    committee_counts = get_committee_submission_counts(ages)
    plot_committee_distribution(committee_counts, total)
