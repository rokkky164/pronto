import hashlib
import logging
import os
import random
import string
from datetime import datetime
from hashlib import md5
from io import BytesIO
from json import loads
from os import SEEK_END
from os import remove
from os.path import exists
from smtplib import SMTPException
from sys import getsizeof

import pandas as pd
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.timezone import now, timedelta
from pronto.settings import DEFAULT_FROM_EMAIL, SERVER_EMAIL, BACK_END_HOST
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN
)
from retry import retry
from google.cloud import storage

from .constants import (
    BADGES_DATA, INDEX_BADGES, SUCCESS, ERROR, MAIL_NOTIFICATION_RETRIES, MAIL_NOTIFICATION_RETRY_DELAY,
    INSUFFICIENT_PERMISSIONS,
    RESOURCE_NOT_FOUND, BRONZE_GEMS, BRONZE_BADGE, SILVER_GEMS, SILVER_BADGE, GOLD_GEMS, GOLD_BADGE, DIAMOND_GEMS,
    DIAMOND_BADGE, CHAMPION_GEMS, CHAMPION_BADGE, DEFAULT_SUPPORT_EMAIL, CORPORATE_HOST_LIST, DEFAULT_ORGANIZATION_NAME,
    DEFAULT_ORG_LOGO_URL, MAILGUN_DOMAIN
)
import re


def create_response(
        success: bool = None,
        insufficient_permissions: bool = None,
        resource_missing: bool = None,
        message: str = None,
        data=None
) -> Response:
    if success:
        status, data_status = HTTP_200_OK, SUCCESS
    else:
        data_status = ERROR
        if insufficient_permissions:
            status, message = HTTP_403_FORBIDDEN, INSUFFICIENT_PERMISSIONS
        elif resource_missing:
            status, message = HTTP_404_NOT_FOUND, RESOURCE_NOT_FOUND
        else:
            status = HTTP_400_BAD_REQUEST

    return Response(status=status, data={'status': data_status, 'message': message, 'data': data})


def calculate_file_size(file=None):
    file.seek(0, SEEK_END)
    size = file.tell()
    file.seek(0)
    return size


def get_stored_file_hash(file_path=None):
    md5_obj = md5()
    with open(file_path, 'rb') as file:
        hash_value = file.read()
        md5_obj.update(hash_value)
        return md5_obj.hexdigest()


def get_in_memory_file_hash(file=None):
    md5_obj = md5()
    hash_value = file.read()
    md5_obj.update(hash_value)
    return md5_obj.hexdigest()


def load_request_json_data(request_data=None, json_key_list=None):
    data = dict()
    for key in request_data:
        if key in json_key_list and type(request_data[key]) != list:
            data[key] = loads(request_data[key])
        else:
            data[key] = request_data[key]
    return data


def compare_file_hashes(in_memory_file=None, stored_file_path=None):
    image_hash = get_in_memory_file_hash(file=in_memory_file)
    existing_image_hash = get_stored_file_hash(
        file_path=stored_file_path) if stored_file_path else None

    if image_hash == existing_image_hash:
        return True
    return False


def remove_keys_from_data(data: dict, key_list: list):
    for key in key_list:
        if key in data:
            del data[key]
    return data


def delete_files_from_path_list(path_list=None):
    for path in path_list:
        if exists(path):
            remove(path)


def generate_random_code(length: int = 8):
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(length))


def get_required_details_for_mail(host_name: str, institute=None, user=None, corporate=None) -> dict:
    from_email = DEFAULT_FROM_EMAIL
    alias_name = "Student"
    org_name = DEFAULT_ORGANIZATION_NAME
    logo_url = DEFAULT_ORG_LOGO_URL
    support_email = DEFAULT_SUPPORT_EMAIL

    if corporate or host_name in CORPORATE_HOST_LIST:
        alias_name = "Candidate"
        if institute:
            parent = institute.get_root()
            if institute.email_prefix:
                email_prefix = institute.email_prefix
            elif parent.email_prefix:
                email_prefix = parent.email_prefix
            else:
                email_prefix = user.role.label
            email_prefix = email_prefix.replace('@', ' ')
            support_email = institute.email if institute.email else institute.created_by.email
            org_name = institute.name
            if institute.logo:
                logo_url = BACK_END_HOST + institute.logo.url
            org_mail = f'<{org_name.lower().replace(" ", "_")}{MAILGUN_DOMAIN}>'
            from_email = f"{email_prefix} " + org_mail if user else DEFAULT_FROM_EMAIL

    return {
        "from_email": from_email,
        "alias_name": alias_name,
        "org_name": org_name,
        "logo_url": logo_url,
        "support_email": support_email
    }


