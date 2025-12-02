from typing import TypedDict, List, Optional

class Course(TypedDict):
    id: int
    name: str
    url: str
    image_url: Optional[str]
    teachers: List[str]

class Category(TypedDict):
    id: Optional[int]
    name: str
    url: str
    course_count: int
    has_children: bool

class Module(TypedDict):
    id: Optional[int]
    type: str
    name: str
    url: Optional[str]
    description: Optional[str]
    completed: bool

class Section(TypedDict):
    id: Optional[str]
    name: str
    summary: str
    modules: List[Module]

class FileItem(TypedDict):
    filename: str
    url: str
    mimetype: Optional[str]

class AssignmentDetails(TypedDict):
    title: str
    intro: str
    attachments: List[FileItem]
    submission_status: str
    grading_status: str
    due_date: str
    time_remaining: str
    last_modified: str
    submission_files: List[FileItem]

class FolderDetails(TypedDict):
    title: str
    files: List[FileItem]
    download_all_url: Optional[str]

class ForumDetails(TypedDict):
    title: str
    intro: str
    has_discussions: bool

class PageDetails(TypedDict):
    title: str
    content: str
    last_modified: str

class QuizAttempt(TypedDict):
    attempt_number: int
    state: str
    grade: Optional[str]
    review_url: Optional[str]
    feedback: Optional[str]

class QuizDetails(TypedDict):
    title: str
    intro: str
    attempts: List[QuizAttempt]
    feedback: Optional[str]
    can_attempt: bool
