from dataclasses import dataclass
from typing import List, Optional, Dict, Any

@dataclass
class Course:
    id: int
    name: str
    url: str
    image_url: Optional[str]
    teachers: List[str]

@dataclass
class Category:
    id: Optional[int]
    name: str
    url: str
    course_count: int
    has_children: bool

@dataclass
class Module:
    id: Optional[int]
    type: str
    name: str
    url: Optional[str]
    description: Optional[str]
    completed: bool

@dataclass
class Section:
    id: Optional[str]
    name: str
    summary: str
    modules: List[Module]

@dataclass
class FileItem:
    filename: str
    url: str
    mimetype: Optional[str]

@dataclass
class AssignmentDetails:
    title: str
    intro: str
    attachments: List[FileItem]
    submission_status: str
    grading_status: str
    due_date: str
    time_remaining: str
    last_modified: str
    submission_files: List[FileItem]

@dataclass
class FolderDetails:
    title: str
    files: List[FileItem]
    download_all_url: Optional[str]

@dataclass
class ForumDetails:
    title: str
    intro: str
    has_discussions: bool

@dataclass
class PageDetails:
    title: str
    content: str
    last_modified: str

@dataclass
class QuizAttempt:
    attempt_number: int
    state: str
    grade: Optional[str]
    review_url: Optional[str]
    feedback: Optional[str]

@dataclass
class QuizQuestion:
    id: str
    number: int
    text: str
    type: str  # 'multianswer', 'multichoice', etc.
    options: Optional[List[Dict[str, str]]]  # For select/radio options
    subquestions: Optional[List[Dict[str, Any]]] # For multianswer subparts
    sequencecheck: Optional[str] = None

@dataclass
class QuizAttemptData:
    attempt_id: str
    sesskey: str
    slots: str
    questions: List[QuizQuestion]
    next_url: Optional[str]

@dataclass
class QuizDetails:
    title: str
    intro: str
    attempts: List[QuizAttempt]
    feedback: Optional[str]
    can_attempt: bool
    cmid: Optional[int]
    sesskey: Optional[str]
    latest_attempt_data: Optional[QuizAttemptData]
