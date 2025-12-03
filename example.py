from pymoodle.client import MoodleClient
import getpass
import logging

# ログ設定: INFOレベル以上を表示
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def main():
    client = MoodleClient(base_url="https://moodle2.maizuru-ct.ac.jp/moodle/", session_file="moodle_session.json")

    # セッションの読み込みを試みる
    if client.load_session():
        print("Checking session validity...")
        if client.is_logged_in():
            print("Session is valid. Logged in.")
        else:
            print("Session expired or invalid.")
            perform_login(client)
    else:
        perform_login(client)

    # ログイン後の動作確認
    if client.is_logged_in():
        print("\nFetching my courses...")
        courses = client.get_my_courses()
        print(f"Found {len(courses)} courses:")
        for course in courses:
            print(f"- [{course.id}] {course.name}")
            # print(f"  URL: {course.url}")

        print("\nFetching root course categories...")
        categories = client.get_course_categories()
        print(f"Found {len(categories)} root categories:")
        for cat in categories:
            print(f"- [{cat.id}] {cat.name} (Courses: {cat.course_count})")

        # サブカテゴリ取得のデモ（最初のカテゴリを使用）
        if categories and categories[0].has_children:
            first_cat_id = categories[0].id
            print(f"\nFetching subcategories for category {first_cat_id}...")
            sub_cats = client.get_course_categories(category_id=first_cat_id)
            for sub in sub_cats:
                 print(f"  - [{sub.id}] {sub.name}")

        # コースコンテンツ取得のデモ（最初のコースを使用）
        if courses:
            first_course_id = 2911
            print(f"\nFetching contents for course {first_course_id}...")
            sections = client.get_course_contents(first_course_id)
            for section in sections:
                print(f"\nSection: {section.name} (ID: {section.id})")
                for mod in section.modules:
                    status = "[x]" if mod.completed else "[ ]"
                    print(f"  {status} {mod.name} ({mod.type})")
                    if mod.description:
                         # print(f"      Desc: {mod.description}")
                         pass

                    # デモ: URL解決 (最初の数件のみ)
                    if mod.type == 'resource' and mod.id:
                        download_url = client.get_resource_download_url(mod.id)
                        # print(f"      -> Download: {download_url}")
                        pass
                    elif mod.type == 'url' and mod.id:
                        # ext_url = client.get_external_url(mod.id)
                        # print(f"      -> External: {ext_url}")
                        pass
                    elif mod.type == "assign" and mod.id:
                        # details = client.get_assignment_details(mod.id)
                        # if details:
                        #     print(f"      -> Status: {details.submission_status}")
                        #     print(f"      -> Due: {details.due_date}")
                        #     if details.attachments:
                        #         print(f"      -> Attachments: {[f.filename for f in details.attachments]}")
                        pass
                    elif mod.type == "folder" and mod.id:
                        details = client.get_folder_details(mod.id)
                        if details:
                            print(f"      -> Files: {[f.filename for f in details.files]}")
                            # print(f"      -> Download All: {details.download_all_url}")

                            # フォルダ内のファイルをダウンロードするデモ
                            import os
                            download_dir = "downloads"
                            if not os.path.exists(download_dir):
                                os.makedirs(download_dir)

                            for file_item in details.files:
                                print(f"        Downloading {file_item.filename}...")
                                saved_path = client.download_file(file_item.url, download_dir)
                                if saved_path:
                                    print(f"        Saved to: {saved_path}")
                    elif mod.type == "forum" and mod.id:
                        # details = client.get_forum_details(mod.id)
                        # if details:
                        #     print(f"      -> Intro: {details.intro[:50]}...")
                        pass
                    elif mod.type == "page" and mod.id:
                        details = client.get_page_details(mod.id)
                        if details:
                            print(f"      -> Title: {details.title}")
                            print(f"      -> Last Modified: {details.last_modified}")
                            # コンテンツは長いので省略表示
                            print(f"      -> Content: {details.content[:100]}...")
                    elif mod.type == "quiz" and mod.id:
                        details = client.get_quiz_details(mod.id)
                        print(details)
                        """
                        if details:
                            print(f"      -> Intro: {details.intro[:50]}...")
                            print(f"      -> Can Attempt: {details.can_attempt}")

                            if details.can_attempt and details.cmid and details.sesskey:
                                print("      -> Starting attempt...")
                                attempt_url = client.start_quiz_attempt(details.cmid, details.sesskey)
                                if attempt_url:
                                    print(f"      -> Attempt URL: {attempt_url}")
                                    attempt_data = client.get_quiz_attempt_data(attempt_url)
                                    if attempt_data:
                                        print(f"      -> Attempt ID: {attempt_data.attempt_id}")
                                        print(f"      -> Questions Found: {len(attempt_data.questions)}")
                                        for q in attempt_data.questions:
                                            print(f"         - Q{q.number} ({q.type}): {q.text[:30]}...")
                                            if q.subquestions:
                                                print(f"           Subquestions: {len(q.subquestions)}")
                                                # for sub in q.subquestions:
                                                #    print(f"             - {sub.label} ({sub.type})")

                            elif details.attempts:
                                last_attempt = details.attempts[-1]
                                print(f"      -> Last Attempt Grade: {last_attempt.grade}")"""
    else:
        print("Failed to login.")

def perform_login(client):
    print("Please login.")
    username = input("Username: ")
    password = getpass.getpass("Password: ")

    if client.login(username, password):
        print("Login process finished successfully.")
    else:
        print("Login process failed.")

if __name__ == "__main__":
    main()
