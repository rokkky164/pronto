"""
Response Constants Start.
"""
from os import getenv

SUCCESS = 'SUCCESS'
ERROR = 'ERROR'

"""
Response Constants End.
"""

"""
HTTP Response Codes Start.
"""

SUCCESS_CODE = 200
BAD_REQUEST = 400
UNAUTHORIZED_CODE = 401
FORBIDDEN = 403
MISSING_RESOURCE = 404

"""
HTTP Response Codes End.
"""

"""
Host constants start
"""
CORPORATE_HOST = 'corporatedev.prep.study'
CORPORATE_HOST_LIST = ['corporatedev.prep.study', 'corporate.prep.study', 'localhost:3000']
DASHBOARD_HOST_DICT = {
    'dashboard.prep.study': 'corporate.prep.study',
    'localhost:3000': 'localhost:3000'
}
BACKEND_HOST_LIST = ['localhost:8000', 'api.prep.study', 'corporatedev.prep.study', 'dev2.prep.study']
"""
Host constants end
"""

"""
Common Model Constants Start.
"""

DELETION_STATUS_MAX_LENGTH = 7
CONTACT_NUMBER_MAX_LENGTH = 15
EMAIL_MAX_LENGTH = 254

"""
Common Model Constants End.
"""

"""
Badges start
"""
BRONZE_BADGE = "Bronze"
SILVER_BADGE = "Silver"
GOLD_BADGE = "Gold"
DIAMOND_BADGE = "Diamond"
CHAMPION_BADGE = "Champion"


# Badges values
BRONZE_GEMS = int(getenv('BRONZE_GEMS', default=1000))
SILVER_GEMS = int(getenv('SILVER_GEMS', default=2000))
GOLD_GEMS = int(getenv('GOLD_GEMS', default=3000))
DIAMOND_GEMS = int(getenv('DIAMOND_GEMS', default=4000))
CHAMPION_GEMS = int(getenv('CHAMPION_GEMS', default=5000))


BADGES_DATA = {
    BRONZE_BADGE: {'index': 1, 'gems': BRONZE_GEMS},
    SILVER_BADGE: {'index': 2, 'gems': SILVER_GEMS},
    GOLD_BADGE: {'index': 3, 'gems': GOLD_GEMS},
    DIAMOND_BADGE: {'index': 4, 'gems': DIAMOND_GEMS},
    CHAMPION_BADGE: {'index': 5, 'gems': CHAMPION_GEMS},
}

INDEX_BADGES = {value['index']: key for key, value in BADGES_DATA.items()}

"""
Badges end
"""

"""
Response Messages Start.
"""

UNAUTHORIZED_ACCESS = 'You must be authenticated to access this endpoint.'
INSUFFICIENT_PERMISSIONS = 'You do not have permission to perform this action.'
INVALID_IMAGE_TYPE = 'Invalid image type.'
INVALID_FILE_TYPE = 'Invalid file type'
MAX_FILE_SIZE_EXCEEDED = 'Max file size allowed: {} MB.'
FIELD_REQUIRED = 'This field is required.'
RESOURCE_NOT_FOUND = 'No resource found.'

"""
Response Messages End.
"""


"""
Upcoming Exam Notifications Constants Start. 
"""

MAIL_NOTIFICATION_RETRIES = 3
MAIL_NOTIFICATION_RETRY_DELAY = 30

"""
Upcoming Exam Notifications Constants End. 
"""


"""
Redis Prefix Constants Start.
"""

STUDENT_ANSWER_CACHE_KEY = 'STUDENT-ANSWERS:{}-{}-{}'
EXAMINEE_QUESTION_CACHE_KEY = 'EXAMINEE-QUESTIONS:{}-{}-{}'
QUESTION_PAPER_CACHE_KEY = 'QUESTION_PAPER:{}'
RANDOMIZE_QUESTION_PAPER_CACHE_KEY = 'RANDOMIZE_QUESTION_PAPER:{exam_id}-{examine_id}'
EXAMINEE_SCREEN_VIOLATION_KEY = 'SCREEN-VIOLATION:{user_exam_submission_id}'

"""
Redis Prefix Constants End.
"""

"""
Mail start
"""
MAIL_DATE_TIME_FORMAT = '%A %I:%M:%S %p %d %b, %Y'
DEFAULT_SUPPORT_EMAIL = "support@prep.study"
DEFAULT_ORGANIZATION_NAME = 'PrepStudy!'
DEFAULT_ORG_LOGO_URL = ('https://hs-8886753.f.hubspotemail.net/hs/hsstatic/TemplateAssets/static-1.60/img/'
                        'hs_default_template_images/email_dnd_template_images/ThankYou-Flower.png')
MAILGUN_DOMAIN = "@pinakasolutions.com"
"""
Mail End
"""


"""
Permission Messages Start.
"""

YOU_ARE_NOT_ALLOWED_TO_PERFORM_THIS_ACTION = 'You are not allowed to perform this action'

"""
Permission Messages End.
"""

"""
CK Editor Constants start
"""
CK_EDITOR_SIZE_FACTOR = 11
"""
CK Editor Constants end
"""


DIGITS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
LOCASE_CHARACTERS = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h',
                 'i', 'j', 'k', 'm', 'n', 'o', 'p', 'q',
                 'r', 's', 't', 'u', 'v', 'w', 'x', 'y',
                 'z']
UPCASE_CHARACTERS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
                 'I', 'J', 'K', 'M', 'N', 'O', 'P', 'Q',
                 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y',
                 'Z']
SYMBOLS = ['@', '#', '$', '%', '=', ':', '?', '.', '/', '|', '~', '*', '(', ')']

"""
Regexes
"""

EMAIL_VALIDATION_REGEX = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

"""
Templates
"""

ONBOARD_EX_CANDIDATE_TEMPLATE = 'email/accounts/onboard_external_candidate.html'
ONBOARD_EX_CANDIDATE_CRPORATE_TEMPLATE = 'email/accounts/corporate/onboard_external_candidate.html'
ONBOARD_CRPORATE_ADMIN_TEMPLATE = 'email/accounts/corporate/onboard_corporate_admin.html'

COMMENT_CELL_VALUE = 'Comments'
ERROR_FILE = "error.xlsx"


""" Date time start """
MONTH_NAMES = {
    1: 'Jan',
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec"
}
ISO_DATE_FORMAT = "%Y-%m-%d"
""" Date time end """

"""
Bucket start
"""
DATA_MIGRATION_BUCKET = 'pinakasolutions-migration-data'
"""
Bucket end
"""