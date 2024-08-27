from django.contrib import admin
from django.contrib.auth.models import Group

from accounts.models import User, Address, DeleteUserAccountRequest, CertificateDocument
from authorization.models import UserSession, UserEnvironmentDetails, PasswordResetRequest
from authorization.role_list import BUYER, SUPPLIER, DISTRIBUTOR, ADMIN, TRADEPRONTO_ADMIN
from utils.admin import CustomBaseModelAdmin


class UserAddressInline(admin.StackedInline):
    model = Address
    autocomplete_fields = ('country', 'state', 'city',)


@admin.register(User)
class UserAdmin(CustomBaseModelAdmin):
    list_display = ('id', 'username', 'first_name', 'last_name', 'email', 'gender', 'role')
    filter_horizontal = ('permissions',)
    search_fields = ('username', 'first_name', 'last_name', 'email')
    readonly_fields = ["permissions"]
    list_filter = ['role']
    model = User
    verbose_name = "User"

    fieldsets = (
        ('Basic Information', {
            'classes': ('extrapretty', 'grp-collapse grp-open',),
            'fields': (('first_name', 'last_name'), 'gender', 'role', ('email', 'is_email_verified'),
                       ('mobile_number', 'is_mobile_verified'),
                       'date_joined', 'photo', 'avatar', 'thumbnail', 'status'),
        }),
        ('Permissions', {
            'classes': ('grp-collapse grp-closed',),
            'fields': ('is_active', 'is_deleted', 'is_superuser', 'is_staff', 'has_completed_profile', 'permissions')
        }),
        ('Authentication', {
            'classes': ('grp-collapse grp-closed',),
            'fields': ('username', 'password', 'auth_code', 'last_login',)
        }),
    )

    def role(self, obj):
        return obj.role.name if obj.role else '--'

    def get_inlines(self, request, obj):
        inlines = [UserAddressInline, ]
        return inlines

    def save_model(self, request, obj, form, change):
        try:
            user = User.objects.get(id=obj.id)
            if not user.password == obj.password:
                obj.set_password(obj.password)
        except User.DoesNotExist:
            obj.set_password(obj.password)

        if obj.role:
            form.cleaned_data['permissions'] = obj.role.permissions.all()
        super().save_model(request, obj, form, change)


@admin.register(UserSession)
class UserSessionAdmin(CustomBaseModelAdmin):
    verbose_name = "User Session"
    model = UserSession
    list_display = ('id', 'user', 'last_login', 'last_logout', 'user_env_details')
    search_fields = ['id', 'user__first_name', 'user__last_name', 'user__username']


@admin.register(CertificateDocument)
class CertificateDocumentAdmin(CustomBaseModelAdmin):
    verbose_name = "Certificate Document"
    model = CertificateDocument
    list_display = ('id', 'name', 'document_no', 'status')
    search_fields = ['id', 'name', 'document_no', 'status']


@admin.register(UserEnvironmentDetails)
class UserEnvironmentDetailsAdmin(CustomBaseModelAdmin):
    verbose_name = "User Environment Details"
    model = UserEnvironmentDetails
    list_display = ('id', 'os', 'os_version', 'ip_address', 'browser', 'browser_version', 'device_type', 'device')
    search_fields = ['id', 'os', 'ip_address', 'device', 'device_type', 'browser_version', 'browser']


admin.site.unregister(Group)


@admin.register(PasswordResetRequest)
class PasswordResetRequestAdmin(CustomBaseModelAdmin):
    model = PasswordResetRequest
    list_display = (
        'id', 'user', 'verification_code', 'created_at', 'expires_at', 'reset_at', 'is_password_reset'
    )
    search_fields = ['id', 'user__first_name', 'user__last_name', 'user__username', 'verification_code']
    verbose_name = "Password Reset Request"


@admin.register(Address)
class AddressAdmin(CustomBaseModelAdmin):
    model = Address
    list_display = (
        'id', 'user', 'address_line_1', 'city', 'state', 'country', 'pincode'
    )
    search_fields = ['id', 'user__first_name', 'user__last_name', 'user__username', 'address_line_1', 'pincode',
                     'city__name']
    verbose_name = "Address"


@admin.register(DeleteUserAccountRequest)
class DeleteUserAccountRequestAdmin(CustomBaseModelAdmin):
    model = DeleteUserAccountRequest
    list_display = ('id', 'user', 'reason', 'is_logged_in', 'is_account_deleted', 'requested_at', 'updated_at')
    search_fields = ['user__first_name', 'user__last_name']
    list_filter = ['is_logged_in', 'is_account_deleted']
    verbose_name = "Delete User Account Request"
