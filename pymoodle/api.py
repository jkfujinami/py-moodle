from typing import List, Optional
import os
from urllib.parse import urljoin
import logging
from pymoodle.session import MoodleSession
from pymoodle import parsers, utils
from pymoodle.types import Course, Category, Section, FolderDetails, AssignmentDetails, ForumDetails, PageDetails, QuizDetails
from pymoodle.exceptions import MoodleRequestError, MoodleParseError

logger = logging.getLogger(__name__)

class MoodleAPI:
    """
    Provides specific Moodle functionality using MoodleSession.
    """
    def __init__(self, session: MoodleSession):
        self.session = session

    def get_my_courses(self) -> List[Course]:
        logger.info(f"Fetching dashboard: {self.session.base_url}")
        try:
            response = self.session.get(self.session.base_url)
            response.raise_for_status()
            return parsers.parse_my_courses(response.text)
        except (MoodleRequestError, Exception) as e:
            logger.error(f"Error fetching dashboard: {e}")
            return []

    def get_course_contents(self, course_id: int) -> List[Section]:
        url = urljoin(self.session.base_url, f"course/view.php?id={course_id}")
        logger.info(f"Fetching course contents: {url}")
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return parsers.parse_course_contents(response.text)
        except (MoodleRequestError, Exception) as e:
            logger.error(f"Error fetching course contents: {e}")
            return []

    def get_course_categories(self, category_id: Optional[int] = None) -> List[Category]:
        if category_id:
            target_url = urljoin(self.session.base_url, f"course/index.php?categoryid={category_id}")
            logger.info(f"Fetching subcategories from: {target_url}")
        else:
            target_url = self.session.base_url
            logger.info(f"Fetching root categories from dashboard: {target_url}")

        try:
            response = self.session.get(target_url)
            response.raise_for_status()
            return parsers.parse_categories(response.text, is_subcategory=bool(category_id))
        except (MoodleRequestError, Exception) as e:
            logger.error(f"Error fetching categories: {e}")
            return []

    def get_resource_download_url(self, resource_id: int) -> Optional[str]:
        resource_url = urljoin(self.session.base_url, f"mod/resource/view.php?id={resource_id}")
        logger.debug(f"Resolving resource URL: {resource_url}")
        try:
            response = self.session.get(resource_url, allow_redirects=False)
            if response.status_code in (301, 302, 303):
                return response.headers.get('Location')
            return parsers.parse_resource_url(response.text)
        except (MoodleRequestError, Exception) as e:
            logger.error(f"Error resolving resource URL: {e}")
            return None

    def get_external_url(self, url_id: int) -> Optional[str]:
        mod_url = urljoin(self.session.base_url, f"mod/url/view.php?id={url_id}")
        logger.debug(f"Resolving external URL: {mod_url}")
        try:
            response = self.session.get(mod_url, allow_redirects=False)
            if response.status_code in (301, 302, 303):
                return response.headers.get('Location')
            return parsers.parse_external_url(response.text)
        except (MoodleRequestError, Exception) as e:
            logger.error(f"Error resolving external URL: {e}")
            return None

    def get_folder_details(self, folder_id: int) -> Optional[FolderDetails]:
        folder_url = urljoin(self.session.base_url, f"mod/folder/view.php?id={folder_id}")
        logger.info(f"Fetching folder details: {folder_url}")
        try:
            response = self.session.get(folder_url)
            response.raise_for_status()
            return parsers.parse_folder(response.text)
        except (MoodleRequestError, Exception) as e:
            logger.error(f"Error fetching folder details: {e}")
            return None

    def get_assignment_details(self, assign_id: int) -> Optional[AssignmentDetails]:
        assign_url = urljoin(self.session.base_url, f"mod/assign/view.php?id={assign_id}")
        logger.info(f"Fetching assignment details: {assign_url}")
        try:
            response = self.session.get(assign_url)
            response.raise_for_status()
            return parsers.parse_assignment(response.text)
        except (MoodleRequestError, Exception) as e:
            logger.error(f"Error fetching assignment details: {e}")
            return None

    def get_forum_details(self, forum_id: int) -> Optional[ForumDetails]:
        forum_url = urljoin(self.session.base_url, f"mod/forum/view.php?id={forum_id}")
        logger.info(f"Fetching forum details: {forum_url}")
        try:
            response = self.session.get(forum_url)
            response.raise_for_status()
            return parsers.parse_forum(response.text)
        except (MoodleRequestError, Exception) as e:
            logger.error(f"Error fetching forum details: {e}")
            return None

    def get_page_details(self, page_id: int) -> Optional[PageDetails]:
        page_url = urljoin(self.session.base_url, f"mod/page/view.php?id={page_id}")
        logger.info(f"Fetching page details: {page_url}")
        try:
            response = self.session.get(page_url)
            response.raise_for_status()
            return parsers.parse_page(response.text)
        except (MoodleRequestError, Exception) as e:
            logger.error(f"Error fetching page details: {e}")
            return None

    def get_quiz_details(self, quiz_id: int) -> Optional[QuizDetails]:
        quiz_url = urljoin(self.session.base_url, f"mod/quiz/view.php?id={quiz_id}")
        logger.info(f"Fetching quiz details: {quiz_url}")
        try:
            response = self.session.get(quiz_url)
            response.raise_for_status()
            return parsers.parse_quiz(response.text)
        except (MoodleRequestError, Exception) as e:
            logger.error(f"Error fetching quiz details: {e}")
            return None

    def download_file(self, url: str, save_path: str) -> Optional[str]:
        """
        Downloads a file and saves it to the specified path.
        """
        logger.info(f"Downloading file from: {url}")
        try:
            response = self.session.get(url, stream=True)
            response.raise_for_status()

            filename = utils.extract_filename_from_response(response, url)

            # save_path logic
            if os.path.isdir(save_path):
                file_path = os.path.join(save_path, filename)
            else:
                file_path = save_path

            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            logger.info(f"File saved to: {file_path}")
            return file_path

        except (MoodleRequestError, Exception) as e:
            logger.error(f"Error downloading file: {e}")
            return None
