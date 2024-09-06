import logging

from django.db.models import Q
from django.db.transaction import atomic, set_rollback
from django.utils import timezone
from django.utils.timezone import now
from django_filters import rest_framework
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import generics, views, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ViewSet

from accounts.constants import (
    COMPANY_INFORMATION_CREATION_SUCCESS,
    COMPANY_INFORMATION_CREATION_FAILED,
    COMPANY_INFORMATION_FETCH_SUCCESS,
    COMPANY_INFORMATION_NOT_FOUND,
    ACCOUNT_MANAGER_CREATION_SUCCESS,
    ACCOUNT_MANAGER_CREATION_FAILED,
    ACCOUNT_MANAGER_FETCH_SUCCESS,
    ACCOUNT_MANAGER_NOT_FOUND,
    USER_UPDATE_SUCCESS,
    USER_LIST_FETCH_SUCCESS,
    USER_DETAIL_FETCH_SUCCESS,
    USER_NOT_FOUND,
    PIN_CODE_LIST_FETCH_SUCCESS,
    LOGIN_SUCCESS,
    AUTHENTICATION_CODE_SEND_SUCCESS,
    EMAIL_CHANGE_SUCCESS,
    PASSWORD_CHANGE_SUCCESS,
    EMAIL_CHANGE_REQUEST_CREATE_SUCCESS,
    PASSWORD_RESET_REQUEST_SENT_SUCCESS,
    ACTIVATED_ACCOUNT_SUCCESS,
    ACCESS_TOKEN_RENEWED_SUCCESS,
    PASSWORD_RESET_REQUEST_FAILED,
    FAILED_TO_RENEW_ACCESS_TOKEN,
    PASSWORD_CHANGE_FAILED,
    INVALID_VERIFICATION_CODE,
    VERIFICATION_CODE_REQUIRED,
    VERIFICATION_CODE_ALREADY_USED,
    INVALID_DATA,
    UNABLE_TO_CREATE_EMAIL_CHANGE_REQUEST,
    EXPECTED_VERIFICATION_CODE_AS_QUERY_PARAMETER,
    INVALID_OR_EXPIRED_VERIFICATION_CODE,
    USER_NOT_FOUND_WITH_GIVEN_MAIL_ID,
    VERIFICATION_CODE_EXPIRED,
    UNABLE_TO_SEND_MAIL_FOR_REGISTRATION,
    PROVIDED_ROLE_DOES_NOT_EXIST,
    USER_CREDS_SENT_SUCCESS,
    USER_BY_EMAIL_URL,
    USER_BY_EMAIL_URL_NAME,
    USER_BY_EMAIL_FETCH_SUCCESS, DELETE_ACCOUNT_REQUEST_URL, DELETE_ACCOUNT_REQUEST_URL_NAME,
    DELETE_USER_ACCOUNT_REQUEST_SUCCESS, SEND_DELETE_REQUEST_EMAIl_URL, SEND_DELETE_REQUEST_EMAIl_URL_NAME,
    SEND_DELETE_REQUEST_EMAIL_SUCCESS,
    UPLOAD_CERTIFICATE_URL_NAME,
    UPLOAD_CERTIFICATE_URL,
    UPLOAD_CERTIFICATE_SUCCESS,
    UPLOAD_CERTIFICATE_FAIL
)
# from accounts.filtersets import UserFilterSet
from accounts.utils import get_device_type
# from accounts.db_interactors import (
#     db_get_verification_request,
#     db_get_user_list,
# )
from accounts.models import (
    User, DeleteUserAccountRequest, CompanyInformation, AccountManager
)
from accounts.permissions import UserPermission, CanChangeEmail, IsActive
from accounts.serializers import (
    CompanyInformationSerializer,
    AccountManagerSerializer,
    AccountManagerDetailsSerializer,
    PasswordChangeSerializer,
    PasswordResetSerializer,
    PasswordVerifySerializer,
    PasswordSetSerializer,
    CustomLoginSerializer,
    CustomTokenRefreshSerializer,
    UserSessionSerializer,
    UserEnvironmentDetailsSerializer,
    LoginDetailSerializer
)
from accounts.tasks import resend_verification_code, initiate_account_verification, set_user_environment_session

from authorization.role_list import BUYER, SUPPLIER, DISTRIBUTOR, ADMIN, TRADEPRONTO_ADMIN
from authorization.db_interactors import get_role_by_name, get_verification_code_by_user_id

from utils.helpers import create_response, load_request_json_data, get_hostname_from_request
from utils.db_interactors import (
    get_record_by_id, db_update_instance, db_get_empty_queryset, db_get_object_list, get_record_by_filters,
    get_single_record_by_filters
)
from utils.paginations import StandardResultsSetPagination

