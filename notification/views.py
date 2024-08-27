import logging

from django.utils.timezone import now, timedelta
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets, mixins, generics
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from accounts.permissions import IsActive
from utils.helpers import create_response
from utils.interactors import get_record_by_id, get_record_by_filters, db_update_instance

from .constants import (
    NOTIFICATION_DOES_NOT_EXIST,
    NOTIFICATION_DELETED,
    NOTIFICATION_UPDATE_SUCCESS,
    NOTIFICATION_UPDATE_FAIL,
    NOTIFICATION_CREATION_SUCCESS,
    NOTIFICATION_CREATION_FAILED,
    NOTIFICATION_FETCHED_SUCCESS,
    NOTIFICATIONS_FETCHED_SUCCESS,
    NOTIFICATIONS_FETCHED_FAIL, EMAIL_HISTORY_STATUS
)
from .models import Notification, EmailHistory
from .serializers import (
    NotificationCreateSerializer,
    NotificationRetrieveSerializer
)
from .interactors import get_notifications
from .pagination import NotificationResultsSetPagination
from .tasks import mailgun_webhook_task

logger = logging.getLogger(__name__)


class NotificationViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = [IsAuthenticated,]
    pagination_class = NotificationResultsSetPagination
    ordering = ['-id']
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    
    def get_queryset(self):
        return get_notifications(self.request.user)

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return NotificationRetrieveSerializer
        elif self.action == 'create':
            return NotificationCreateSerializer
        else:
            return NotificationRetrieveSerializer
    
    def get_object(self, *args, **kwargs):
        status, notification = get_record_by_id(model=Notification, _id=self.kwargs.get('pk'))
        if not status:
            return None
        return notification

    def retrieve(self, request, *args, **kwargs):
        notification = self.get_object()
        if not notification:
            return create_response(success=False, message=NOTIFICATION_DOES_NOT_EXIST)

        serializer = self.get_serializer(notification)
        return create_response(success=True, message=NOTIFICATION_FETCHED_SUCCESS, data=serializer.data)

    def destroy(self, request, *args, **kwargs):
        notification = self.get_object()

        if not notification:
            return create_response(
                success=False,
                message=NOTIFICATION_DOES_NOT_EXIST
            )

        notification.delete()

        return create_response(
            success=True,
            message=NOTIFICATION_DELETED
        )

    def partial_update(self, request, *args, **kwargs):
        notification = self.get_object()
        request_data = request.data

        if not notification:
            return create_response(
                success=False,
                message=NOTIFICATION_DOES_NOT_EXIST
            )

        serializer = self.get_serializer(notification, data=request_data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return create_response(
                success=True,
                message=NOTIFICATION_UPDATE_SUCCESS,
                data=serializer.data
            )
        else:
            return create_response(
                success=False,
                message=NOTIFICATION_UPDATE_FAIL,
                data=serializer.errors
            )

    def create(self, request, *args, **kwargs):
        """
        Endpoint to create a new Notification.
        """
        serializer = self.get_serializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            _, notification = serializer.save()
            return create_response(
                success=True, message=NOTIFICATION_CREATION_SUCCESS,
                data=NotificationRetrieveSerializer(notification).data
            )
        return create_response(message=NOTIFICATION_CREATION_FAILED, data=serializer.errors)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(queryset=self.get_queryset())
        if not queryset:
            return create_response(success=True, message=NOTIFICATIONS_FETCHED_SUCCESS, data=[])

        page = request.GET.get('page')
        if page:
            queryset = self.paginate_queryset(queryset)
            queryset = sorted(queryset, key=lambda notification: notification.status)

        serializer = self.get_serializer(queryset, context=self.get_serializer_context(), many=True)

        if page:
            serializer = self.get_paginated_response(data=serializer.data)
        return create_response(success=True, message=NOTIFICATIONS_FETCHED_SUCCESS, data=serializer.data)

    def filter_queryset(self, queryset=None):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, view=self)
        return queryset


class EmailHistoryViewSet(ModelViewSet):
    permission_classes = [AllowAny]
    authentication_classes = []

    def create(self, request, *args, **kwargs) -> Response:
        response = mailgun_webhook_task.apply_async(
            kwargs={'mg_payload': request.data}, eta=now() + timedelta(seconds=1))
        return create_response(success=True, message='Email status changed.')
