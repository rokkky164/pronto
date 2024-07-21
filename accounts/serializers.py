from collections import OrderedDict
from logging import getLogger

from django.contrib.auth import password_validation, authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer, CharField, ChoiceField, IntegerField, EmailField, \
    SlugRelatedField
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
# from accounts.db_interactors import (
#     get_user_by_email,
#     get_password_reset_request_by_code
# )
from accounts.models import User, Address, CompanyInformation, AccountManagerDetails, CertificateDocument, DeleteUserAccountRequest
# from accounts.services import (
#     create_user_env_details_service,
#     create_user_service,
#     change_password_service,
#     create_password_reset_request_service,
#     update_password_reset_request_service,
#     update_school_service, update_user_service,
#     create_change_email_request_service, delete_user_account_request_service, send_delete_account_request_service
# )
from accounts.tasks import check_and_update_user_delete_request_task
from accounts.utils import match_re
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
                  'product_categories', 'vat_payer', 'legal_address', 'district'
                )


class AccountManagerDetailsSerializer(ModelSerializer):
    
    class Meta:
        model = AccountManagerDetails
        fields = ('name', 'title', 'department', 'email', 'phone')


class CertificateDocumentSerializer(ModelSerializer):
    
    class Meta:
        model = CertificateDocument
        fields = ('name', 'document_no', 'document', 'status')


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=False,
        validators=[UniqueValidator(queryset=User.objects.filter(), message=EMAIL_IS_REGISTERED)]
    )
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.filter(), message=USERNAME_IS_REGISTERED)]
    )
    mobile_number = serializers.CharField(
        required=False,
        validators=[UniqueValidator(queryset=User.objects.filter(), message=NUMBER_IS_REGISTERED)]
    )
    role = serializers.SlugRelatedField(
        slug_field='name',
        required=True,
        queryset=Role.objects.filter(
            name__in=[BUYER['name'], SUPPLIER['name'], DISTRIBUTOR['name'], ADMIN['name'],
                      TRADEPRONTO_ADMIN['name']]),
        error_messages={'does_not_exist': PROVIDED_ROLE_DOES_NOT_EXIST}
    )

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    gender = serializers.ChoiceField(choices=User.Gender.choices, required=False)
    iid = serializers.UUIDField(required=False)
 
    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'mobile_number', 'first_name', 'last_name', 'role',
                  'gender', 'bid', 'status', 'grade', 'is_corporate', 'iid'
                  )
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': False}
        }

    def validate(self, attrs):
        grade = None

        # TODO: temp. commented validation. need to remove this comment
        # if attrs.get('role') and attrs.get('role').name == STUDENT['name'] and not attrs.get('grade'):
        #     raise ValidationError({'Grade/Degree': GRADE_FIELD_REQUIRED_STUDENT})

        if not attrs.get('email', None) and not attrs.get('mobile_number', None):
            raise serializers.ValidationError(EITHER_MOBILE_OR_EMAIL_REQUIRED)
        if attrs.get('grade'):
            grade = attrs['grade']
            del attrs['grade']
        # get the password from the data
        password = attrs.get('password')

        # pop batch invitation id and is_corporate from attrs and add into context
        self.context.update({'bid': attrs.pop('bid', None)})
        self.context.update({'is_corporate': attrs.pop('is_corporate', None)})
        self.context.update({'iid': attrs.pop('iid', None)})
        errors = dict()
        try:
            password_validation.validate_password(password=password, user=User(**attrs))
        except ValidationError as e:
            errors['password'] = list(e.messages)
        if errors:
            raise serializers.ValidationError(errors)
        attrs['grade'] = grade
        return attrs

    def create(self, validated_data):
        is_corporate = self.context.get('is_corporate', None)
        auto_activate = False if not is_corporate else True
        status, user = create_user_service(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            username=validated_data['username'],
            password=validated_data['password'],
            role=validated_data['role'],
            email=validated_data.get('email', ''),  # added blank email to overcome the null IntegrityError,
            mobile_number=validated_data.get('mobile_number'),
            gender=validated_data.get('gender'),
            status=validated_data.get('status'),
            grade=validated_data.get('grade'),
            is_active=auto_activate
        )
        return status, user


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer to save new password for user
    """
    current_password = serializers.CharField(
        required=True
    )
    password_1 = serializers.CharField(
        required=True
    )
    password_2 = serializers.CharField(
        required=True
    )

    def validate_current_password(self, value):
        user = self.context.get('user')
        if not user.check_password(value):
            raise serializers.ValidationError(INVALID_CURRENT_PASSWORD)
        return value

    def validate(self, attrs):
        if attrs.get('password_1') != attrs.get('password_2'):
            raise serializers.ValidationError(BOTH_PASSWORD_MUST_SAME)
        
        if attrs.get('current_password') == attrs.get('password_1'):
            raise serializers.ValidationError(NEW_PASSWORD_SAME_AS_CURRENT_PASSWORD)

        # Temporary Commented
        # if attrs.get('current_password') == attrs.get('password_1'):
        #     raise serializers.ValidationError(NEW_PASSWORD_SAME_AS_CURRENT_PASSWORD)

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
        user = self.context.get('user')

        if not user:
            raise ValueError(USER_OBJECT_NOT_PROVIDED)

        return change_password_service(user=user, password=validated_data['password_1'])


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


class UserDetailSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    address = UserAddressSerializer()

    section = serializers.CharField(source='student_profile.section.name', read_only=True)
    fathers_name = serializers.CharField(source='student_profile.fathers_name', read_only=True)
    mothers_name = serializers.CharField(source='student_profile.mothers_name', read_only=True)
    guardian_contact_number = serializers.CharField(source='student_profile.guardian_contact_number', read_only=True)
    total_gems = serializers.IntegerField(source='student_profile.total_gems', read_only=True, default=0)
    rank = serializers.IntegerField(source='student_profile.rank', read_only=True)
    daily_challenge = serializers.BooleanField(source='student_profile.daily_challenge', read_only=True)
    school = serializers.SerializerMethodField()

    qualification = serializers.CharField(source='teacher_profile.qualification', read_only=True)
    experience = serializers.IntegerField(source='teacher_profile.experience', read_only=True)
    current_student_count = serializers.IntegerField(source='teacher_profile.current_student_count', read_only=True)
    total_student_count = serializers.IntegerField(source='teacher_profile.total_student_count', read_only=True)
    area_of_expertise = serializers.CharField(source='teacher_profile.area_of_expertise', read_only=True)
    institute = serializers.SerializerMethodField(read_only=True)
    is_superteacher = serializers.BooleanField(source='teacher_profile.is_superteacher')
    badge = serializers.SerializerMethodField()

    #   Employees
    educations = SerializerMethodField()

    def get_role(self, obj):
        if obj.role:
            return obj.role.label
        return None

    def get_institute(self, obj):
        institute = obj.institute()
        if institute:
            return {'id': institute.id, 'name': institute.name, 'is_editable': False}
        return None

    def get_school(self, obj):
        if hasattr(obj, 'student_profile'):
            school = getattr(obj.student_profile, 'school')
            if school:
                return SchoolDetailUpdateSerializer(school).data
        return None

    @staticmethod
    def get_badge(obj):
        if obj.role and obj.role.name == STUDENT['name'] and hasattr(obj, 'student_profile'):
            return get_badge_by_gems(gems=obj.student_profile.total_gems)[-1]
        return None

    @staticmethod
    def get_educations(obj):
        if hasattr(obj, 'employee'):
            educations = db_filter_query_set(
                query_set=obj.employee.educations, filters={'status': Education.Status.ACTIVE})[1]
            return EducationDetailsSerializer(educations, many=True).data
        return None

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'mobile_number', 'first_name', 'last_name', 'role', 'gender', 'grade', 'dob',
            'section', 'fathers_name', 'mothers_name', 'guardian_contact_number', 'total_gems', 'rank', 'daily_challenge', 'school', 'qualification',
            'experience', 'current_student_count', 'total_student_count', 'area_of_expertise', 'is_superteacher',
            'institute', 'address', 'photo', 'avatar', 'thumbnail', 'has_completed_profile', 'status', 'is_active',
            'is_deleted', 'badge', 'educations'
        )


class CustomLoginSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True, required=False)
    password = serializers.CharField(
        write_only=True, required=False, style={'input_type': 'password', 'placeholder': 'Password'}
    )
    auth_code = serializers.CharField(write_only=True, required=False)
    bid = serializers.UUIDField(required=False, write_only=True)
    is_corporate = serializers.BooleanField(default=False)
    iid = serializers.UUIDField(required=False)
    sbid = serializers.CharField(required=False)


    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        auth_code = attrs.get('auth_code')

        if not (username and password) and not auth_code:
            raise serializers.ValidationError(EITHER_USERNAME_AND_PASSWORD_OR_AUTH_CODE_REQUIRED)

        user = None
        if username and password:
            filters = {'is_deleted': False}
            if '@' in username:
                filters['email'] = username
            else:
                filters['username'] = username
            user = User.objects.filter(**filters).last()
            if not user or not user.check_password(password):
                user = None
        elif auth_code:
            user = authenticate(auth_code=auth_code, is_deleted=False)

        if not user or user.is_deleted:
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
    section = serializers.CharField(source='student_profile.section.name', read_only=True)
    total_gems = serializers.IntegerField(source='student_profile.total_gems', read_only=True, default=0)
    rank = serializers.IntegerField(source='student_profile.rank', read_only=True)
    daily_challenge = serializers.BooleanField(source='student_profile.daily_challenge', read_only=True)

    qualification = serializers.CharField(source='teacher_profile.qualification', read_only=True)
    institute = serializers.SerializerMethodField(read_only=True)
    is_superteacher = serializers.BooleanField(source='teacher_profile.is_superteacher')
    badge = serializers.SerializerMethodField()

    def get_role(self, obj):
        if obj.role:
            return obj.role.label
        return None

    def get_institute(self, obj):
        institutes = obj.get_institutes()
        if institutes:
            institute = institutes.last()
            return {'id': institute.id, 'name': institute.name, 'is_editable': False}
        return None

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'mobile_number', 'first_name', 'last_name', 'role', 'gender', 'grade', 'dob',
            'section', 'total_gems', 'rank', 'daily_challenge', 'qualification', 'is_superteacher',
            'institute', 'photo', 'avatar', 'thumbnail', 'has_completed_profile', 'status', 'is_active',
            'is_deleted', 'badge',
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
