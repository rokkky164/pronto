from django.core.exceptions import ValidationError
from django.db.models.fields.files import FieldFile

from bulk_upload.constants import SPREADSHEET_MIME_TYPES, SPREADSHEET_MIME_NAMES
from question.settings import IMAGE_MIME_TYPES, MAX_QUESTION_FILE_SIZE
from utils.constants import INVALID_IMAGE_TYPE, INVALID_FILE_TYPE
from utils.constants import MAX_FILE_SIZE_EXCEEDED
from utils.helpers import calculate_file_size


def check_file_mime_type(file=None, mime_type_list: list = None) -> None:
    try:
        if file.content_type not in mime_type_list:
            raise ValidationError(INVALID_IMAGE_TYPE)
    except:
        pass


def check_file_size(file=None, max_size: int = None) -> None:
    if calculate_file_size(file=file) > max_size:
        raise ValidationError(MAX_FILE_SIZE_EXCEEDED.format(max_size / 1000000))


def verify_excel_mime_type(file):
    if type(file) == FieldFile:
        if file.name.split('/')[-1].split('.')[-1] not in SPREADSHEET_MIME_NAMES:
            raise ValidationError(INVALID_FILE_TYPE)
    else:
        # Check MIME type to check for file corruption.
        if file.content_type not in SPREADSHEET_MIME_TYPES:
            raise ValidationError(INVALID_FILE_TYPE)


def verify_excel_size(file):
    # Check whether file exceeds maximum file size.
    size = calculate_file_size(file=file)
    if size >= MAX_QUESTION_FILE_SIZE:
        raise ValidationError(MAX_FILE_SIZE_EXCEEDED.format(MAX_QUESTION_FILE_SIZE / 1000000))


def verify_logo_mime_type(logo):
    check_file_mime_type(file=logo, mime_type_list=LOGO_MIME_TYPES)


def verify_logo_size(logo):
    check_file_size(file=logo, max_size=LOGO_MAX_SIZE)


def verify_document_mime_type(document):
    check_file_mime_type(file=document, mime_type_list=KYC_DOCUMENT_MIME_TYPES)


def verify_document_size(logo):
    check_file_size(file=logo, max_size=KYC_DOCUMENT_MAX_SIZE)
