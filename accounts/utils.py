from authorization.models import UserEnvironmentDetails
import re

from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _

from accounts.constants import USERNAME_VALIDATION_MESSAGE

_re_patterns = {
    'username': "^(?=[a-zA-Z0-9._-]{4,72}$)(?=.*[a-zA-Z._-]+.*)(?!.*[_.-]{2})[^_.-].*[^_.-]$",
    'password': "^[A-Za-z0-9!@#$%^&*]{8,32}$",
    'mobile_number': "^([+]{1}[0-9]{1,3})?[0-9]{10,12}$",
    'first_name': "^(?=.{2,40}$)(?!.*[\.\-\_\ ]{2})[a-z][a-z._ -]*[a-z]$",
    'last_name': "^(?=.{2,40}$)(?!.*[\.\-\_\ ]{2})[a-z][a-z._ -]*[a-z]$",
    'experience': '^\d{1,2}$',
    'section': '^[A-Za-z]$',
    'batch_name': "^(?=.{6,72}$)(?!.*[\.\-\_\,\'\+\:\(\)]{2})[a-zA-Z][a-zA-Z0-9._\-,'+:() ]*[a-zA-Z0-9()]$",
    'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
}


def match_re(pattern, value):
    try:
        return re.match(_re_patterns[pattern], value)
    except Exception as e:
        return False


@deconstructible
class UsernameValidator(validators.RegexValidator):
    regex = r'^(?=.{4,}$)(?!.*[\.\-\_]{2})[a-z][a-z0-9._-]*[a-z0-9]$'
    message = _(USERNAME_VALIDATION_MESSAGE)
    flags = re.ASCII

def check_file_mime_type(file=None, mime_type_list: list = None) -> None:
    try:
        if file.content_type not in mime_type_list:
            raise ValidationError(INVALID_IMAGE_TYPE)
    except:
        pass


def check_file_size(file=None, max_size: int = None) -> None:
    if calculate_file_size(file=file) > max_size:
        raise ValidationError(MAX_FILE_SIZE_EXCEEDED.format(max_size / 1000000))


def user_directory_path(instance, filename):
    return "profile/{}/{}".format(instance.id, filename)


def get_device_type(user_agent=None):
    device_type = None
    if user_agent.is_mobile:
        device_type = UserEnvironmentDetails.DeviceType.MOBILE
    elif user_agent.is_tablet:
        device_type = UserEnvironmentDetails.DeviceType.TABLET
    elif user_agent.is_pc:
        device_type = UserEnvironmentDetails.DeviceType.PC
    elif user_agent.is_bot:
        device_type = UserEnvironmentDetails.DeviceType.BOT
    return device_type


def verify_logo_mime_type(logo):
    check_file_mime_type(file=logo, mime_type_list=LOGO_MIME_TYPES)


def verify_logo_size(logo):
    check_file_size(file=logo, max_size=LOGO_MAX_SIZE)


def verify_document_mime_type(document):
    check_file_mime_type(file=document, mime_type_list=KYC_DOCUMENT_MIME_TYPES)


def verify_document_size(logo):
    check_file_size(file=logo, max_size=KYC_DOCUMENT_MAX_SIZE)

def generate_strong_password():
    MAX_LEN = 12
    COMBINED_LIST = DIGITS + UPCASE_CHARACTERS + LOCASE_CHARACTERS + SYMBOLS
    rand_digit = random.choice(DIGITS)
    rand_upper = random.choice(UPCASE_CHARACTERS)
    rand_lower = random.choice(LOCASE_CHARACTERS)
    rand_symbol = random.choice(SYMBOLS)
    temp_pass = rand_digit + rand_upper + rand_lower + rand_symbol

    for x in range(MAX_LEN - 4): 
        temp_pass = temp_pass + random.choice(COMBINED_LIST) 
        temp_pass_list = array.array('u', temp_pass) 
        random.shuffle(temp_pass_list) 
    
    password = "" 
    for x in temp_pass_list: 
        password = password + x

    return password


def generate_username(first_name, last_name, email):
    first_name = first_name.replace(' ', '')
    last_name = last_name.replace(' ', '')
    random_no = random.randint(1000, 9999)
    userdetails_from_email = email.split("@")[0]
    email_result = re.match("\w+", userdetails_from_email)
    if email_result:
        userdetails_from_email = email_result.group()
    return random.choice([
        f'{first_name}.{last_name}{random_no}',
        f'{last_name}.{first_name}{random_no}',
        f'{userdetails_from_email}{random_no}'
    ])
