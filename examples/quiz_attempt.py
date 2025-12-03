from pymoodle.client import MoodleClient
import getpass
import logging

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def get_client():
    client = MoodleClient(base_url="https://moodle2.example.jp/moodle/", session_file="session.json")

    if client.load_session() and client.is_logged_in():
        print("Session is valid. Logged in.")
        return client
    else:
        print("Please login.")
        username = input("Username: ")
        password = getpass.getpass("Password: ")
        if client.login(username, password):
            print("Login successful.")
            return client
        else:
            print("Login failed.")
            return None

def main():
    client = get_client()
    if not client:
        return

    # テスト用のクイズID (適宜変更してください)
    quiz_id = 12345

    print(f"Fetching details for quiz {quiz_id}...")
    details = client.get_quiz_details(quiz_id)

    if not details:
        print("Could not fetch quiz details.")
        return

    print(f"Title: {details.title}")
    print(f"Intro: {details.intro[:50]}...")
    print(f"Can Attempt: {details.can_attempt}")

    if details.can_attempt and details.cmid and details.sesskey:
        print("Starting attempt...")
        attempt_url = client.start_quiz_attempt(details.cmid, details.sesskey)

        if attempt_url:
            print(f"Attempt URL: {attempt_url}")
            attempt_data = client.get_quiz_attempt_data(attempt_url)

            if attempt_data:
                print(f"\n=== Quiz Attempt: {attempt_data.attempt_id} ===")
                for q in attempt_data.questions:
                    print(f"\n[Q{q.number}] Type: {q.type}")
                    print("-" * 20 + " Question Text " + "-" * 20)
                    print(q.text)
                    print("-" * 55)

                    if q.subquestions:
                        print("  Subquestions / Blanks:")
                        for i, sub in enumerate(q.subquestions, 1):
                            # sub is a dict here
                            label = sub.get('label', '').strip()
                            if not label:
                                label = f'Blank {i}'
                            stype = sub.get('type', 'unknown')
                            name = sub.get('name', 'unknown')

                            print(f"    ({i}) {label} [{stype}] (name: {name})")

                            options = sub.get('options')
                            if options:
                                for opt in options:
                                    val = opt.get('value')
                                    text = opt.get('text')
                                    print(f"        - {text} (value: {val})")
                    print("=" * 60)
                """
                # 回答の作成（デモ用）
                # 注意: 実際のname属性（q566739:1_sub1_answerなど）は実行ごとに変わる可能性があります。
                # ここでは、取得したattempt_dataから動的にnameを取得して回答を構築します。

                answers = {}

                # Q1 分離法
                # (1) 再結晶 (value: 1)
                # (2) 分留 (value: 4)
                # (3) クロマトグラフィー (value: 2) (Wait, check options)
                #     Blank 3: 再結晶(0), ろ過(1), 昇華法(2), クロマトグラフィー(3), 分留(4), 抽出(5) -> 3
                # (4) ろ過 (value: 3)
                # (5) 抽出 (value: 5)

                q1 = attempt_data.questions[0]
                if q1.subquestions:
                    answers[q1.subquestions[0]['name']] = '1' # 再結晶
                    answers[q1.subquestions[1]['name']] = '4' # 分留
                    answers[q1.subquestions[2]['name']] = '3' # クロマトグラフィー (Based on options list for Blank 3)
                    answers[q1.subquestions[3]['name']] = '3' # ろ過 (Based on options list for Blank 4)
                    answers[q1.subquestions[4]['name']] = '5' # 抽出 (Based on options list for Blank 5)

                # Q2 単体 or 元素
                # (1) 酸素(単体) -> 1
                # (2) 酸素(元素) -> 0
                # (3) 酸素(単体) -> 1
                # (4) 酸素(単体) -> 0 (Wait, check options for Blank 4: 単体(0), 元素(1)) -> 0
                # (5) 酸素(元素) -> 1 (Wait, check options for Blank 5: 単体(0), 元素(1)) -> 1
                # (6) 酸素(単体) -> 0 (Wait, check options for Blank 6: 単体(0), 元素(1)) -> 0

                q2 = attempt_data.questions[1]
                if q2.subquestions:
                    answers[q2.subquestions[0]['name']] = '1' # 単体 (元素(0), 単体(1))
                    answers[q2.subquestions[1]['name']] = '0' # 元素 (元素(0), 単体(1))
                    answers[q2.subquestions[2]['name']] = '1' # 単体 (元素(0), 単体(1))
                    answers[q2.subquestions[3]['name']] = '0' # 単体 (単体(0), 元素(1))
                    answers[q2.subquestions[4]['name']] = '1' # 元素 (単体(0), 元素(1))
                    answers[q2.subquestions[5]['name']] = '0' # 単体 (単体(0), 元素(1))

                # Q3 同素体 (○ or ×)
                # (1) Ne, Ar -> × (0) (×(0), ○(1))
                # (2) CO, CO2 -> × (1) (○(0), ×(1))
                # (3) 黄リン, 赤リン -> ○ (0) (○(0), ×(1))
                # (4) 氷, 水蒸気 -> × (0) (×(0), ○(1))
                # (5) 斜方硫黄, 単斜硫黄 -> ○ (1) (×(0), ○(1))
                # (6) Pb, Zn -> × (1) (○(0), ×(1))

                q3 = attempt_data.questions[2]
                if q3.subquestions:
                    answers[q3.subquestions[0]['name']] = '0' # ×
                    answers[q3.subquestions[1]['name']] = '1' # ×
                    answers[q3.subquestions[2]['name']] = '0' # ○
                    answers[q3.subquestions[3]['name']] = '0' # ×
                    answers[q3.subquestions[4]['name']] = '1' # ○
                    answers[q3.subquestions[5]['name']] = '1' # ×

                # Q4 原子 (○ or ×)
                # (1) 半径100-1000倍 -> × (10000倍くらい) -> × (1) (○(0), ×(1))
                # (2) 陽子+電子=質量数 -> × (陽子+中性子) -> × (0) (×(0), ○(1))
                # (3) 中性子はすべて -> × (H-1はなし) -> × (0) (×(0), ○(1))
                # (4) 陽子数等しい=同元素 -> ○ (1) (×(0), ○(1))
                # (5) 質量ほぼ等しい -> × (電子は軽い) -> × (1) (○(0), ×(1))
                # (6) 同位体ないものもある -> ○ (1) (×(0), ○(1))

                q4 = attempt_data.questions[3]
                if q4.subquestions:
                    answers[q4.subquestions[0]['name']] = '1' # ×
                    answers[q4.subquestions[1]['name']] = '0' # ×
                    answers[q4.subquestions[2]['name']] = '0' # ×
                    answers[q4.subquestions[3]['name']] = '1' # ○
                    answers[q4.subquestions[4]['name']] = '1' # ×
                    answers[q4.subquestions[5]['name']] = '1' # ○

                # Q5 酸素同位体
                # (1) 同位体
                # (2) 18O: 陽子8, 中性子10, 電子8
                # (3) 組み合わせ: 16-16, 17-17, 18-18, 16-17, 16-18, 17-18 -> 6種類

                q5 = attempt_data.questions[4]
                if q5.subquestions:
                    answers[q5.subquestions[0]['name']] = '同位体'
                    answers[q5.subquestions[1]['name']] = '8'
                    answers[q5.subquestions[2]['name']] = '10'
                    answers[q5.subquestions[3]['name']] = '8'
                    answers[q5.subquestions[4]['name']] = '6'

                print("\nSubmitting answers...")
                # finish_attempt=True で「テストを終了する」を送信
                result_url = client.submit_quiz_answers(attempt_data, answers, finish_attempt=True)
                if result_url:
                    print(f"Submission successful! Next URL: {result_url}")

                    # 最終的な提出（Submit all and finish）
                    # cmidはdetailsから取得できます
                    if details.cmid:
                        print("\nFinishing attempt (Submit all and finish)...")
                        review_url = client.finish_quiz_attempt(attempt_data.attempt_id, attempt_data.sesskey, str(details.cmid))
                        if review_url:
                            print(f"Attempt finished! Review URL: {review_url}")
                        else:
                            print("Failed to finish attempt.")
                else:
                    print("Submission failed.")
                """
    elif details.attempts:
        last_attempt = details.attempts[-1]
        print(f"Last Attempt Grade: {last_attempt.grade}")

if __name__ == "__main__":
    main()
