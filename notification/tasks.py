from logging import getLogger

from notification.constants import EMAIL_HISTORY_STATUS
from notification.models import EmailHistory
from utils.interactors import get_record_by_filters, db_update_instance
from utils.tasks import base_task

logger = getLogger(__name__)


@base_task
def mailgun_webhook_task(mg_payload):
    logger_prefix = 'mailgun_webhook_task: '
    event = mg_payload['event-data']['event']
    recipient_email = mg_payload['event-data']['recipient']
    message_id = mg_payload['event-data']['message']['headers']['message-id']

    record_status, email_record = get_record_by_filters(
        model=EmailHistory, filters={'message_id': message_id, 'email': recipient_email})
    if not record_status:
        logger.error(logger_prefix + f"Error while getting email history. Error: {record_status}")
        return False
    if not email_record:
        logger.info(logger_prefix + f"Email history record does not exist.")
        return True

    logger.info(logger_prefix + f"Message id: {message_id}.")
    logger.info(logger_prefix + f"Email: {recipient_email}. Event: {event}")
    email_record = email_record.last()
    record_status, upd_email_record = db_update_instance(
        instance=email_record, data={'status': EMAIL_HISTORY_STATUS[event], 'mailgun_response': mg_payload})
    if not record_status:
        logger.error(logger_prefix + f"Error while updating email history. Error: {upd_email_record}")
        return False
    return True
