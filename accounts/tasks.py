import logging

from django.utils.timezone import now, timedelta

from accounts.constants import (
    ACCOUNT_ACTIVATION_MAIL_MESSAGE, ACCOUNT_ACTIVATION_MAIL_SUBJECT, RESEND_VERIFICATION_MAIL_TAG,
    ACCOUNT_ACTIVATION_MAIL_HEADER, SEND_PASSWORD_RESET_MAIL_HEADER, SEND_PASSWORD_RESET_MAIL_MESSAGE,
    SEND_PASSWORD_RESET_MAIL_SUBJECT, ACCOUNT_ACTIVATION_MAIL_TAG, SEND_PASSWORD_RESET_MAIL_TAG,
    RESEND_VERIFICATION_MAIL_MESSAGE, RESEND_VERIFICATION_MAIL_SUBJECT, SEND_EMAIL_CHANGE_VERIFICATION_EMAIL_HEADER,
    SEND_EMAIL_CHANGE_VERIFICATION_EMAIL_MESSAGE, SEND_EMAIL_CHANGE_VERIFICATION_EMAIL_TAG,
    SEND_EMAIL_CHANGE_VERIFICATION_EMAIL_SUBJECT, SEND_EMAIL_TO_NEW_USER_HEADER,
    SEND_EMAIL_TO_NEW_USER_MESSAGE, SEND_EMAIL_TO_NEW_USER_SUBJECT,
    SEND_EMAIL_TO_NEW_USER_TAG, SEND_EMAIL_TO_NEW_USER_MESSAGE_SUPPORT,
    SEND_EMAIL_TO_NEW_USER_HEADER_V2, SEND_EMAIL_TO_NEW_USER_SUBJECT_V2, SEND_EMAIL_TO_NEW_USER_TAG_V2,
    SEND_EMAIL_TO_NEW_USER_SUBJECT_CROPORATE, SEND_EMAIL_TO_NEW_USER_HEADER_CORPORATE, SEND_DELETE_REQUEST_HEADER,
    SEND_DELETE_REQUEST_MAIL_TAG, SEND_DELETE_REQUEST_MAIL_SUBJECT
)
from accounts.models import User, DeleteUserAccountRequest
from authorization.models import AccountVerificationRequest, UserSession, UserEnvironmentDetails
from pronto.celery import app
from pronto.settings import URL_PREFIX, RESEND_NOTIFICATION_EMAIL_TIME, DELETE_ACCOUNT_REQUEST_HOURS

from utils.constants import (MAIL_DATE_TIME_FORMAT, CORPORATE_HOST_LIST, DEFAULT_SUPPORT_EMAIL,
                             ONBOARD_EX_CANDIDATE_CRPORATE_TEMPLATE, ONBOARD_EX_CANDIDATE_TEMPLATE,
                             DEFAULT_SUPPORT_EMAIL, ONBOARD_CRPORATE_ADMIN_TEMPLATE, DASHBOARD_HOST_DICT)
from utils.helpers import notification_mail, get_required_details_for_mail
from utils.db_interactors import get_record_by_filters, get_record_by_id, db_create_record, db_update_instance, \
    db_update_records_with_filters
from utils.tasks import base_task


logger = logging.getLogger(__name__)


@app.task(name='InitiateAccountVerification')
def initiate_account_verification(user_id: int):
    """
    This task creates an entry in AccountVerificationRequest table and sends email
    """
    try:
        user = User.objects.get(id=user_id)
    except Exception as e:
        logger.debug('User Doesn\'t exist')
        return

    account_verification_request = AccountVerificationRequest(
        user=user
    )
    account_verification_request.save()
    if user.email:
        body = {
            'fullname': user.get_full_name(),
            'message_heading': ACCOUNT_ACTIVATION_MAIL_HEADER,
            'username': user.username,
            'role': user.role.label,
            'registered_at': user.date_joined.strftime(MAIL_DATE_TIME_FORMAT),
            'message': ACCOUNT_ACTIVATION_MAIL_MESSAGE,
            'code': account_verification_request.verification_code
        }
        notification_mail(
            email_template='email/initiate_account_verification_template.html',
            subject=ACCOUNT_ACTIVATION_MAIL_SUBJECT,
            body=body,
            recipient_list=[f"{user.get_full_name()} <{user.email}"],
            tags=[ACCOUNT_ACTIVATION_MAIL_TAG],
            track_clicks=True,
            meta_data={'user_id': user_id}
        )
    return account_verification_request.verification_code