logger = logging.getLogger(__name__)


class CompanyInformationView(generics.GenericAPIView):
    queryset = CompanyInformation.objects.all()
    permission_classes = (AllowAny,)
    authentication_classes = []
    serializer_class = CompanyInformationSerializer

    def get_object(self, *args, **kwargs):
        return get_record_by_id(model=CompanyInformation, _id=self.kwargs.get('company_info_id'))

    def get(self, request, *args, **kwargs):
        """
        View to get company info details
        """
        status, company_information = self.get_object(*args, **kwargs)
        if not status:
            return create_response(message=COMPANY_INFORMATION_NOT_FOUND)
        serializer = self.get_serializer(instance=company_information)
        return create_response(success=True, message=COMPANY_INFORMATION_FETCH_SUCCESS, data=serializer.data)
    
    @atomic()
    def post(self, request, *args, **kwargs):
        request_data = request.data.copy()
        hostname = request.headers.get('origin', None)
        hostname = hostname.split('//')[-1] if hostname else request.get_host()
        serializer = self.serializer_class(data=request_data, context={'host_name': hostname})
        if serializer.is_valid():
            status, company_information = serializer.save()
            if not status:
                set_rollback(True)
                return create_response(message=COMPANY_INFORMATION_CREATION_FAILED, data=company_information)

            return create_response(success=True, message=COMPANY_INFORMATION_CREATION_SUCCESS, data=serializer.validated_data)
        else:
            return create_response(message=COMPANY_INFORMATION_CREATION_FAILED, data=serializer.errors)


class AccountManagerDetailsView(generics.GenericAPIView):
    queryset = AccountManager.objects.all()
    permission_classes = (AllowAny,)
    authentication_classes = []
    serializer_class = AccountManagerSerializer

    def get_object(self, *args, **kwargs):
        return get_record_by_id(model=AccountManager, _id=self.kwargs.get('manager_id'))

    def get(self, request, *args, **kwargs):
        """
        View to get Account Manager details
        """
        status, account_manager = self.get_object(*args, **kwargs)
        if not status:
            return create_response(message=ACCOUNT_MANAGER_NOT_FOUND)
        serializer = AccountManagerDetailsSerializer(instance=account_manager)
        return create_response(success=True, message=ACCOUNT_MANAGER_FETCH_SUCCESS, data=serializer.data)

    @atomic()
    def post(self, request, *args, **kwargs):
        request_data = request.data.copy()
        hostname = request.headers.get('origin', None)
        hostname = hostname.split('//')[-1] if hostname else request.get_host()
        request_data = {
            'first_name': request_data['first_name'],
            'last_name': request_data['last_name'],
            'email': request_data['email'],
            'phone': request_data['phone'],
            'role': request_data['role'],
            'title': request_data['title'],
            'department': request_data['department']
        }
        serializer = self.serializer_class(data=request_data, context={'host_name': hostname})
        if serializer.is_valid():
            status, account_manager = serializer.save()
            if not status:
                set_rollback(True)
                return create_response(message=ACCOUNT_MANAGER_CREATION_FAILED, data=account_manager)
            return create_response(success=True, message=ACCOUNT_MANAGER_CREATION_SUCCESS, data=serializer.validated_data)
        else:
            return create_response(message=ACCOUNT_MANAGER_CREATION_FAILED, data=serializer.errors)


class AccountVerifyView(generics.GenericAPIView):
    permission_classes = [AllowAny, ]
    authentication_classes = []

    def get_object(self, *args, **kwargs):
        verification_code = kwargs.get('verification_code', None)
        if verification_code:
            status, obj = db_get_verification_request(verification_code)
            if not status:
                return False, INVALID_VERIFICATION_CODE
            return True, obj
        return False, VERIFICATION_CODE_REQUIRED

    def get(self, request, *args, **kwargs):
        """
        View to activate user account
        """
        status, account_verification_request = self.get_object(*args, **kwargs)
        if not status:
            return create_response(message=account_verification_request)

        if account_verification_request.is_expired:
            return create_response(message=VERIFICATION_CODE_EXPIRED)

        elif account_verification_request.is_account_verified:
            return create_response(message=VERIFICATION_CODE_ALREADY_USED)

        data = {'verified_at': timezone.now(), 'is_account_verified': True}
        status, update_request = db_update_instance(instance=account_verification_request, data=data)
        if not status:
            return create_response(message=status)
        data = {'is_email_verified': True, 'is_active': True}
        status, update_user = db_update_instance(instance=account_verification_request.user, data=data)
        if not status:
            return create_response(message=status)

        return create_response(success=True, message=ACTIVATED_ACCOUNT_SUCCESS)


