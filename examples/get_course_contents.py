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

    # 動作確認用のコースID (例: 3240)
    course_id = 3240
    print(f"\nFetching contents for course {course_id}...")

    sections = client.get_course_contents(course_id)
    if not sections:
        print("No sections found or error occurred.")
        return

    for section in sections:
        print(f"\nSection: {section['name']} (ID: {section['id']})")
        for mod in section['modules']:
            status = "[x]" if mod['completed'] else "[ ]"
            print(f"  {status} {mod['name']} ({mod['type']})")
            if mod['description']:
                # print(f"      Desc: {mod['description']}")
                pass

if __name__ == "__main__":
    main()
