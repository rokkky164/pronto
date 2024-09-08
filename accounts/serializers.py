from collections import OrderedDict
from logging import getLogger

from django.contrib.auth import password_validation, authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import Serializer, ModelSerializer, CharField, ChoiceField, IntegerField, EmailField, \
    SlugRelatedField, FileField, ListField
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.constants import (
    PROVIDED_ROLE_DOES_NOT_EXIST, EITHER_MOBILE_OR_EMAIL_REQUIRED, INVALID_CURRENT_PASSWORD, USER_OBJECT_NOT_PROVIDED,
    BOTH_PASSWORD_MUST_SAME, INCORRECT_EMAIL, USER_NOT_PROVIDED_IN_SERIALIZER_CONTEXT, INVALID_VERIFICATION_CODE,
    USERNAME_IS_REGISTERED, VERIFICATION_CODE_EXPIRED, VERIFICATION_CODE_ALREADY_USED,
    CITY_STATE_SHOULD_BE_PROVIDED_WHEN_UPDATING_THE_COUNTRY, CITY_SHOULD_BE_PROVIDED_WHEN_UPDATING_THE_STATE,
    COUNTRY_STATE_CITY_HIERARCHY_DO_NOT_MATCH, EITHER_USERNAME_AND_PASSWORD_OR_AUTH_CODE_REQUIRED, INVALID_CREDENTIALS,
    INVALID_MOBILE_NUMBER, INACTIVATED_ACCOUNT,
    NEW_PASSWORD_SAME_AS_CURRENT_PASSWORD, EMAIL_IS_REGISTERED, NUMBER_IS_REGISTERED
)
from accounts.models import User, Address, CompanyInformation, AccountManager, CertificateDocument, DeleteUserAccountRequest
from accounts.tasks import check_and_update_user_delete_request_task, initiate_account_verification
from accounts.utils import match_re, generate_username
from accounts.db_interactors import db_update_password
from authorization.role_list import (
    BUYER, SUPPLIER, DISTRIBUTOR, ADMIN, TRADEPRONTO_ADMIN
)
from authorization.models import Role, UserSession, UserEnvironmentDetails
from authorization.serializers import RoleListSerializer
from common.location.models import City, State, Country
from common.location.serializers import CitySerializer, StateSerializer, CountrySerializer
from utils.helpers import get_hostname_from_request
from utils.db_interactors import get_record_by_id, get_single_record_by_filters, db_create_record, get_record_by_filters, \
    db_filter_query_set

logger = getLogger(__name__)


class CompanyInformationSerializer(ModelSerializer):
    
    class Meta:
        model = CompanyInformation
        fields = ('name', 'tax_id', 'annual_turnover', 'hq_location', 'other_hubs', 'company_type',
                  'product_categories', 'vat_payer', 'legal_address'
                )

    def create(self, validated_data):
        status, company_information = db_create_record(
            model=CompanyInformation,
            data={
                'name': validated_data['name'],
                'tax_id': validated_data['tax_id'],
                'annual_turnover': validated_data['annual_turnover'],
                'hq_location': validated_data['hq_location'],
                'company_type': validated_data['company_type'],
                'other_hubs': validated_data['other_hubs'],
                'product_categories': validated_data['product_categories'],
                'vat_payer': validated_data['vat_payer'],
                'legal_address': validated_data['legal_address']
            }
        )
        return status, company_information


class AccountManagerSerializer(Serializer):
    first_name = CharField(required=True)
    last_name = CharField(required=True)
    email = CharField(required=True)
    phone = CharField(required=True)
    role = CharField(required=True)
    title = CharField(required=True)
    department = CharField(required=True)

    def validate(self, attrs):
        if User.objects.filter(email=attrs['email']).exists():
            raise ValidationError(f"User with this mail id {attrs['email']} already exists.")
        return attrs
    
    def create(self, validated_data):
        _, role = get_single_record_by_filters(model=Role, filters={'name': validated_data['role']})
        status, user = db_create_record(
            model=User,
            data={
                'first_name': validated_data['first_name'],
                'last_name': validated_data['last_name'],
                'email': validated_data['email'],
                'mobile_number': validated_data['phone'],
                'role': role,
                'username': generate_username(validated_data['first_name'], validated_data['last_name'], validated_data['email'])
            }
        )
        account_manager_status, account_manager = db_create_record(
            model=AccountManager,
            data={
                'user': user,
                'title': validated_data['title'],
                'department': validated_data['department']
            }
        )
        return account_manager_status, account_manager


