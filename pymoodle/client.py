import requests
import json
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import List, Optional
from pymoodle.core import BaseMoodleClient
from pymoodle.services import MoodleService
from pymoodle.types import Course, Category, Section, FolderDetails, AssignmentDetails, ForumDetails, PageDetails, QuizDetails

class MoodleClient(BaseMoodleClient):
    """
    ユーザー向けの高レベルクライアント。
    BaseMoodleClientを継承し、MoodleServiceの機能をメソッドとして公開する。
    """
    BASE_URL = "https://moodle2.maizuru-ct.ac.jp/moodle/"
    LOGIN_URL = urljoin(BASE_URL, "login/index.php")

    def __init__(self, session_file="session.json", base_url: Optional[str] = None):
        super().__init__(session_file, base_url)
        self.service = MoodleService(self)
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "ja,en-US;q=0.9,en;q=0.8"
        })

    def login(self, username, password) -> bool:
        """
        ログイン処理を行う。
        成功すればTrueを返し、セッションを保存する。
        """
        # 1. ログインページにアクセスして logintoken を取得
        print(f"Fetching login page: {self.LOGIN_URL}")
        try:
            response = self.session.get(self.LOGIN_URL)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching login page: {e}")
            return False

        soup = BeautifulSoup(response.text, 'html.parser')
        login_token_input = soup.find('input', {'name': 'logintoken'})

        payload = {
            'username': username,
            'password': password,
        }

        if login_token_input:
            token = login_token_input.get('value')
            payload['logintoken'] = token
            print(f"Login token found: {token}")
        else:
            print("Warning: No login token found. Trying without it.")

        # 2. POST送信
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": self.LOGIN_URL,
            "Origin": "https://moodle2.maizuru-ct.ac.jp"
        }

        print("Submitting login form...")
        try:
            response = self.session.post(self.LOGIN_URL, data=payload, headers=headers)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Login request failed: {e}")
            return False

        # ログイン成功判定
        # URLがホーム画面などの内部ページであれば成功とみなす
        # 失敗時は通常 login/index.php に留まる
        if "login/index.php" not in response.url:
            print("Login successful!")
            self.save_session()
            return True
        else:
            # エラーメッセージの確認（簡易）
            if "Invalid login" in response.text or "ログインが無効" in response.text:
                print("Login failed: Invalid credentials.")
            else:
                print("Login failed: Unknown reason (still on login page).")
            return False

    def save_session(self):
        """現在のセッションCookieをJSONファイルに保存"""
        cookies = self.session.cookies.get_dict()
        with open(self.session_file, 'w') as f:
            json.dump(cookies, f)
        print(f"Session saved to {self.session_file}")

    def load_session(self) -> bool:
        """JSONファイルからセッションCookieを読み込む"""
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file, 'r') as f:
                    cookies = json.load(f)
                self.session.cookies.update(cookies)
                print(f"Session loaded from {self.session_file}")
                return True
            except json.JSONDecodeError:
                print("Failed to decode session file.")
        return False

    def is_logged_in(self) -> bool:
        """
        現在ログイン済みか確認する。
        ホームにアクセスしてログインページにリダイレクトされなければOK。
        """
        try:
            response = self.session.get(self.BASE_URL, allow_redirects=False)
            # Moodleは未ログインでホームに行くとログイン画面へ303リダイレクトすることが多い
            if response.status_code == 200:
                # 念のためログインフォームがないか確認
                if "login/index.php" in response.url:
                    return False
                return True
            elif response.status_code in (301, 302, 303):
                location = response.headers.get('Location', '')
                if "login/index.php" in location:
                    return False
            return True # その他の挙動は一旦ログイン済みとみなす（要調整）
        except requests.RequestException:
            return False

    def get_my_courses(self) -> List[Course]:
        return self.service.get_my_courses()

    def get_course_contents(self, course_id: int) -> List[Section]:
        return self.service.get_course_contents(course_id)

    def get_resource_download_url(self, resource_id: int) -> Optional[str]:
        return self.service.get_resource_download_url(resource_id)

    def get_external_url(self, url_id: int) -> Optional[str]:
        return self.service.get_external_url(url_id)

    def get_folder_details(self, folder_id: int) -> Optional[FolderDetails]:
        return self.service.get_folder_details(folder_id)

    def get_assignment_details(self, assign_id: int) -> Optional[AssignmentDetails]:
        return self.service.get_assignment_details(assign_id)

    def get_forum_details(self, forum_id: int) -> Optional[ForumDetails]:
        return self.service.get_forum_details(forum_id)

    def get_page_details(self, page_id: int) -> Optional[PageDetails]:
        return self.service.get_page_details(page_id)

    def get_quiz_details(self, quiz_id: int) -> Optional[QuizDetails]:
        return self.service.get_quiz_details(quiz_id)

    def download_file(self, url: str, save_path: str) -> Optional[str]:
        return self.service.download_file(url, save_path)

    def get_course_categories(self, category_id: Optional[int] = None) -> List[Category]:
        """
        コースカテゴリ一覧を取得する。
        category_idを指定すると、そのカテゴリ内のサブカテゴリを取得する。
        戻り値: カテゴリ情報の辞書のリスト
        """
        from urllib.parse import urljoin

        if category_id:
            target_url = urljoin(self.BASE_URL, f"course/index.php?categoryid={category_id}")
            print(f"Fetching subcategories from: {target_url}")
        else:
            target_url = self.BASE_URL
            print(f"Fetching root categories from dashboard: {target_url}")

        try:
            response = self.session.get(target_url)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching categories: {e}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        categories: List[Category] = []

        # カテゴリ要素を探す
        # category_id指定時は .subcategories 内の .category を探すのが確実
        if category_id:
            container = soup.select_one('.subcategories')
            if container:
                category_items = container.select('.category')
            else:
                # コンテナが見つからない場合は全体から探す（フォールバック）
                category_items = soup.select('.category')
        else:
            category_items = soup.select('.category')

        for item in category_items:
            cat_id = item.get('data-categoryid')

            name_tag = item.select_one('.categoryname a')
            if not name_tag:
                continue

            name = name_tag.get_text(strip=True)
            url = name_tag['href']

            # コース数 (Optional)
            count_span = item.select_one('.numberofcourse')
            course_count = 0
            if count_span:
                import re
                match = re.search(r'\((\d+)\)', count_span.get_text())
                if match:
                    course_count = int(match.group(1))

            categories.append({
                "id": int(cat_id) if cat_id else None,
                "name": name,
                "url": url,
                "course_count": course_count,
                "has_children": "with_children" in item.get("class", [])
            })

        return categories
