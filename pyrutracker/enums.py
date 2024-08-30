from enum import Enum

class Url(Enum):
    HOST = "https://rutracker.org"
    FORUM = f"{HOST}/forum"
    INDEX = f"{FORUM}/index.php"
    AUTH = f"{FORUM}/login.php"
    SEARCH = f"{FORUM}/tracker.php"
    VIEWTOPIC = f"{FORUM}/viewtopic.php"
    DOWNLOAD = f"{FORUM}/dl.php"