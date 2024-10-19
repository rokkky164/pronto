import uuid
from collections import OrderedDict

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import (
	RegexValidator, MinLengthValidator, MaxLengthValidator, MaxValueValidator, MinValueValidator
)
from django.db import models
from django.db.models import QuerySet, Q, Model, OneToOneField, CASCADE, ManyToManyField, ForeignKey, SET_NULL, \
	CharField, TextField, BooleanField, DateTimeField, UUIDField, TextChoices, EmailField, FileField, ImageField,\
	IntegerField, DecimalField, JSONField
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import ArrayField

from accounts.models import Address
from common.location.models import City, State, Country
from pronto.settings import IMAGE_MIME_TYPES, MAX_PRODUCT_IMAGE_SIZE
from utils.db_interactors import get_record_by_filters, db_get_family, get_single_record_by_filters, db_add_many_to_many_field_data
from utils.validators import check_file_mime_type, check_file_size
from utils.helpers import catalog_directory_path


def verify_product_image_mime_type(image):
	check_file_mime_type(file=image, mime_type_list=IMAGE_MIME_TYPES)


def verify_product_image_size(logo):
	check_file_size(file=logo, max_size=MAX_PRODUCT_IMAGE_SIZE)


class Category(Model):
	name = CharField(max_length=255)

	def __str__(self):
		return self.name


class Manufacturer(Model):
	name = CharField(_('Manufacturer Name'), max_length=100)
	brand_name = CharField(verbose_name=_("Brand Name"), max_length=100)
	address = ForeignKey(Address, on_delete=models.CASCADE, null=True, blank=True)
	ingredients = TextField(max_length=1000, help_text=_('Enter ingredients'))
	annual_production_size = CharField(_('Annual Production Size'), max_length=50, null=True, blank=True)
	quantity_available_per_month = CharField(_('Quantity Available Per Month'), max_length=50, null=True, blank=True)
	lead_time = CharField(_('Lead Time'), max_length=50, null=True, blank=True)
	quantity_available_today = CharField(_('Quantity Available Today'), max_length=50, null=True, blank=True)
	incoterms = CharField(_('Incoterms'), max_length=50, null=True, blank=True)


class Product(Model):
	class BarCodeType(TextChoices):
		UNIVERSAL_PRODUCT_CODE = 'UPC', _('Universal Product Code')
		EUROPEAN_ARTICLE_NUMBER = 'EAN', _('European Article Number')
		GS1_DATABAR = 'GS1', _('GS1 DataBar')
		QR_CODES = 'QR', _('QR Codes')
		CODE_128 = 'C128', _('Code 128')
		ITF_14 = 'ITF14', _('ITF-14')

	name = CharField(_('Product Name'), max_length=100)
	category = ManyToManyField(Category, related_name='products', blank=True)
	description = TextField(max_length=1000, help_text=_('Enter description'))
	advance_payment = CharField(_('Advance Payment'), max_length=20, null=True, blank=True)
	shelf_life = IntegerField(_('Shelf Life in days'), null=True, blank=True)
	packaging_details = TextField(max_length=1000, help_text=_('Packaging details'), blank=True, null=True)
	grade = CharField(_('Grade'), max_length=10, null=True, blank=True)
	bar_code = CharField(_('Bar Code'), max_length=20)
	bar_code_type = CharField(_('Bar Code Type'), choices=BarCodeType.choices, max_length=5)
	certificates = ForeignKey('accounts.CertificateDocument', on_delete=CASCADE, null=True, blank=True)
	additional_data = JSONField(default=OrderedDict, null=True, blank=True)
	is_private_label_available = BooleanField(default=False)
	manufacturer = ForeignKey(Manufacturer, on_delete=models.CASCADE, null=True)
	created = DateTimeField(auto_now_add=True)
	updated = DateTimeField(auto_now=True)

	def __str__(self):
		return f'{self.pk}: {self.name}'


