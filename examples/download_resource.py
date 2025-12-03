from pymoodle.client import MoodleClient
import getpass
import logging
import os

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

    # テスト用のリソースID (適宜変更してください)
    resource_id = 12345

    print(f"Resolving download URL for resource {resource_id}...")
    download_url = client.get_resource_download_url(resource_id)

    if download_url:
        print(f"Download URL: {download_url}")

        download_dir = "downloads"
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

        print(f"Downloading to {download_dir}...")
        saved_path = client.download_file(download_url, download_dir)
        if saved_path:
            print(f"Saved to: {saved_path}")
    else:
        print("Could not resolve download URL.")

if __name__ == "__main__":
    main()