class PasswordViewSet(ViewSet):
    """
    View to reset password for authenticated and anonymous users
    """

    @action(detail=False, url_path='change', methods=['post'], permission_classes=[IsAuthenticated, IsActive])
    def change(self, request):
        """
        Method which changes password for authenticated user
        """
        serializer = PasswordChangeSerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            status, change_password = serializer.save()
            if not status:
                return create_response(message=change_password)
            return create_response(success=True, message=PASSWORD_CHANGE_SUCCESS)

        else:
            return create_response(message=PASSWORD_CHANGE_FAILED, data=serializer.errors)

    @atomic()
    @action(detail=False, url_path='reset', methods=['post'], permission_classes=[AllowAny], authentication_classes=[])
    def reset(self, request):
        """
        Method which initiates password reset flow for anonymous user
        """
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            status, password_resset_request = serializer.save()
            if not status:
                return create_response(message=password_resset_request)
            return create_response(success=True, message=PASSWORD_RESET_REQUEST_SENT_SUCCESS)

        else:
            return create_response(message=PASSWORD_RESET_REQUEST_FAILED, data=serializer.errors)

    @atomic()
    @action(detail=False, url_path='verify', methods=['post'], permission_classes=[AllowAny], authentication_classes=[])
    def verify(self, request):
        """
        Method which verifies and sets the new password for anonymous user
        """
        serializer = PasswordVerifySerializer(data=request.data, context={'user': request.user})
        if serializer.is_valid():
            status, reset_password = serializer.save()
            if not status:
                return create_response(message=reset_password)
            return create_response(success=True, message=PASSWORD_CHANGE_SUCCESS)

        else:
            return create_response(message=PASSWORD_CHANGE_FAILED, data=serializer.errors)

    @atomic()
    @action(detail=False, url_path='set-password', methods=['post'], permission_classes=[AllowAny], authentication_classes=[])
    def set(self, request):
        """
        Method which verifies and sets the new password for anonymous user
        """
        serializer = PasswordSetSerializer(data=request.data)
        if serializer.is_valid():
            status, set_password = serializer.save()
            if not status:
                return create_response(message=set_password)
            return create_response(success=True, message=PASSWORD_CHANGE_SUCCESS)

        else:
            return create_response(message=PASSWORD_CHANGE_FAILED, data=serializer.errors)