class ProductVariant(Model):
	product = ForeignKey(Product, on_delete=models.CASCADE)
	net_weight_per_volume = CharField(_('Net Weight/Volume'), max_length=20)
	gross_weight_per_volume = CharField(_('Gross Weight/Volume'), max_length=20, null=True, blank=True)
	quantity_per_carton = CharField(_('Quantity/Carton'), max_length=20, null=True, blank=True)
	quantity_of_items_per_pallete = CharField(_('Quantity/allete'), max_length=20, null=True, blank=True)
	volume = CharField(_('Volume'), max_length=20, null=True, blank=True)
	
	def __str__(self):
		return f'{self.product.name}'


class ProductConfig(Model):
	is_in_stock = BooleanField(default=False)
	product = ForeignKey(Product, on_delete=models.CASCADE)


class SupplierProducts(Model):
	product = ForeignKey(Product, on_delete=models.CASCADE)
	supplier = ForeignKey('accounts.Company', on_delete=models.CASCADE)


class ProductReview(Model):
	buyer_name = CharField(_('Buyer Name'), max_length=100)
	review = TextField(max_length=1000, blank=True, null=True)
	product = ForeignKey(Product, on_delete=models.CASCADE)
	created = DateTimeField(auto_now_add=True)
	updated = DateTimeField(auto_now=True)


class ProductRatings(Model):
	buyer_name = CharField(_('Buyer Name'), max_length=100)
	rating = DecimalField(max_digits=1, decimal_places=1, default=0.0)
	product = ForeignKey(Product, on_delete=models.CASCADE)
	created = DateTimeField(auto_now_add=True)
	updated = DateTimeField(auto_now=True)


class ProductImages(Model):
	product = ForeignKey(Product, on_delete=CASCADE, related_name='product_images')
	image = ImageField(upload_to=catalog_directory_path, blank=True, null=True, validators=[verify_product_image_mime_type, verify_product_image_size])

	def __str__(self):
		return f'{self.id}-{self.product.name}'


class ShippingAndOrdering(Model):
	class PalletsTypes(TextChoices):
		EUROPEAN_PALLET = 'EP', _('European Pallet')
		NORTHAMERICAN_PALLET = 'NP', _('North American Pallet')
		AUSTRALIAN_STANDARD_PALLET = 'AP', _('Australian Standard Pallet')
		ISO_PALLET = 'IP', _('ISO Pallet')
		UK_PALLET = 'UP', _('UK Pallet')
		ASIA_PACIFIC_PALLET = 'APP', _('Asia-Pacific Pallet')
		CHEP_PALLET  = 'CP', _(' CHEP Pallets ')
		ISPM_15 = 'ISP', _('ISPM 15')
		CANADIAN_PALLET  = 'CAP', _('Canadian Pallet')

	product = ForeignKey(Product, on_delete=CASCADE, related_name='product')
	quantity_in_the_box = CharField(_('Quantity in the box'), max_length=50)
	payment_terms = TextField(_('Payment terms'), max_length=1000)
	moq = CharField(_('MOQ per Month'), max_length=50, null=True, blank=True)
	ltl_available = BooleanField(default=False)
	lead_time_first_shipment = CharField(_('Lead Time First Shipment'), max_length=50, null=True, blank=True)
	annual_production = CharField(_('Annual Production'), max_length=50, null=True, blank=True)
	min_no_boxes_pallet = CharField(_('Min No of boxes on pallet'), max_length=50, null=True, blank=True)
	max_no_boxes_pallet = CharField(_('Max No of boxes on pallet'), max_length=50, null=True, blank=True)
	max_no_items_in_full_40_inch_container = CharField(_('Max no of boxes in full 40 inch container'), max_length=50, null=True, blank=True)
	shipment_terms = CharField(_('Shipment terms'), max_length=100, null=True, blank=True)
	shipping_modes = CharField(_('Shipment Modes'), max_length=100, null=True, blank=True)
	types_of_pallets_used = CharField(_('Types of Pallets used'), max_length=100, null=True, blank=True)
