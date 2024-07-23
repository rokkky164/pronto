import uuid

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import (
    RegexValidator, MinLengthValidator, MaxLengthValidator, MaxValueValidator, MinValueValidator
)
from django.db import models
from django.db.models import QuerySet, Q, Model, OneToOneField, CASCADE, ManyToManyField, ForeignKey, SET_NULL, \
    CharField, TextField, BooleanField, DateTimeField, UUIDField, TextChoices, EmailField, FileField
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.fields import JSONField

from accounts.constants import (
    FIRST_NAME_VALIDATION_MESSAGE,
    FIRST_NAME_MINIMUM_LENGTH_MESSAGE,
    FIRST_NAME_MAXIMUM_LENGTH_MESSAGE,
    EMAIL_ALREADY_EXIST,
    LAST_NAME_MAXIMUM_LENGTH_MESSAGE,
    LAST_NAME_VALIDATION_MESSAGE
)
from accounts.utils import user_directory_path, UsernameValidator, verify_document_mime_type, verify_document_size
from authorization.role_list import (
    BUYER,
    SUPPLIER,
    DISTRIBUTOR,
    ADMIN,
    TRADEPRONTO_ADMIN
)
from common.location.models import City, State, Country

from utils.db_interactors import get_record_by_filters, db_get_family, get_single_record_by_filters, db_add_many_to_many_field_data


class User(AbstractUser):

    class Gender(models.TextChoices):
        MALE = 'MALE', _('MALE')
        FEMALE = 'FEMALE', _('FEMALE')
        __empty__ = _('Unknown')


    username_validator = UsernameValidator()

    first_name = models.CharField(
        _('First Name'), max_length=40, null=False, blank=False,
        validators=[
            RegexValidator(
                regex="^(?!.*[.'-]{2})[a-zA-Z][a-zA-Z'.-]*[a-zA-Z]$",  # (?=.{2,40}$)
                message=FIRST_NAME_VALIDATION_MESSAGE
            ),
            MinLengthValidator(limit_value=2, message=FIRST_NAME_MINIMUM_LENGTH_MESSAGE),
            MaxLengthValidator(limit_value=40, message=FIRST_NAME_MAXIMUM_LENGTH_MESSAGE)
        ]
    )
    last_name = models.CharField(
        _('Last Name'), max_length=50, null=True, blank=True,
        validators=[
            RegexValidator(
                regex="^(?!.*[.'-]{2})[a-zA-Z]([a-zA-Z '.-]*[a-zA-Z])?$",  # (?=.{2,40}$)
                message=LAST_NAME_VALIDATION_MESSAGE
            ),
            MaxLengthValidator(limit_value=50, message=LAST_NAME_MAXIMUM_LENGTH_MESSAGE)
        ]
    )

    auth_code = models.CharField(_('Auth Code'), max_length=8, blank=True, null=True)
    gender = models.CharField(verbose_name=_("Gender"), choices=Gender.choices, max_length=6, blank=True, null=True)
    photo = models.ImageField(_('Photo'), upload_to=user_directory_path, blank=True, null=True)
    dob = models.DateField(_('Date of Birth'), blank=True, null=True)
    mobile_number = models.CharField(_('Mobile Number'), max_length=14, blank=True, null=True)
    has_completed_profile = models.BooleanField(verbose_name=_("Has Completed Profile"), default=False)

    avatar = models.CharField(verbose_name=_("Avtar"), max_length=200, blank=True, null=True)
    thumbnail = models.CharField(verbose_name=_("Avtar Thumbnail"), max_length=200, blank=True, null=True)

    role = models.ForeignKey(
        to='authorization.Role',
        verbose_name=_("Role"),
        on_delete=models.SET_NULL,
        related_name='users',
        blank=True,
        null=True
    )
    permissions = models.ManyToManyField(
        'authorization.Permission', verbose_name=_("Permissions"), related_name='associated_users', blank=True)


    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f'{self.pk}: {self.get_full_name()}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.role:
            self.permissions.clear()
            db_add_many_to_many_field_data(instance=self, field='permissions', _id_list=self.role.permissions.all())

    def get_role(self):
        if self.role:
            return self.role.label
        else:
            return None

    def clean(self):
        email = self.email
        if email:
            exist = User.objects.filter(Q(email=email) & ~Q(id=self.id) & Q(is_deleted=False)).exists()
            if exist:
                raise ValidationError({'email': EMAIL_ALREADY_EXIST})

    def has_permission(self, keywords: list[str]) -> bool:
        permission = self.permissions.filter(keyword__in=keywords)
        return permission.count() == len(keywords)

    def is_tradepronto_admin(self) -> bool:
        return self.role.name == TRADEPRONTO_ADMIN['name']

    def is_supplier(self) -> bool:
        return self.role.name == HR_PERSONNEL['name']

    def is_buyer(self) -> bool:
        return self.role.name == EXTERNAL_CANDIDATE['name']