class UserViewSet(
    mixins.ListModelMixin, viewsets.GenericViewSet
):
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, UserPermission, ]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # filterset_class = UserFilterSet
    ordering_fields = ['first_name', 'id']
    ordering = ['-id']
    search_fields = [
        'first_name',
        'last_name'
    ]

    def get_object(self):
        if self.action == 'user_by_email':
            filters = Q(email=self.request.GET.get('email'))
            if self.request.GET.get('role'):
                filters &= Q(role__name=self.request.GET.get('role'))
            return get_single_record_by_filters(model=User, filters=filters, q_filtering=True)
        elif self.action == 'delete_account_request':
            return get_single_record_by_filters(model=DeleteUserAccountRequest,
                                                filters={'identifier': self.request.GET.get('uid'),
                                                         'is_logged_in': False,
                                                         'is_account_deleted': False})
        elif self.action == 'send_delete_email_request':
            return get_record_by_filters(model=User, filters={
                'email': self.request.data.get('email'),
                'is_deleted': False
            })
        return get_record_by_id(model=User, _id=self.kwargs.get('pk'))

    def get_serializer_class(self):
        if self.action == 'list':
            return UserShortDetailSerializer
        elif self.action in ['retrieve', 'user_by_email']:
            return UserDetailSerializer
        elif self.action == 'update':
            return UserUpdateSerializer
        elif self.action == 'change_email':
            return EmailChangeRequestSerializer
        elif self.action == 'send_delete_email_request':
            return SendDeleteRequestSerializer

        # short-circuit for swagger
        else:
            return UserShortDetailSerializer

    def get_queryset(self, is_active: bool = None, is_deleted: bool = None, get_undeleted_users: bool = None):
        if getattr(self, 'swagger_fake_view', False):
            return User.objects.none()
        if self.action == 'list':
            return db_get_user_list(
                self.request.user,
                is_active=is_active,
                is_deleted=is_deleted,
                get_undeleted_users=get_undeleted_users,
                branch_id=self.request.GET.get('branch_id', None),
                exclude_self=self.request.GET.get('exclude_self', None),
                exclude_batch=self.request.GET.get('exclude_batch', None),
                search=self.request.GET.get('search')
            )
        elif self.action == 'student_grades':
            return get_student_grade_by_user(self.request.user, student_id=self.request.GET.get('student'))
        elif self.action == 'user_exam_types':
            return get_user_exam_type(self.request.user, student_id=self.request.GET.get('student'))
        elif self.action == 'student_dropdown_list':
            include_self = self.request.GET.get('include_self', None)
            return get_all_students(user=self.request.user, include_self=include_self, 
                                    search=self.request.GET.get('search', None))

    def list(self, request, *args, **kwargs):
        page = request.GET.get('page')
        is_active = request.GET.get('is_active', True)
        is_deleted = request.GET.get('is_deleted', False)

        get_undeleted_users = request.GET.get('get_undeleted_users', False)
        queryset = self.filter_queryset(
            self.get_queryset(is_active=is_active, is_deleted=is_deleted, get_undeleted_users=get_undeleted_users)
        )
        if page:
            queryset = self.paginate_queryset(queryset)
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(queryset, many=True)
        if page:
            serializer = self.get_paginated_response(serializer.data)
        return create_response(success=True, message=USER_LIST_FETCH_SUCCESS, data=serializer.data)

    def retrieve(self, request, *args, **kwargs):
        status, user = self.get_object()
        if not status:
            return create_response(message=USER_NOT_FOUND)
        if user:
            serializer_class = self.get_serializer_class()
            return create_response(success=True, message=USER_DETAIL_FETCH_SUCCESS, data=serializer_class(user).data)
        else:
            return create_response(message=USER_NOT_FOUND)

    @atomic()
    def update(self, request, *args, **kwargs):
        status, user = self.get_object()
        if not status:
            return create_response(message=user)

        request_data = load_request_json_data(
            request_data=request.data, json_key_list=['departments', 'educations', 'address'])

        if 'photo' in request_data and not request_data['photo']:
            request_data['photo'] = None
        serializer = self.get_serializer(data=request_data, partial=True, context={'user': user})
        if serializer.is_valid():
            validated_data = serializer.validated_data
            validated_data['updated_by'] = request.user
            status, update_user = serializer.update(instance=user, validated_data=validated_data)
            if not status:
                set_rollback(True)
                return create_response(message=update_user)
            return create_response(
                success=True, message=USER_UPDATE_SUCCESS, data=UserDetailSerializer(update_user).data
            )
        else:
            return create_response(message=INVALID_DATA, data=serializer.errors)

    @action(methods=['post'], detail=True, url_path='change-email',
            permission_classes=[IsAuthenticated, IsActive, CanChangeEmail])
    def change_email(self, request, *args, **kwargs):
        """
        Endpoint to initiate email change request
        """
        status, user = self.get_object()
        if not status:
            return create_response(message=USER_NOT_FOUND)
        serializer = self.get_serializer(user, data=request.data, partial=True, context={'user': user})
        if serializer.is_valid():
            serializer.save()
            return create_response(success=True, message=EMAIL_CHANGE_REQUEST_CREATE_SUCCESS)
        else:
            return create_response(message=UNABLE_TO_CREATE_EMAIL_CHANGE_REQUEST, data=serializer.errors)

    @action(methods=['get'], detail=True, url_path='verify-email',
            permission_classes=[IsAuthenticated, IsActive, CanChangeEmail])
    def verify_email(self, request, *args, **kwargs):
        verification_code = request.query_params.get('verification_code')
        if not verification_code:
            return create_response(message=EXPECTED_VERIFICATION_CODE_AS_QUERY_PARAMETER)
        status, user = self.get_object()
        if not status:
            return create_response(message=USER_NOT_FOUND)
        # Verify verification code and change email
        status, ecr = verify_request_and_change_email_service(user=user, verification_code=verification_code)
        if not status:
            return create_response(message=INVALID_OR_EXPIRED_VERIFICATION_CODE)
        return create_response(success=True, message=EMAIL_CHANGE_SUCCESS)

    @action(detail=False, methods=['get'], url_path=USER_BY_EMAIL_URL, url_name=USER_BY_EMAIL_URL_NAME)
    def user_by_email(self, request, *args, **kwargs):
        status, user = self.get_object()
        if not status:
            return create_response(message=USER_NOT_FOUND)
        serializer = self.get_serializer(user)
        if user:
            return create_response(success=True, message=USER_BY_EMAIL_FETCH_SUCCESS, data=serializer.data)
        return create_response(success=True, message=USER_NOT_FOUND)

    @action(
        detail=False,
        methods=['delete'],
        url_path=DELETE_ACCOUNT_REQUEST_URL,
        url_name=DELETE_ACCOUNT_REQUEST_URL_NAME,
        permission_classes=[AllowAny]
    )
    def delete_account_request(self, request, *args, **kwargs):
        status, obj = self.get_object()
        if not status:
            return create_response(message=USER_NOT_FOUND)
        status, response = delete_user_account_request_service(obj)
        if not status:
            return create_response(message=response)
        return create_response(success=True, message=DELETE_USER_ACCOUNT_REQUEST_SUCCESS)

    @action(detail=False, methods=['post'], url_path=SEND_DELETE_REQUEST_EMAIl_URL,
            url_name=SEND_DELETE_REQUEST_EMAIl_URL_NAME, permission_classes=[AllowAny])
    def send_delete_email_request(self, request, *args, **kwargs):
        status, user = self.get_object()
        if not status:
            return create_response(message=user)
        elif not user:
            return create_response(message=USER_NOT_FOUND)
        hostname = get_hostname_from_request(request=request)
        serializer = self.get_serializer(data=request.data,
                                         context={'user': user.last(), 'hostname': hostname})
        if not serializer.is_valid():
            return create_response(message=serializer.errors)
        status, response = serializer.save()
        if not status:
            return create_response(message=response)
        return create_response(success=True, message=SEND_DELETE_REQUEST_EMAIL_SUCCESS)

    @action(detail=True ,methods=['post'], url_name=UPLOAD_CERTIFICATE_URL_NAME, url_path=UPLOAD_CERTIFICATE_URL)
    def upload_certs_n_videos(self, request, *args, **kwargs):
        serializer = CertificateDocumentSerializer(data=request.data, files=request.FILES)
        if serializer.is_valid():
            # TO DO

            return create_response(success=True, message=UPLOAD_CERTIFICATE_SUCCESS)
        return create_response(message=UPLOAD_CERTIFICATE_FAIL, data=serializer.errors)


