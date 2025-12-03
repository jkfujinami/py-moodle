from pymoodle.client import MoodleClient
import getpass
import logging

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def get_client():
    client = MoodleClient(base_url="https://moodle2.maizuru-ct.ac.jp/moodle/", session_file="session.json")

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
    quiz_id = 83184

    print(f"Fetching details for quiz {quiz_id}...")
    details = client.get_quiz_details(quiz_id)

    if not details:
        print("Could not fetch quiz details.")
        return

    print(f"Title: {details['title']}")
    print(f"Intro: {details['intro'][:50]}...")
    print(f"Can Attempt: {details['can_attempt']}")

    if details['can_attempt'] and details['cmid'] and details['sesskey']:
        print("Starting attempt...")
        attempt_url = client.start_quiz_attempt(details['cmid'], details['sesskey'])

        if attempt_url:
            print(f"Attempt URL: {attempt_url}")
            attempt_data = client.get_quiz_attempt_data(attempt_url)

            if attempt_data:
                print(f"Attempt ID: {attempt_data['attempt_id']}")
                print(f"Questions Found: {len(attempt_data['questions'])}")
                for q in attempt_data['questions']:
                    print(f"  - Q{q['number']} ({q['type']}): {q['text'][:30]}...")
                    if q['subquestions']:
                        print(f"    Subquestions: {len(q['subquestions'])}")

    elif details['attempts']:
        last_attempt = details['attempts'][-1]
        print(f"Last Attempt Grade: {last_attempt['grade']}")

if __name__ == "__main__":
    main()
