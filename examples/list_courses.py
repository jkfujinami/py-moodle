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

    print("\nFetching my courses...")
    courses = client.get_my_courses()
    print(f"Found {len(courses)} courses:")
    for course in courses:
        print(f"- [{course['id']}] {course['name']}")

    print("\nFetching root course categories...")
    categories = client.get_course_categories()
    print(f"Found {len(categories)} root categories:")
    for cat in categories:
        print(f"- [{cat['id']}] {cat['name']} (Courses: {cat['course_count']})")

if __name__ == "__main__":
    main()