@retry(exceptions=SMTPException, tries=MAIL_NOTIFICATION_RETRIES, delay=MAIL_NOTIFICATION_RETRY_DELAY)
def notification_mail(
        email_template: str = None, subject: str = None, body: dict = None, recipient_list=None,
        tags: list = None, track_clicks: bool = False, meta_data: dict = None, bcc_recipient_list=None,
        from_email=DEFAULT_FROM_EMAIL, message_id: str = None
):
    body_message = render_to_string(email_template, body)
    if not recipient_list:
        recipient_list = [SERVER_EMAIL]

    header = {'message-id': message_id} if message_id else {}

    message = EmailMultiAlternatives(
        f'{subject}',
        body_message,
        from_email,
        to=recipient_list,
        bcc=bcc_recipient_list,
        headers=header
    )
    message.attach_alternative(body_message, 'text/html')

    # Optional Anymail extensions:
    if meta_data:
        message.metadata = meta_data
    if tags:
        message.tags = tags
    message.track_clicks = track_clicks
    message.send(fail_silently=False)

    if not message:
        raise SMTPException()


def get_in_memory_file_upload(image, file_name=None, mime_type=None, file_format=None):
    # image = Image.open(file_path).convert('RGB').resize((800, 800), Image.ANTIALIAS)
    output = BytesIO()
    image.save(output, format=str.upper(file_format), quality=85)
    output.seek(0)
    return InMemoryUploadedFile(output, 'ImageField', file_name, mime_type, getsizeof(output), None)


def get_excel_hash(file):
    md5 = hashlib.md5()
    with open(file, 'rb') as file:
        hash_value = file.read()
        md5.update(hash_value)
        return md5.hexdigest()


def get_badge_by_gems(gems: int):
    if BRONZE_GEMS <= gems < SILVER_GEMS:
        return BRONZE_GEMS, BRONZE_BADGE
    elif SILVER_GEMS <= gems < GOLD_GEMS:
        return SILVER_GEMS, SILVER_BADGE
    elif GOLD_GEMS <= gems < DIAMOND_GEMS:
        return GOLD_GEMS, GOLD_BADGE
    elif DIAMOND_GEMS <= gems < CHAMPION_GEMS:
        return DIAMOND_GEMS, DIAMOND_BADGE
    elif gems >= CHAMPION_GEMS:
        return CHAMPION_GEMS, CHAMPION_BADGE
    else:
        return None, None
    

def get_next_badge_data(current_badge: str = None) -> any:
    if not current_badge:
        return {'badge': INDEX_BADGES[1], 'gems': BADGES_DATA[INDEX_BADGES[1]]['gems']}
    badge_data = BADGES_DATA[current_badge]
    if badge_data['index'] >= len(BADGES_DATA):
        return None
    return {
        "badge": INDEX_BADGES[badge_data['index']+1], 
        "gems": BADGES_DATA[INDEX_BADGES[badge_data['index']+1]]['gems']
    }
    
    
def convert_xls_to_xlsx(file=None, folder_path=None, file_path=None):
    files = pd.ExcelFile(file)
    
    # Create directory with file
    if not os.path.isdir(folder_path):
        os.makedirs(folder_path)
    writer = pd.ExcelWriter(file_path)
    for sheet in files.sheet_names:
        excel_file = pd.read_excel(file, sheet_name=sheet)
        excel_file.to_excel(writer, sheet_name=sheet, header=True, index=False)
    writer.save()
    
    
def delete_temp_folder(folder_path, file_path):
    delete_file = os.path.isdir(folder_path)
    if delete_file:
        os.remove(file_path)
        os.rmdir(folder_path)

def seprate_questions(a, b):
    q, r = divmod(a, b)
    return [q + 1] * r + [q] * (b - r)


def get_hostname_from_request(request) -> str:
    hostname = request.headers.get('origin', None)
    hostname = hostname.split('//')[-1] if hostname else request.get_host()
    return hostname


def get_image_path(image=None):
    return f'/media/{image}' if image else None


def get_unique_mailgun_message_id(module: str, hostname: str = None) -> str:
    return f'{module}-{datetime.timestamp(datetime.now())}@{hostname}'


def remove_spaces_and_format_string(string_: str) -> str:
    return re.sub(' +', ' ', string_.title().strip())


def get_bucket(bucket_name) -> storage.bucket.Bucket:
    file_path = f"/home/user/pronto/pronto-eac899977c9b.json"

    storage_client = storage.Client.from_service_account_json(file_path)
    bucket = storage_client.bucket(bucket_name)

    return bucket


def create_directory_if_not_exists(directory_path):
    if not os.path.exists(directory_path):
        try:
            os.makedirs(directory_path)
        except OSError as error:
            (logging.getLogger(__name__ + 'create_directory_if_not_exists')
             .info(f"Error creating directory '{directory_path}': {error}"))


def catalog_directory_path(instance, filename):
    return "catalog/{}/{}".format(instance.id, filename)