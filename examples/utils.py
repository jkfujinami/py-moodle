from pymoodle.client import MoodleClient
import getpass
import logging
import os

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def get_client():
    # 親ディレクトリのsession.jsonを参照するように調整
    session_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "moodle_session.json")
    client = MoodleClient(base_url="https://moodle2.maizuru-ct.ac.jp/moodle/", session_file=session_file)

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