@app.task(name='SendPasswordResetEmail')
def send_password_reset_email(user_id, full_name: str, email: str, verification_code: str):
    """
    This task creates an entry in AccountVerificationRequest table and sends email
    """
    if email:
        body = {
            'fullname': full_name, 'message_heading': SEND_PASSWORD_RESET_MAIL_HEADER,
            'message': SEND_PASSWORD_RESET_MAIL_MESSAGE, 'code': verification_code
        }

        notification_mail(
            email_template='email/accounts/send_password_reset_email_template.html',
            subject=SEND_PASSWORD_RESET_MAIL_SUBJECT,
            body=body,
            recipient_list=[f"{full_name} <{email}>"],
            tags=[SEND_PASSWORD_RESET_MAIL_TAG],
            track_clicks=True,
            meta_data={'user_id': user_id}
        )


@app.task(name='ResendVerificationCode')
def resend_verification_code(verification_id: int):

    """
    verification : verification object
    This function send Authentication code and sends email
    """
    try:
        verification = AccountVerificationRequest.objects.get(id=verification_id)
    except AccountVerificationRequest.DoesNotExist:
        logger.error('Account Verification Code Doesn\'t exist')
        return
    user = verification.user
    if verification.user.email:

        body = {
            'fullname': user.get_full_name(),
            'message': RESEND_VERIFICATION_MAIL_MESSAGE, 'code': verification.verification_code
        }

        notification_mail(
            email_template='email/accounts/resend_verification_email_template.html',
            subject=RESEND_VERIFICATION_MAIL_SUBJECT,
            body=body,
            recipient_list=[f"{user.get_full_name()} <{user.email}>"],
            tags=[RESEND_VERIFICATION_MAIL_TAG],
            track_clicks=True,
            meta_data={'user_id': user.id}
        )

    return True


@app.task(name='SendEmailChangeVerificationCode')
def send_email_change_verification_code(user_id: int, full_name: str, new_email: str, verification_code: str):
    """
        This task creates an entry in AccountVerificationRequest table and sends email
        """
    if new_email:
        body = {
            'fullname': full_name, 'message_heading': SEND_EMAIL_CHANGE_VERIFICATION_EMAIL_HEADER,
            'message': SEND_EMAIL_CHANGE_VERIFICATION_EMAIL_MESSAGE,  'code': verification_code
        }

        notification_mail(
            email_template='email/accounts/change_email_verification_template.html',
            subject=SEND_EMAIL_CHANGE_VERIFICATION_EMAIL_SUBJECT,
            body=body,
            recipient_list=[f"{full_name} <{new_email}>"],
            tags=[SEND_EMAIL_CHANGE_VERIFICATION_EMAIL_TAG],
            track_clicks=True,
            meta_data={'user_id': user_id}
        )


@app.task(name='SendMailToRegisterUserForLogin')
def send_mail_to_register_user_for_login(user_id, full_name: str, email: str,
                                                  username: str, password: str,
                                                  host_name: str, support_email= None):
    """
    This task sends mail to all users who were added to a batch
    """
    body = {
        'fullname': full_name,
        'message_heading': SEND_EMAIL_TO_NEW_USER_HEADER_V2,
        'message': SEND_EMAIL_TO_NEW_USER_MESSAGE_SUPPORT.format(username=username, password=password,
                                                                 support_email=support_email),
        'login_link': f'{URL_PREFIX}{host_name}/auth/login'
    }

    notification_mail(
        email_template= ONBOARD_EX_CANDIDATE_TEMPLATE,
        subject=SEND_EMAIL_TO_NEW_USER_SUBJECT_V2,
        body=body,
        recipient_list=[f"{full_name} <{email}>"],
        tags=[SEND_EMAIL_TO_NEW_USER_TAG_V2],
        track_clicks=True,
        meta_data={'user_id': user_id}
    )


@base_task
def set_user_environment_session(
        user_id: int,
        os: str = None,
        os_version: str = None,
        ip_address: str = None,
        browser: str = None,
        browser_version: str = None,
        device_type: str = None,
        device: str = None,
        token: str = None,

) -> bool:
    environment_data = {
        'os': os,
        'os_version': os_version,
        'ip_address': ip_address,
        'browser': browser,
        'browser_version': browser_version,
        'device_type': device_type,
        'device': device
    }
    logger_prefix = f"set_user_environment_session: User: {user_id}. "
    logger.info(logger_prefix + f"environment_data: {environment_data}")

    status, user = get_record_by_id(model=User, _id=user_id)
    if not status:
        logger.error(logger_prefix + f"Error while getting user. Error: {user}")
        return False

    # set user's environment
    status, environment = get_record_by_filters(model=UserEnvironmentDetails, filters=environment_data, distinct=True)
    if not status:
        environment = None
        logger.error(logger_prefix + f"Error while getting environment. Error: {environment}")
    elif not environment:
        status, environment = db_create_record(model=UserEnvironmentDetails, data=environment_data)
        if not status:
            environment = None
            logger.error(logger_prefix + f"Error while creating environment. Error: {environment}")
    else:
        environment = environment.last()

    # set user's session
    session_data = {
        'user': user,
        'token': token,
        'user_env_details': environment
    }
    status, session = get_record_by_filters(
        model=UserSession, filters={'user': user, "user_env_details": environment}, distinct=True)
    if not status:
        logger.error(logger_prefix + f"Error while getting session. Error: {session}")
    elif not session:
        status, session = db_create_record(model=UserSession, data=session_data)
        if not status:
            logger.error(logger_prefix + f"Error while creating session. Error: {session}")
    else:
        status, session = db_update_instance(instance=session.last(), data=session_data)
        if not status:
            logger.error(logger_prefix + f"Error while updating session. Error: {session}")

    return True


