import requests
import json
import os
import logging
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any

from pymoodle.exceptions import MoodleLoginError, MoodleRequestError

logger = logging.getLogger(__name__)

class MoodleSession:
    """
    Handles HTTP session, authentication, and cookie management for Moodle.
    """

    def __init__(self, base_url: Optional[str], session_file: str = "session.json"):
        self.session = requests.Session()
        self.session_file = session_file
        if not base_url.endswith('/'):
            base_url += '/'
        self.base_url = base_url
        self.login_url = urljoin(self.base_url, "login/index.php")

        # Default headers
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,application/apng,*/*;q=0.8",
            "Accept-Language": "ja,en-US;q=0.9,en;q=0.8"
        })

    def get(self, url: str, **kwargs) -> requests.Response:
        try:
            return self.session.get(url, **kwargs)
        except requests.RequestException as e:
            raise MoodleRequestError(f"GET request failed: {e}") from e

    def post(self, url: str, **kwargs) -> requests.Response:
        try:
            return self.session.post(url, **kwargs)
        except requests.RequestException as e:
            raise MoodleRequestError(f"POST request failed: {e}") from e

    def authenticate(self, username, password) -> bool:
        """
        Performs the login flow.
        """
        logger.info(f"Fetching login page: {self.login_url}")
        try:
            response = self.get(self.login_url)
            response.raise_for_status()
        except (MoodleRequestError, requests.HTTPError) as e:
            logger.error(f"Error fetching login page: {e}")
            raise MoodleLoginError(f"Could not access login page: {e}")

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
        else:
            logger.warning("No login token found. Trying without it.")

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": self.login_url,
            "Origin": self.base_url.rstrip('/') # Approximate origin
        }

        logger.info("Submitting login form...")
        try:
            response = self.post(self.login_url, data=payload, headers=headers)
            response.raise_for_status()
        except (MoodleRequestError, requests.HTTPError) as e:
            logger.error(f"Login request failed: {e}")
            raise MoodleLoginError(f"Login request failed: {e}")

        # Check login success
        if "login/index.php" not in response.url:
            logger.info("Login successful!")
            self.save_session()
            return True
        else:
            # Check for specific error messages
            if "Invalid login" in response.text or "ログインが無効" in response.text:
                msg = "Login failed: Invalid credentials."
            else:
                msg = "Login failed: Unknown reason (still on login page)."

            logger.warning(msg)
            return False

    def save_session(self):
        """Saves current session cookies to file."""
        cookies = self.session.cookies.get_dict()
        try:
            with open(self.session_file, 'w') as f:
                json.dump(cookies, f)
            logger.info(f"Session saved to {self.session_file}")
        except IOError as e:
            logger.error(f"Failed to save session file: {e}")

    def load_session(self) -> bool:
        """Loads session cookies from file."""
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file, 'r') as f:
                    cookies = json.load(f)
                print(cookies)
                self.session.cookies.update(cookies)
                logger.info(f"Session loaded from {self.session_file}")
                return True
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Failed to load session file: {e}")
        return False

    def is_logged_in(self) -> bool:
        """
        Checks if the current session is valid.
        """
        try:
            response = self.session.get(self.base_url, allow_redirects=False)
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
