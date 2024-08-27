import logging

from django.utils.timezone import now

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .models import Notification
from .services import create_notification_service

logger = logging.getLogger(__name__)


class NotificationCreateSerializer(ModelSerializer):

    class Meta:
        model = Notification
        exclude = ('created_at', 'updated_at')

    def create(self, validated_data):
        logger.info('Initiating Notification Creation')
        return create_notification_service(**validated_data)


class NotificationRetrieveSerializer(ModelSerializer):
    sender = serializers.SerializerMethodField()
    recipients = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = (
            'id', 'notification', 'status', 'notification_type', 'sender',
            'recipients', 'created_at', 'updated_at'
        )

    def get_sender(self, obj):
        return obj.sender.username

    def get_recipients(self, obj):
        return [elem.username for elem in obj.recipients.all()]