class CustomLoginView(generics.GenericAPIView):
    serializer_class = CustomLoginSerializer
    permission_classes = [AllowAny, ]
    authentication_classes = []

    @atomic()
    def post(self, request, *args, **kwargs):
        # Assign batch to user
        bid = request.data.get('bid')
        iid = request.data.get('iid')
        is_corporate = request.data.get('is_corporate', False)
        open_batch_invitation = request.data.get('open_batch_invitation', False)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            data = serializer.save()
            user = data['user']
            # env_session_data = {
            #     'user_id': user.id,
            #     'os': request.user_agent.os.family,
            #     'os_version': request.user_agent.os.version_string,
            #     'ip_address': request.META.get('HTTP_X_FORWARDED_FOR'),
            #     'browser': request.user_agent.browser.family,
            #     'browser_version': request.user_agent.browser.version_string,
            #     'device_type': get_device_type(user_agent=request.user_agent),
            #     'device': request.user_agent.device.family,
            #     'token': data['refresh'],
            # }
            # set_user_environment_session.apply_async(kwargs=env_session_data, eta=now())

            data['user'] = LoginDetailSerializer(user).data
            return create_response(success=True, message=LOGIN_SUCCESS, data=data)
        return create_response(message=serializer.errors)


class CustomTokenRefreshView(generics.GenericAPIView):
    serializer_class = CustomTokenRefreshSerializer
    permission_classes = [AllowAny, ]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            if serializer.is_valid():
                return \
                    create_response(success=True, message=ACCESS_TOKEN_RENEWED_SUCCESS, data=serializer.validated_data)
            else:
                return create_response(message=FAILED_TO_RENEW_ACCESS_TOKEN, data=serializer.errors)
        except Exception as e:
            return create_response(message=FAILED_TO_RENEW_ACCESS_TOKEN, data={'refresh': e.args[0]})


class ResendVerificationCodeView(views.APIView):
    permission_classes = [AllowAny, ]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        """
        resend verification code to user
        """
        response = {}
        user = get_user_by_email(request.data.get('email'))
        if user:
            verification_obj = get_verification_code_by_user_id(user.id)
            if verification_obj:
                if verification_obj.is_expired:
                    initiate_account_verification.delay(user.id)
                    return create_response(success=True, message=AUTHENTICATION_CODE_SEND_SUCCESS)  # TODO: check once
                else:
                    resend_verification_code.delay(verification_obj.id)
                    return create_response(success=True, message=AUTHENTICATION_CODE_SEND_SUCCESS)  # TODO: check once
            else:
                initiate_account_verification.delay(user.id)
                return create_response(success=True, message=AUTHENTICATION_CODE_SEND_SUCCESS)
        else:
            return create_response(message=USER_NOT_FOUND_WITH_GIVEN_MAIL_ID)
