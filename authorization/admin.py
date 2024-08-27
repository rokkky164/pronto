from django.contrib import admin

from authorization.models import Role, Permission, AccountVerificationRequest, EmailChangeRequest
from utils.admin import CustomBaseModelAdmin


@admin.register(Permission)
class PermissionAdmin(CustomBaseModelAdmin):
	list_display = ('id', 'keyword', )
	model = Permission
	search_fields = ['id', 'keyword']
	verbose_name = "Permission"


@admin.register(Role)
class RoleAdmin(CustomBaseModelAdmin):
	list_display = ('id', 'name', 'label', 'is_default', 'role_type')
	search_fields = ['id', 'label']
	model = Role
	verbose_name = "Role"
	filter_horizontal = ('permissions', )


@admin.register(AccountVerificationRequest)
class AccountVerificationRequestAdmin(CustomBaseModelAdmin):
	list_display = ('id', 'user', 'verification_code', 'created_at', 'expires_at', 'verified_at', 'is_account_verified')
	search_fields = ['id', 'verification_code', 'user__first_name', 'user__last_name', 'user__username']
	model = AccountVerificationRequest
	verbose_name = "Account Verification Request"


@admin.register(EmailChangeRequest)
class EmailChangeRequestAdmin(CustomBaseModelAdmin):
	list_display = ('id', 'user', 'new_email', 'verification_code', 'created_at', 'expires_at', 'changed_at',
					'is_email_changed')
	search_fields = ['id', 'verification_code', 'user__first_name', 'user__last_name', 'user__username']
	model = EmailChangeRequest
	verbose_name = "Email Change Request"
