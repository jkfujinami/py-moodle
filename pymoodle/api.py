from typing import List, Optional
import os
from urllib.parse import urljoin
import logging
from pymoodle.session import MoodleSession
from pymoodle import parsers, utils
from pymoodle.types import Course, Category, Section, FolderDetails, AssignmentDetails, ForumDetails, PageDetails, QuizDetails, QuizAttemptData
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

    def start_quiz_attempt(self, cmid: int, sesskey: str) -> Optional[str]:
        """
        Starts a new quiz attempt.
        Returns the URL of the attempt page if successful (e.g., .../mod/quiz/attempt.php?attempt=...).
        """
        url = urljoin(self.session.base_url, "mod/quiz/startattempt.php")
        payload = {
            "cmid": cmid,
            "sesskey": sesskey
        }
        logger.info(f"Starting quiz attempt for cmid={cmid}")
        try:
            # Moodle usually redirects to attempt.php after POST
            response = self.session.post(url, data=payload)
            response.raise_for_status()

            if "attempt.php" in response.url:
                logger.info(f"Quiz attempt started. Redirected to: {response.url}")
                return response.url
            elif "view.php" in response.url:
                 # Sometimes it redirects back to view if failed or confirmation needed (though confirmation usually is a form)
                 logger.warning("Redirected back to quiz view page. Attempt might not have started.")
                 return None
            else:
                logger.info(f"Request finished. Current URL: {response.url}")
                return response.url

        except (MoodleRequestError, Exception) as e:
            logger.error(f"Error starting quiz attempt: {e}")
            return None

    def get_quiz_attempt_data(self, attempt_url: str) -> Optional[QuizAttemptData]:
        """
        Fetches the quiz attempt page and parses the questions.
        """
        logger.info(f"Fetching quiz attempt data from: {attempt_url}")
        try:
            response = self.session.get(attempt_url)
            response.raise_for_status()
            return parsers.parse_quiz_attempt(response.text)
        except (MoodleRequestError, Exception) as e:
            logger.error(f"Error fetching quiz attempt data: {e}")
            return None

    def submit_quiz_answers(self, attempt_data: QuizAttemptData, answers: Dict[str, str], finish_attempt: bool = False) -> Optional[str]:
        """
        Submits quiz answers.

        :param attempt_data: The parsed data from the attempt page.
        :param answers: A dictionary mapping input names (e.g., 'q123:1_sub1_answer') to values.
        :param finish_attempt: If True, submits 'Finish attempt' (this usually leads to summary page).
                               If False, just saves (Next page).
        :return: The URL of the next page (e.g., summary or next question page) or None on failure.
        """
        url = urljoin(self.session.base_url, "mod/quiz/processattempt.php")

        # Basic payload required by Moodle
        payload = {
            'attempt': attempt_data.attempt_id,
            'sesskey': attempt_data.sesskey,
            'slots': attempt_data.slots,
            'thispage': '0', # Assuming single page or first page for now. Ideally should be parsed.
            'nextpage': '-1', # -1 usually means finish or next.
            'timeup': '0',
            'scrollpos': '',
        }

        # Add user answers
        payload.update(answers)

        # Add sequence checks and flagged status for each question involved
        # We iterate through questions in attempt_data to find their sequencecheck values
        # The keys in 'answers' usually contain the question unique ID, but we need to match them.
        # Actually, we should just add sequencecheck for ALL questions on the page,
        # regardless of whether we are answering them or not, to be safe.

        for q in attempt_data.questions:
            # Construct the prefix for this question's inputs.
            # The question ID in parsed data is like 'question-566730-1'.
            # The input names are like 'q566730:1_...'.
            # We need to extract the uniqueid and slot from the ID or just look at subquestion names.

            # If we have subquestions, we can get the prefix from their names.
            prefix = ""
            if q.subquestions:
                # Take the first subquestion's name, e.g., 'q566730:1_sub1_answer'
                # Split by '_' to get 'q566730:1'
                first_name = q.subquestions[0]['name']
                if first_name:
                    prefix = first_name.split('_')[0]

            # If we couldn't determine prefix from subquestions (e.g. simple question),
            # we might need to parse it from the question div ID or sequencecheck name if we had it.
            # But wait, we parsed sequencecheck value, but what is its NAME?
            # We didn't parse the sequencecheck NAME, only VALUE.
            # Moodle requires 'q{uniqueid}:{slot}_:sequencecheck': value.

            # Let's assume the user passes the correct keys in 'answers'.
            # But for sequencecheck, we need to construct the key.
            # In parsers.py, we extracted sequencecheck value.
            # We should probably have extracted the name too, or at least the prefix.

            # Let's try to infer the prefix from the subquestion names if available.
            if prefix and q.sequencecheck:
                payload[f'{prefix}_:sequencecheck'] = q.sequencecheck
                payload[f'{prefix}_:flagged'] = '0' # Default to not flagged

        if finish_attempt:
            payload['next'] = 'テストを終了する ...' # This text might vary by language!
            # Moodle often checks the presence of the button name.
            # 'finishattempt' might be safer if it exists as a hidden field, but usually it's a submit button.
            # In English it's 'Finish attempt ...'. In Japanese 'テストを終了する ...'.
            # Safer to include 'next' with some value.
        else:
            payload['next'] = 'Next'

        logger.info(f"Submitting quiz answers for attempt {attempt_data.attempt_id}")
        try:
            response = self.session.post(url, data=payload)
            response.raise_for_status()
            logger.info(f"Submission successful. Redirected to: {response.url}")
            return response.url
        except (MoodleRequestError, Exception) as e:
            logger.error(f"Error submitting quiz answers: {e}")
            return None

    def finish_quiz_attempt(self, attempt_id: str, sesskey: str, cmid: str) -> Optional[str]:
        """
        Finalizes the quiz attempt (equivalent to clicking "Submit all and finish").

        :param attempt_id: The attempt ID.
        :param sesskey: The session key.
        :param cmid: The course module ID (quiz ID).
        :return: The URL of the review page or None on failure.
        """
        url = urljoin(self.session.base_url, "mod/quiz/processattempt.php")

        payload = {
            'attempt': attempt_id,
            'finishattempt': '1',
            'timeup': '0',
            'slots': '',
            'cmid': cmid,
            'sesskey': sesskey
        }

        logger.info(f"Finishing quiz attempt {attempt_id} (cmid={cmid})")
        try:
            response = self.session.post(url, data=payload)
            response.raise_for_status()
            logger.info(f"Finish successful. Redirected to: {response.url}")
            return response.url
        except (MoodleRequestError, Exception) as e:
            logger.error(f"Error finishing quiz attempt: {e}")
            return None