class AccountManagerDetailsSerializer(ModelSerializer):
    first_name = CharField(source='user.first_name', read_only=True)
    last_name = CharField(source='user.last_name', read_only=True)
    email = CharField(source='user.email', read_only=True)
    phone = CharField(source='user.mobile_number', read_only=True)
    role = CharField(source='user.role.name', read_only=True)
    
    class Meta:
        model = AccountManager
        fields = ('first_name', 'last_name', 'email', 'phone', 'role', 'title', 'department')


# class CertificateDocumentSerializer(ModelSerializer):
    
#     class Meta:
#         model = CertificateDocument
#         fields = ('name', 'document_no', 'document', 'status')




class PasswordSetSerializer(serializers.Serializer):
    """
    Serializer to save new password for user
    """
    email = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, attrs):
        if not attrs.get('password') == attrs.get('confirm_password'):
            raise serializers.ValidationError(BOTH_PASSWORD_MUST_SAME)
        user_status, user = get_single_record_by_filters(model=User, filters={'email': attrs['email']})
        attrs['user'] = user
        if not user:
            raise ValueError(USER_OBJECT_NOT_PROVIDED)

        password = attrs.get('password')
        errors = dict()

        try:
            password_validation.validate_password(password=password, user=user)
        except ValidationError as e:
            errors['password'] = list(e.messages)

        if errors:
            raise serializers.ValidationError(errors)

        return attrs

    def create(self, validated_data):
        validated_data['user'].set_password(validated_data['password'])
        validated_data['user'].save()
        # send mail to user for account verification
        initiate_account_verification.delay(validated_data['user'].id)
        return True, validated_data['user']


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer to save new password for user
    """
    old_password = serializers.CharField(
        required=True
    )
    new_password = serializers.CharField(
        required=True
    )
    confirm_password = serializers.CharField(
        required=True
    )

    def validate_current_password(self, value):
        user = self.context.get('user')
        if not user.check_password(value):
            raise serializers.ValidationError(INVALID_CURRENT_PASSWORD)
        return value

    def validate(self, attrs):
        if attrs.get('new_password') != attrs.get('confirm_password'):
            raise serializers.ValidationError(BOTH_PASSWORD_MUST_SAME)
        
        if attrs.get('old_password') == attrs.get('new_password'):
            raise serializers.ValidationError(NEW_PASSWORD_SAME_AS_CURRENT_PASSWORD)

        # Temporary Commented
        # if attrs.get('current_password') == attrs.get('password_1'):
        #     raise serializers.ValidationError(NEW_PASSWORD_SAME_AS_CURRENT_PASSWORD)

        user = self.context.get('user')
        if not user:
            raise ValueError(USER_OBJECT_NOT_PROVIDED)

        password = attrs.get('new_password')
        errors = dict()

        try:
            password_validation.validate_password(password=password, user=user)
        except ValidationError as e:
            errors['password'] = list(e.messages)

        if errors:
            raise serializers.ValidationError(errors)

        return attrs

    def create(self, validated_data):
        user = self.context.get('user')

        if not user:
            raise ValueError(USER_OBJECT_NOT_PROVIDED)
        return db_update_password(user, validated_data['new_password'])


class PasswordResetSerializer(serializers.Serializer):
    """
    Serializer used for password reset flow initialisation
    """
    email = serializers.EmailField(
        required=True
    )

    def validate_email(self, value):
        user = get_user_by_email(value)

        if not user:
            raise serializers.ValidationError(INCORRECT_EMAIL)

        self.context.update({'user': user})

        return value

    def create(self, validated_data):
        user = self.context.get('user')
        if not user:
            raise ValueError(USER_NOT_PROVIDED_IN_SERIALIZER_CONTEXT)

        return create_password_reset_request_service(user=user)


class PasswordVerifySerializer(serializers.Serializer):
    """
    Serializer to save new password for user
    """
    verification_code = serializers.CharField(required=True)

    password_1 = serializers.CharField(
        required=True
    )
    password_2 = serializers.CharField(
        required=True
    )

    def validate_verification_code(self, value):
        password_reset_request = get_password_reset_request_by_code(verification_code=value)

        if not password_reset_request:
            raise serializers.ValidationError(INVALID_VERIFICATION_CODE)

        if password_reset_request.is_expired:
            raise serializers.ValidationError(VERIFICATION_CODE_EXPIRED)

        if password_reset_request.is_password_reset:
            raise serializers.ValidationError(VERIFICATION_CODE_ALREADY_USED)

        self.context.update({'password_reset_request': password_reset_request})
        self.context.update({'user': password_reset_request.user})

        return value

    def validate(self, attrs):
        if not attrs.get('password_1') == attrs.get('password_2'):
            raise serializers.ValidationError(BOTH_PASSWORD_MUST_SAME)

        user = self.context.get('user')
        if not user:
            raise ValueError(USER_OBJECT_NOT_PROVIDED)

        password = attrs.get('password_1')
        errors = dict()

        try:
            password_validation.validate_password(password=password, user=user)
        except ValidationError as e:
            errors['password'] = list(e.messages)

        if errors:
            raise serializers.ValidationError(errors)

        return attrs

    def create(self, validated_data):
        password_reset_request = self.context.get('password_reset_request')
        return update_password_reset_request_service(
            password_reset_request=password_reset_request, password=validated_data['password_1']
        )


class UserAddressSerializer(serializers.ModelSerializer):
    city = CitySerializer()
    state = StateSerializer()
    country = CountrySerializer()

    class Meta:
        model = Address
        fields = '__all__'
        extra_kwargs = {'user': {'write_only': True}}


class UserAddressCreateSerializer(serializers.ModelSerializer):
    city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all())
    state = serializers.PrimaryKeyRelatedField(queryset=State.objects.all())
    country = serializers.PrimaryKeyRelatedField(queryset=Country.objects.all())

    class Meta:
        model = Address
        fields = '__all__'

    def validate(self, attrs):
        country = attrs.get('country')
        state = attrs.get('state')
        city = attrs.get('city')
        # Check Country, State and City hierarchy
        if city.state != state or state.country != country:
            raise serializers.ValidationError(COUNTRY_STATE_CITY_HIERARCHY_DO_NOT_MATCH)
        return attrs


class UserAddressUpdateSerializer(serializers.ModelSerializer):
    address_line_1 = serializers.CharField(max_length=50, required=False)
    address_line_2 = serializers.CharField(max_length=50, required=False, allow_blank=True)
    city = serializers.PrimaryKeyRelatedField(required=False, queryset=City.objects.all())
    state = serializers.PrimaryKeyRelatedField(required=False, queryset=State.objects.all())
    country = serializers.PrimaryKeyRelatedField(required=False, queryset=Country.objects.all())
    pincode = serializers.IntegerField(required=False)

    class Meta:
        fields = "__all__"
        model = Address

    def validate(self, attrs):
        # check if country state and city hierarchy is correct
        if attrs.get('country') and not (attrs.get('city') or attrs.get('state')):
            raise serializers.ValidationError(CITY_STATE_SHOULD_BE_PROVIDED_WHEN_UPDATING_THE_COUNTRY)
        if attrs.get('state') and not attrs.get('city'):
            raise serializers.ValidationError(CITY_SHOULD_BE_PROVIDED_WHEN_UPDATING_THE_STATE)

        # Get new or current Country, State and City
        user_current_address = self.context['user'].address
        country = attrs.get('country') or user_current_address.country
        state = attrs.get('state') or user_current_address.state
        city = attrs.get('city') or user_current_address.city
        # Check Country, State and City hierarchy
        if city.state != state or state.country != country:
            raise serializers.ValidationError(COUNTRY_STATE_CITY_HIERARCHY_DO_NOT_MATCH)

        return attrs

    def to_representation(self, instance):
        result = super().to_representation(instance)
        return OrderedDict([(key, result[key]) for key in result if result[key] is not None])


class CustomLoginSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True, required=False)
    password = serializers.CharField(
        write_only=True, required=False, style={'input_type': 'password', 'placeholder': 'Password'}
    )
    auth_code = serializers.CharField(write_only=True, required=False)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        auth_code = attrs.get('auth_code')

        if not (username and password) and not auth_code:
            raise serializers.ValidationError(EITHER_USERNAME_AND_PASSWORD_OR_AUTH_CODE_REQUIRED)

        user = None
        if username and password:
            filters = {}
            if '@' in username:
                filters['email'] = username
            else:
                filters['username'] = username
            user = User.objects.filter(**filters).last()
            if not user or not user.check_password(password):
                user = None
        elif auth_code:
            user = authenticate(auth_code=auth_code, is_deleted=False)

        if not user:
            raise serializers.ValidationError(INVALID_CREDENTIALS)
        elif not user.is_active:
            raise serializers.ValidationError(INACTIVATED_ACCOUNT)

        attrs['user_id'] = user.id
        return attrs

    def create(self, validated_data):
        _, user = get_record_by_id(model=User, _id=validated_data['user_id'])
        refresh = RefreshToken.for_user(user)
        check_and_update_user_delete_request_task.apply_async(kwargs={'user_id': user.pk}, eta=now())
        return {'access': str(refresh.access_token), 'refresh': str(refresh), 'user': user}


class CustomTokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)
    access = serializers.CharField(read_only=True)

    def validate(self, attrs):
        refresh = RefreshToken(attrs['refresh'])

        data = {'access': str(refresh.access_token), 'refresh': str(refresh)}

        if api_settings.ROTATE_REFRESH_TOKENS:
            if api_settings.BLACKLIST_AFTER_ROTATION:
                try:
                    # Attempt to blacklist the given refresh token
                    refresh.blacklist()
                except AttributeError:
                    # If blacklist app not installed, `blacklist` method will
                    # not be present
                    pass

            refresh.set_jti()
            refresh.set_exp()
            refresh.set_iat()

            data['refresh'] = str(refresh)

        return data


class UserSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSession
        fields = '__all__'


class UserEnvironmentDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserEnvironmentDetails
        fields = '__all__'

    def create(self, validated_data):
        status, user_env_details = create_user_env_details_service(**validated_data)
        if not status:
            raise ValidationError(user_env_details)
        return status, user_env_details


class UserNameSerializer(ModelSerializer):
    photo = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'photo', 'mobile_number']

    def get_photo(self, obj):
        return f'/media/{obj.photo}' if obj.photo else None


class LoginDetailSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    def get_role(self, obj):
        if obj.role:
            return obj.role.label
        return None

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'mobile_number', 'first_name', 'last_name', 'role', 'gender', 'dob',
            'photo', 'is_active'
        )


class ValidateDeleteAccountRequestSerializer(ModelSerializer):
    class Meta:
        model = DeleteUserAccountRequest
        fields = ['reason']

    def create(self, validated_data):
        validated_data['user'] = self.context.get('request').user
        return delete_user_account_request_service(**validated_data)


class SendDeleteRequestSerializer(ModelSerializer):
    email = EmailField(required=True)

    class Meta:
        model = DeleteUserAccountRequest
        fields = ['reason', 'email']

    def create(self, validated_data):
        validated_data['user'] = self.context.get('user')
        validated_data['hostname'] = self.context.get('hostname')
        validated_data.pop('email')
        return send_delete_account_request_service(**validated_data)


class CertificateDocumentSerializer(Serializer):
    certificates = ListField(child=FileField(required=True), min_length=0, max_length=5)
    videos = ListField(child=FileField(required=True), min_length=0, max_length=5)

    def create(self, validated_data):
        certificate_document = None
        videos = None
        for each_file in validated_data['certificates']:
            status, certificate_document = db_create_record(
                model=CertificateDocument,
                data={
                    'name': each_file.name,
                    'document': each_file
                }
            )
        for each_file in validated_data['videos']:
            status, videos = db_create_record(
                model=CertificateDocument,
                data={
                    'name': each_file.name,
                    'document': each_file
                }
            )
        if certificate_document:
            return certificate_document
        if videos:
            return videos
