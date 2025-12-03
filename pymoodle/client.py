from typing import List, Optional
import logging
from pymoodle.session import MoodleSession
from pymoodle.api import MoodleAPI
from pymoodle.types import Course, Category, Section, FolderDetails, AssignmentDetails, ForumDetails, PageDetails, QuizDetails

logger = logging.getLogger(__name__)

class MoodleClient:
    """
    High-level client for Moodle.
    Acts as a facade for MoodleSession and MoodleAPI.
    """
    def __init__(self, session_file="session.json", base_url: Optional[str] = None):
        self.session = MoodleSession(session_file, base_url)
        self.api = MoodleAPI(self.session)

    def login(self, username, password) -> bool:
        """
        Performs login.
        """
        return self.session.authenticate(username, password)

    def save_session(self):
        """Saves the current session to file."""
        self.session.save_session()

    def load_session(self) -> bool:
        """Loads the session from file."""
        return self.session.load_session()

    def is_logged_in(self) -> bool:
        """Checks if logged in."""
        return self.session.is_logged_in()

    def get_my_courses(self) -> List[Course]:
        return self.api.get_my_courses()

    def get_course_contents(self, course_id: int) -> List[Section]:
        return self.api.get_course_contents(course_id)

    def get_resource_download_url(self, resource_id: int) -> Optional[str]:
        return self.api.get_resource_download_url(resource_id)

    def get_external_url(self, url_id: int) -> Optional[str]:
        return self.api.get_external_url(url_id)

    def get_folder_details(self, folder_id: int) -> Optional[FolderDetails]:
        return self.api.get_folder_details(folder_id)

    def get_assignment_details(self, assign_id: int) -> Optional[AssignmentDetails]:
        return self.api.get_assignment_details(assign_id)

    def get_forum_details(self, forum_id: int) -> Optional[ForumDetails]:
        return self.api.get_forum_details(forum_id)

    def get_page_details(self, page_id: int) -> Optional[PageDetails]:
        return self.api.get_page_details(page_id)

    def get_quiz_details(self, quiz_id: int) -> Optional[QuizDetails]:
        return self.api.get_quiz_details(quiz_id)

    def download_file(self, url: str, save_path: str) -> Optional[str]:
        return self.api.download_file(url, save_path)

    def get_course_categories(self, category_id: Optional[int] = None) -> List[Category]:
        return self.api.get_course_categories(category_id)
