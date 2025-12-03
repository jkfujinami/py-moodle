class MoodleError(Exception):
    """Base exception for all Moodle related errors."""
    pass

class MoodleLoginError(MoodleError):
    """Raised when login fails."""
    pass

class MoodleRequestError(MoodleError):
    """Raised when an HTTP request fails."""
    pass

class MoodleParseError(MoodleError):
    """Raised when parsing response fails."""
    pass