class Address(models.Model):
    """
    Model to store user/company addresses
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=False, null=False, related_name='address')

    address_line_1 = models.CharField(_('Address Line 1'), max_length=50, null=True, blank=True)
    address_line_2 = models.CharField(_('Address Line 2'), max_length=50, null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.PROTECT, null=False, blank=False)
    state = models.ForeignKey(State, on_delete=models.PROTECT, null=False, blank=False)
    country = models.ForeignKey(Country, on_delete=models.PROTECT, null=False, blank=False)
    pincode = models.PositiveIntegerField(_('Pin Code'), validators=[MinValueValidator(1000), MaxValueValidator(9999999999)])

    def __str__(self):
        return f'<Address: {self.address_line_1}, {self.address_line_2}, {self.city}, {self.state}, {self.country}>'


class DeleteUserAccountRequest(Model):
    identifier = UUIDField(default=uuid.uuid4, unique=True, blank=True, null=True)
    user = ForeignKey(to=User, related_name='delete_requests', verbose_name=_("User"), on_delete=CASCADE)
    reason = TextField(_("Delete reason"), null=True, blank=True)
    is_logged_in = BooleanField(default=False, verbose_name=_("Is user logged in)"))
    is_account_deleted = BooleanField(default=False, verbose_name=_("Is account deleted"))
    requested_at = DateTimeField(auto_now_add=True, verbose_name=_("Requested at"))
    confirm_at = DateTimeField(verbose_name=_("Confirm At"), blank=True, null=True)
    updated_at = DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    def __str__(self):
        return f"{self.pk}: {self.user}"


class CompanyInformation(Model):
    class AnnualTurnover(TextChoices):
        TILL_5M = 'TILL_5M', _('0-5M')
        FIVEM_TO_TWENTYM = 'FIVEM_TO_TWENTYM', _('5M-20M')
        TWENTYM_TO_HUNDREDM = 'TWENTYM_TO_HUNDREDM', _('20M-100M')
        HUNDREDM_TO_ONEBILLION   = 'HUNDREDM_TO_ONEBILLION', _('100M-1B')
        ONEBILLION_PLUS   = 'ONEBILLION_PLUS', _('1B+')

    name = CharField(_('Company Name'), max_length=100)
    tax_id = CharField(_('Tax Identification Number'), max_length=100)
    annual_turnover = CharField(_('Annual Turnover'), max_length=50, choices=AnnualTurnover.choices)
    hq_location = CharField(_('Headquarter Location'), max_length=50)
    company_type = CharField(_('Company Type'), max_length=100)
    other_hubs = ArrayField(CharField(max_length=50), null=True, default=list)
    product_categories = ArrayField(CharField(max_length=50), null=True, default=list)
    vat_payer = CharField(_('Vat Payer'), max_length=100)
    legal_address = CharField(_('Legal Address'), max_length=255)

    def __str__(self):
        return f"{self.pk}: {self.name}"


class AccountManagerDetails(Model):
    name = CharField(_('Account Manager Name'), max_length=100)
    title = CharField(_('Title'), max_length=100)
    department = CharField(_('Department'), max_length=100)
    email = EmailField(verbose_name=_('Email'), max_length=100, unique=True)
    phone = CharField(_('Mobile Number'), max_length=14, blank=True, null=True)   
    user = ForeignKey(User, on_delete=CASCADE)
    
    def __str__(self):
        return f"{self.pk}: {self.name}"


class CertificateDocument(Model):
    class Name(TextChoices):
        PAN = 'PAN', _('Permanent Account Number')
        CIN = 'CIN', _('Corporate Identification Number')
        TAN = 'TAN', _('Tax Deduction Account Number')
        GSTIN = 'GSTIN', _('Goods & Services Tax Identification Number')

    class Status(TextChoices):
        SAVED = 'S', _('Saved')
        APPROVAL_REQUESTED = 'AR', _('Approval Requested')
        APPROVED = 'A', _('Approved')
        REJECTED = 'R', _('Rejected')

    name = CharField(_('Name'), choices=Name.choices, max_length=50)
    document_no = CharField(_('Document Number'), max_length=50, null=True, blank=True)
    document = FileField(validators=[verify_document_mime_type, verify_document_size], null=True, blank=True)
    status = CharField(_('Status'), choices=Status.choices, max_length=50)
    
    def __str__(self):
        return f"{self.pk}: {self.name}"
