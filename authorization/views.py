from django.shortcuts import render
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from authorization.db_interactors import get_all_roles
from authorization.models import Role
from authorization.permissions import CanManageRole
from authorization.serializers import RoleListSerializer, RoleDetailSerializer, RoleUpdateSerializer, \
    PartialRoleUpdateSerializer
from utils.db_interactors import get_record_by_filters
from utils.helpers import create_response
from authorization.role_list import BUYER, SUPPLIER, DISTRIBUTOR, ADMIN, TRADEPRONTO_ADMIN


# TODO: Need to fully implement all the endpoints
class RoleViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
    viewsets.GenericViewSet):
    """
    ViewSet to manage role related endpoints
    """
    permission_classes = [CanManageRole]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ('name', 'label')
    ordering_fields = ['name']
    ordering = ['name']

    def get_object(self):
        pass

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Role.objects.none()
        if self.request.user.is_authenticated and self.request.user.is_prepstudy_admin() and self.action == 'list':
            return get_all_roles()
        elif self.action == 'corporate_role':
            return get_record_by_filters(model=Role, filters={"name__in": [MANAGER['name'], SUBJECT_MATTER_EXPERT['name'], HR_HEAD['name'], \
                                                    HR_PERSONNEL['name'], BRANCH_ADMIN['name'], CORPORATE_ADMIN['name'], \
                                                    INTERNAL_CANDIDATE['name'], EXTERNAL_CANDIDATE['name']]})
        elif self.action == 'v2_role':
            return get_record_by_filters(model=Role, filters={"name__in": [STUDENT['name'], TEACHER['name'], PARENT['name'], \
                                                    ADMIN['name'], PREPSTUDY_ADMIN['name']]})

        elif self.request.user.is_institute_admin():
            return get_roles_by_institute(self.request.user.institute())
        return None
    
    def filter_queryset(self, queryset=None):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, view=self)
        return queryset

    def get_serializer_class(self):
        if self.action in ['list', 'corporate_role', 'v2_role']:
            return RoleListSerializer
        elif self.action == 'retrieve':
            return RoleDetailSerializer
        elif self.action in ['update', 'partial_update']:
            if self.request.user.is_prepstudy_admin():
                return RoleUpdateSerializer
            else:
                return PartialRoleUpdateSerializer


    def update(self, request, *args, **kwargs):
        response = {
            'status': 'ERROR',
            'message': 'Method Not Allowed'
        }
        return Response(response, status=status.HTTP_405_METHOD_NOT_ALLOWED)


    @action(detail=False, methods=['get'], url_name='corporate', url_path='corporate')
    def corporate_role(self, request, *args, **kwargs):
        status, role_queryset = self.get_queryset()
        if not status:
            return create_response(message=role_queryset)
        role_queryset = self.filter_queryset(queryset=role_queryset)
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(role_queryset, many=True)
        return create_response(success=True, message=CORPORATE_ROLE_FETCHED, data=serializer.data)
    
    @action(detail=False, methods=['get'], url_name='v2', url_path='v2')
    def v2_role(self, request, *args, **kwargs):
        status, role_queryset = self.get_queryset()
        if not status:
            return create_response(message=role_queryset)
        role_queryset = self.filter_queryset(queryset=role_queryset)
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(role_queryset, many=True)
        return create_response(success=True, message=V2_ROLE_FETCHED, data=serializer.data)