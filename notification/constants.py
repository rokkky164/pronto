NOTIFICATION_DOES_NOT_EXIST = 'Notification does not exist.'
NOTIFICATION_DELETED = 'Notification deleted successfully.'
NOTIFICATION_UPDATE_SUCCESS = 'Notification updated successfully.'
NOTIFICATION_UPDATE_FAIL = 'Failed to updated Notification.'
NOTIFICATION_CREATION_SUCCESS = 'Notification created successfully.'
NOTIFICATION_CREATION_FAILED = 'Failed to create Notification.'
NOTIFICATION_FETCHED_SUCCESS = 'Notification Fetched Successfully.'
NOTIFICATIONS_FETCHED_SUCCESS = 'notifications Fetched Successfully.'
NOTIFICATIONS_FETCHED_FAIL = 'Failed to fetch notifications.'


APP_NAME = 'notification'
BASENAME = 'notification'
BASENAME_EMAIL = 'notification-email'
URL_PREFIX = r'notification'
URL_PREFIX_EMAIL = r'notification-email'


NOTIFICATION_MAX_LENGTH = 2048
NOTIFICATION_STATUS_MAX_LENGTH = 5
NOTIFICATION_TYPE_MAX_LENGTH = 5


MG_EVENT_SENT = "sent"
MG_EVENT_ACCEPTED = "accepted"
MG_EVENT_CLICKED = "clicked"
MG_EVENT_COMPLAINED = "complained"
MG_EVENT_DELIVERED = "delivered"
MG_EVENT_OPENED = "opened"
MG_EVENT_PERMANENT_FAIL = "permanent_fail"
MG_EVENT_TEMPORARY_FAIL = "temporary_fail"
MG_EVENT_UNSUBSCRIBED = "unsubscribed"


EMAIL_HISTORY_STATUS = {
    "sent": MG_EVENT_SENT,
    "accepted": MG_EVENT_ACCEPTED,
    "clicked": MG_EVENT_CLICKED,
    "complained": MG_EVENT_COMPLAINED,
    "delivered": MG_EVENT_DELIVERED,
    "opened": MG_EVENT_OPENED,
    "permanent_fail": MG_EVENT_PERMANENT_FAIL,
    "temporary_fail": MG_EVENT_TEMPORARY_FAIL,
    'unsubscribed': MG_EVENT_UNSUBSCRIBED
}