@app.task(name='SendMailTradeProntoAdminForLogin')
def send_mail_to_tradepronto_admin_for_login(user_id, full_name: str, email: str,
                                           username: str, password: str, host_name: str,
                                           message_id: str = None, support_email=None):
    """
    This task sends mail to all users who were added to a batch
    """
    if host_name in DASHBOARD_HOST_DICT:
        host_name = DASHBOARD_HOST_DICT.get(host_name)

    body = {
        'fullname': full_name,
        'message_heading': SEND_EMAIL_TO_NEW_USER_SUBJECT,
        'login_link': f'{URL_PREFIX}{host_name}/auth/login',
        'user_credential': {'username': username, 'password': password},
        'support_email': DEFAULT_SUPPORT_EMAIL,
    }

    notification_mail(
        email_template=ONBOARD_CRPORATE_ADMIN_TEMPLATE,
        subject=SEND_EMAIL_TO_NEW_USER_SUBJECT,
        body=body,
        recipient_list=[f"{full_name} <{email}>"],
        tags=[SEND_EMAIL_TO_NEW_USER_TAG],
        track_clicks=True,
        meta_data={'user_id': user_id},
        message_id=message_id
    )


@base_task
def delete_user_account_task(account_request_id: int) -> bool:
    log_prefix = f"delete_user_account_task: Request id: {account_request_id}. "
    status, acc_req = get_record_by_id(model=DeleteUserAccountRequest, _id=account_request_id)
    if not status:
        logger.error(log_prefix + f"Error while getting record. Error: {acc_req}")
        return False
    acc_req: DeleteUserAccountRequest

    if acc_req.is_account_deleted:
        logger.info(log_prefix + f"User account already deleted.")
        return True
    elif acc_req.is_logged_in:
        logger.info(log_prefix + f"After the deletion request, the user logged in within the 7-day timeframe.")
        return True
    else:
        status, user = db_update_instance(instance=acc_req.user, data={'is_deleted': True})
        if not status:
            logger.error(log_prefix + f"Error while deleting user. Error: {user}")
            return False

        status, acc_req = db_update_instance(instance=acc_req, data={'is_account_deleted': True})
        if not status:
            logger.error(log_prefix + f"Error while updating request. Error: {acc_req}")
            return False
        logger.info(log_prefix + "User delete successfully.")
        return True


@base_task
def check_and_update_user_delete_request_task(user_id: int) -> bool:
    log_prefix = f"check_and_update_user_delete_request_task: user id: {user_id}. "
    status, delete_requests = db_update_records_with_filters(
        model=DeleteUserAccountRequest,
        filters={"user": user_id, "is_logged_in": False, "is_account_deleted": False},
        data={'is_logged_in': True}
    )
    if not status:
        logger.error(log_prefix + f"Error while get delete requests. Error: {delete_requests}")
        return False
    return True


@app.task(name='SendDeleteRequestEmail')
def send_delete_request_email(user_id, full_name: str, email: str, host_name: str, identifier: str):
    """
    This task creates an entry in AccountVerificationRequest table and sends email
    """
    if email:
        body = {
            'fullname': full_name, 'message_heading': SEND_DELETE_REQUEST_HEADER,
            'delete_link': f'{URL_PREFIX}{host_name}/auth/confirm-request?uid={identifier}',
            'expire_hours': DELETE_ACCOUNT_REQUEST_HOURS
        }

        notification_mail(
            email_template='email/accounts/send_delete_request_email.html',
            subject=SEND_DELETE_REQUEST_MAIL_SUBJECT,
            body=body,
            recipient_list=[f"{full_name} <{email}>"],
            tags=[SEND_DELETE_REQUEST_MAIL_TAG],
            track_clicks=True,
            meta_data={'user_id': user_id}
        )
