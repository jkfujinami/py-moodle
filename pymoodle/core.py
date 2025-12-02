import requests
import json
import os
import logging
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from typing import Optional

logger = logging.getLogger(__name__)

class BaseMoodleClient:
    _DEFAULT_BASE_URL = "https://moodle2.maizuru-ct.ac.jp/moodle/"

    def __init__(self, session_file="session.json", base_url: Optional[str] = None):
        self.session = requests.Session()
        self.session_file = session_file

        if base_url:
            # 末尾にスラッシュがない場合は追加
            if not base_url.endswith('/'):
                base_url += '/'
            self.BASE_URL = base_url
        else:
            self.BASE_URL = self._DEFAULT_BASE_URL

        self.LOGIN_URL = urljoin(self.BASE_URL, "login/index.php")

        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,application/apng,*/*;q=0.8",
            "Accept-Language": "ja,en-US;q=0.9,en;q=0.8"
        })

    def get(self, url, **kwargs):
        return self.session.get(url, **kwargs)

    def post(self, url, **kwargs):
        return self.session.post(url, **kwargs)

    def login(self, username, password) -> bool:
        logger.info(f"Fetching login page: {self.LOGIN_URL}")
        try:
            response = self.session.get(self.LOGIN_URL)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Error fetching login page: {e}")
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
            logger.debug(f"Login token found: {token}")

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": self.LOGIN_URL,
            "Origin": "https://moodle2.maizuru-ct.ac.jp"
        }

        logger.info("Submitting login form...")
        try:
            response = self.session.post(self.LOGIN_URL, data=payload, headers=headers)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Login request failed: {e}")
            return False

        if "login/index.php" not in response.url:
            logger.info("Login successful!")
            self.save_session()
            return True
        else:
            logger.warning("Login failed.")
            return False

    def save_session(self):
        cookies = self.session.cookies.get_dict()
        with open(self.session_file, 'w') as f:
            json.dump(cookies, f)
        logger.info(f"Session saved to {self.session_file}")

    def load_session(self) -> bool:
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file, 'r') as f:
                    cookies = json.load(f)
                self.session.cookies.update(cookies)
                logger.info(f"Session loaded from {self.session_file}")
                return True
            except json.JSONDecodeError:
                logger.error("Failed to decode session file.")
        return False

    def is_logged_in(self) -> bool:
        try:
            response = self.session.get(self.BASE_URL, allow_redirects=False)
            if response.status_code == 200:
                if "login/index.php" in response.url:
                    return False
                return True
            elif response.status_code in (301, 302, 303):
                location = response.headers.get('Location', '')
                if "login/index.php" in location:
                    return False
            return True
        except requests.RequestException:
            return False
