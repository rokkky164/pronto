from django.db.models import ForeignKey
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db import models

from accounts.constants import (
	OS_MAX_LENGTH,
	IP_ADDRESS_MAX_LENGTH,
	BROWSER_MAX_LENGTH,
	DEVICE_TYPE_MAX_LENGTH,
	DEVICE_MAX_LENGTH,
	VERSION_MAX_LENGTH
)
from utils.helpers import generate_random_code


class Permission(models.Model):
	"""
	Model to store different roles
	"""
	keyword = models.CharField(_('Name'), max_length=50, null=False, blank=False)
	is_internal = models.BooleanField(default=False)

	def __str__(self):
		return f'<Permission: {self.keyword}>'


class Role(models.Model):
	"""
	Model to store different roles
	"""
	name = models.CharField(_('Name'), max_length=50, null=False, blank=False)
	label = models.CharField(_('Label'), max_length=50, null=True, blank=True)
	is_default = models.BooleanField(default=False)
	role_type = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True)
	permissions = models.ManyToManyField(to=Permission, related_name='associated_roles', blank=True)

	def __str__(self):
		return f'{self.pk}: {self.label}'


class UserEnvironmentDetails(models.Model):

	class DeviceType(models.TextChoices):
		PC = 'PC', _('PC')
		MOBILE = 'MOBILE', _('MOBILE')
		TABLET = 'TABLET', _('TABLET')
		BOT = 'BOT', _('BOT')

	os = models.CharField(_('OS'), max_length=OS_MAX_LENGTH, null=True, blank=True)
	os_version = models.CharField(_('OS Version'), max_length=VERSION_MAX_LENGTH, null=True, blank=True)
	ip_address = models.CharField(_('IP Address'), max_length=IP_ADDRESS_MAX_LENGTH, null=True, blank=True)
	browser = models.CharField(_('Browser'), max_length=BROWSER_MAX_LENGTH, null=True, blank=True)
	browser_version = models.CharField(_('Browser Version'), max_length=OS_MAX_LENGTH, null=True, blank=True)
	device_type = models.CharField(
		_('Device Type'), choices=DeviceType.choices, max_length=DEVICE_TYPE_MAX_LENGTH, null=True, blank=True
	)
	device = models.CharField(_('Device'), max_length=DEVICE_MAX_LENGTH, null=True, blank=True)

	def __str__(self):
		return f'{self.pk}'


class UserSession(models.Model):
	"""
	Model to store session related info for User
	"""

	user = ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='session_info')
	token = models.TextField(_('JWT Token'))
	last_login = models.DateTimeField(_('Last Login'), auto_now_add=True)
	last_logout = models.DateTimeField(_('Last Logout'), blank=True, null=True)
	user_env_details = ForeignKey(
		UserEnvironmentDetails, related_name='user_sessions', on_delete=models.CASCADE, null=True, blank=True
	)

	def __str__(self):
		return f'{self.pk}'


class PasswordResetRequest(models.Model):
	"""
	Model to store password request related data for each user
	"""
	user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='password_reset_requests')
	verification_code = models.CharField(_('Password Verification Code'), max_length=8, blank=False, null=False)
	created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
	expires_at = models.DateTimeField(_('Expires At'))
	reset_at = models.DateTimeField(_('Reset At'), blank=True, null=True)
	is_password_reset = models.BooleanField(_('Is Password Reset'), default=False)

	def __str__(self):
		return f'<PasswordResetRequest: {self.verification_code}>'

	def save(self, **kwargs):
		if not self.pk:
			self.verification_code = generate_random_code()
			self.expires_at = timezone.now() + timezone.timedelta(days=7)
		return super().save()

	@property
	def is_expired(self):
		return self.expires_at < timezone.now()


class EmailChangeRequest(models.Model):
	"""
	Model to store email change request related data for each user
	"""
	user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='email_change_requests')
	new_email = models.EmailField(_('New Email'), blank=False, null=False)
	verification_code = models.CharField(_('Verification Code'), max_length=8, blank=False, null=False)
	created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
	expires_at = models.DateTimeField(_('Expires At'))
	changed_at = models.DateTimeField(_('Changed At'), blank=True, null=True)
	is_email_changed = models.BooleanField(_('Is Email Changed'), default=False)

	class Meta:
		unique_together = ('user', 'verification_code')

	def __str__(self):
		return f'<EmailChangeRequest: {self.verification_code}>'

	def save(self, *args, **kwargs):
		if not self.pk:
			self.verification_code = generate_random_code()
			self.expires_at = timezone.now() + timezone.timedelta(days=7)
		return super().save()

	@property
	def is_expired(self):
		return self.expires_at < timezone.now()

	@property
	def is_valid(self):
		return not self.is_expired and not self.is_email_changed


class AccountVerificationRequest(models.Model):
	"""
	Model to store account verification request related data for each user
	"""
	user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='account_verification_requests')
	verification_code = models.CharField(_('Verification Code'), max_length=8, blank=False, null=False)
	created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
	expires_at = models.DateTimeField(_('Expires At'))
	verified_at = models.DateTimeField(_('Verified At'), blank=True, null=True)
	is_account_verified = models.BooleanField(_('Is Account Verified'), default=False)

	def __str__(self):
		return f'<AccountVerificationRequest: {self.verification_code}>'

	def save(self, **kwargs):
		if not self.pk:
			self.verification_code = generate_random_code()
			self.expires_at = timezone.now() + timezone.timedelta(days=7)
		return super().save()

	@property
	def is_expired(self):
		return self.expires_at < timezone.now()
