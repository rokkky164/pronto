from django.db.models import (
    Model,
    DecimalField,
    CharField,
    DateTimeField,
    ManyToManyField,
    ForeignKey,
    TextChoices,
    TextField,
    BooleanField,
    SET_NULL,
    PROTECT, EmailField, JSONField,
)
from django.utils.translation import gettext_lazy as _

from accounts.models import User
from .constants import (
    NOTIFICATION_MAX_LENGTH,
    NOTIFICATION_STATUS_MAX_LENGTH,
    NOTIFICATION_TYPE_MAX_LENGTH, MG_EVENT_UNSUBSCRIBED, MG_EVENT_TEMPORARY_FAIL, MG_EVENT_PERMANENT_FAIL,
    MG_EVENT_OPENED, MG_EVENT_DELIVERED, MG_EVENT_COMPLAINED, MG_EVENT_CLICKED, MG_EVENT_ACCEPTED, MG_EVENT_SENT
)


class Notification(Model):
    class Status(TextChoices):
        CREATED = 'CR', _('Created')
        SENT = 'S', _('Sent')
        READ  = 'R', _('Read')
        UNREAD  = 'U', _('Unread')
    class NotificationTypes(TextChoices):
        # more notification types to be added
        APPROVAL_REQUEST = 'AR', _('Approval Request')
        REPORT_AVAILABLE = 'RA', _('Report Available')
    notification = TextField(max_length=NOTIFICATION_MAX_LENGTH)
    status = CharField(_('Status'), choices=Status.choices,
                                  max_length=NOTIFICATION_STATUS_MAX_LENGTH, default=Status.CREATED)
    notification_type = CharField(_('NotificationType'), choices=NotificationTypes.choices,
    							  max_length=NOTIFICATION_TYPE_MAX_LENGTH)
    recipients = ManyToManyField(User, related_name='recipients')
    sender = ForeignKey(User, on_delete=SET_NULL, related_name='sender', null=True, blank=True)
    created_at = DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = DateTimeField(_('Updated At'), auto_now=True, blank=True, null=True)

    def __str__(self):
        return f"Notification: {self.notification_type}:{self.sender.username}"


class EmailHistory(Model):
    class EmailType(TextChoices):
        BATCH_INVITATION = 'BIN', _('Batch Invitation')
        EXAM_INVITATION = 'EIN', _('Exam Invitation')
        EXAM_ASSIGNMENT = 'EAS', _('Exam Assignment')

    class Status(TextChoices):
        SENT = MG_EVENT_SENT, _('Sent from the backed.')
        ACCEPTED = MG_EVENT_ACCEPTED, _('Tracking Accepted')
        CLICKED = MG_EVENT_CLICKED, _('Tracking Clicks')
        COMPLAINED = MG_EVENT_COMPLAINED, _('Tracking Spam Complaints')
        DELIVERED = MG_EVENT_DELIVERED, _('Tracking Deliveries')
        OPENED = MG_EVENT_OPENED, _('Tracking Opens')
        PERMANENT_FAIL = MG_EVENT_PERMANENT_FAIL, _('Tracking Failures')
        TEMPORARY_FAIL = MG_EVENT_TEMPORARY_FAIL, _('Tracking Failures')
        UNSUBSCRIBED = MG_EVENT_UNSUBSCRIBED, _('Open and Click Bot Detection')

    email_type = CharField(verbose_name='Email type', choices=EmailType.choices, max_length=3)
    message_id = CharField(verbose_name='Message id', max_length=50)
    status = CharField(verbose_name='Status', max_length=20, default=Status.SENT, choices=Status.choices)
    email = EmailField(verbose_name='Email', )
    from_email = CharField(verbose_name='From email', max_length=200)
    created_at = DateTimeField(verbose_name='Created at', auto_now_add=True)
    updated_at = DateTimeField(verbose_name='Updated at', auto_now_add=True)
    mailgun_response = JSONField(verbose_name='Mailgun response', null=True, blank=True)
