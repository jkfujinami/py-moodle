from typing import List, Optional
import os
from urllib.parse import urljoin
import requests
import logging
from pymoodle.core import BaseMoodleClient
from pymoodle import parsers
from pymoodle.types import Course, Category, Section, FolderDetails, AssignmentDetails, ForumDetails, PageDetails, QuizDetails

logger = logging.getLogger(__name__)

class MoodleService:
    def __init__(self, client: BaseMoodleClient):
        self.client = client

    def get_my_courses(self) -> List[Course]:
        logger.info(f"Fetching dashboard: {self.client.BASE_URL}")
        try:
            response = self.client.get(self.client.BASE_URL)
            response.raise_for_status()
            return parsers.parse_my_courses(response.text)
        except requests.RequestException as e:
            logger.error(f"Error fetching dashboard: {e}")
            return []

    def get_course_contents(self, course_id: int) -> List[Section]:
        url = urljoin(self.client.BASE_URL, f"course/view.php?id={course_id}")
        logger.info(f"Fetching course contents: {url}")
        try:
            response = self.client.get(url)
            response.raise_for_status()
            return parsers.parse_course_contents(response.text)
        except requests.RequestException as e:
            logger.error(f"Error fetching course contents: {e}")
            return []

    def get_course_categories(self, category_id: Optional[int] = None) -> List[Category]:
        if category_id:
            target_url = urljoin(self.client.BASE_URL, f"course/index.php?categoryid={category_id}")
            logger.info(f"Fetching subcategories from: {target_url}")
        else:
            target_url = self.client.BASE_URL
            logger.info(f"Fetching root categories from dashboard: {target_url}")

        try:
            response = self.client.get(target_url)
            response.raise_for_status()
            return parsers.parse_categories(response.text, is_subcategory=bool(category_id))
        except requests.RequestException as e:
            logger.error(f"Error fetching categories: {e}")
            return []

    def get_resource_download_url(self, resource_id: int) -> Optional[str]:
        resource_url = urljoin(self.client.BASE_URL, f"mod/resource/view.php?id={resource_id}")
        logger.debug(f"Resolving resource URL: {resource_url}")
        try:
            response = self.client.get(resource_url, allow_redirects=False)
            if response.status_code in (301, 302, 303):
                return response.headers.get('Location')
            return parsers.parse_resource_url(response.text)
        except requests.RequestException as e:
            logger.error(f"Error resolving resource URL: {e}")
            return None

    def get_external_url(self, url_id: int) -> Optional[str]:
        mod_url = urljoin(self.client.BASE_URL, f"mod/url/view.php?id={url_id}")
        logger.debug(f"Resolving external URL: {mod_url}")
        try:
            response = self.client.get(mod_url, allow_redirects=False)
            if response.status_code in (301, 302, 303):
                return response.headers.get('Location')
            return parsers.parse_external_url(response.text)
        except requests.RequestException as e:
            logger.error(f"Error resolving external URL: {e}")
            return None

    def get_folder_details(self, folder_id: int) -> Optional[FolderDetails]:
        folder_url = urljoin(self.client.BASE_URL, f"mod/folder/view.php?id={folder_id}")
        logger.info(f"Fetching folder details: {folder_url}")
        try:
            response = self.client.get(folder_url)
            response.raise_for_status()
            return parsers.parse_folder(response.text)
        except requests.RequestException as e:
            logger.error(f"Error fetching folder details: {e}")
            return None

    def get_assignment_details(self, assign_id: int) -> Optional[AssignmentDetails]:
        assign_url = urljoin(self.client.BASE_URL, f"mod/assign/view.php?id={assign_id}")
        logger.info(f"Fetching assignment details: {assign_url}")
        try:
            response = self.client.get(assign_url)
            response.raise_for_status()
            return parsers.parse_assignment(response.text)
        except requests.RequestException as e:
            logger.error(f"Error fetching assignment details: {e}")
            return None

    def get_forum_details(self, forum_id: int) -> Optional[ForumDetails]:
        forum_url = urljoin(self.client.BASE_URL, f"mod/forum/view.php?id={forum_id}")
        logger.info(f"Fetching forum details: {forum_url}")
        try:
            response = self.client.get(forum_url)
            response.raise_for_status()
            return parsers.parse_forum(response.text)
        except requests.RequestException as e:
            logger.error(f"Error fetching forum details: {e}")
            return None

    def get_page_details(self, page_id: int) -> Optional[PageDetails]:
        page_url = urljoin(self.client.BASE_URL, f"mod/page/view.php?id={page_id}")
        logger.info(f"Fetching page details: {page_url}")
        try:
            response = self.client.get(page_url)
            response.raise_for_status()
            return parsers.parse_page(response.text)
        except requests.RequestException as e:
            logger.error(f"Error fetching page details: {e}")
            return None

    def get_quiz_details(self, quiz_id: int) -> Optional[QuizDetails]:
        quiz_url = urljoin(self.client.BASE_URL, f"mod/quiz/view.php?id={quiz_id}")
        logger.info(f"Fetching quiz details: {quiz_url}")
        try:
            response = self.client.get(quiz_url)
            response.raise_for_status()
            return parsers.parse_quiz(response.text)
        except requests.RequestException as e:
            logger.error(f"Error fetching quiz details: {e}")
            return None

    def download_file(self, url: str, save_path: str) -> Optional[str]:
        """
        ファイルをダウンロードして保存する。
        save_path がディレクトリの場合は、ファイル名を自動判別して保存する。
        """
        logger.info(f"Downloading file from: {url}")
        try:
            response = self.client.get(url, stream=True)
            response.raise_for_status()

            filename = ""
            # Content-Dispositionヘッダーからファイル名を取得
            if "Content-Disposition" in response.headers:
                import re
                # filename="example.pdf" または filename*=UTF-8''example.pdf などを解析
                # 簡易的な実装
                cd = response.headers["Content-Disposition"]
                matches = re.findall(r'filename\*=UTF-8\'\'(.+)|filename="([^"]+)"|filename=([^;]+)', cd)
                if matches:
                    # マッチしたグループのどれかを採用
                    for match in matches[0]:
                        if match:
                            from urllib.parse import unquote
                            filename = unquote(match)
                            break

            # ヘッダーになければURLから取得
            if not filename:
                from urllib.parse import urlparse, unquote
                parsed = urlparse(url)
                filename = unquote(os.path.basename(parsed.path))

            if not filename:
                filename = "downloaded_file"

            # save_pathの判定
            if os.path.isdir(save_path):
                file_path = os.path.join(save_path, filename)
            else:
                file_path = save_path

            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            logger.info(f"File saved to: {file_path}")
            return file_path

        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            return None
