from rest_framework.serializers import Serializer, ModelSerializer, CharField, ChoiceField, IntegerField, EmailField, \
    SlugRelatedField, FileField, SerializerMethodField, BooleanField

from accounts.models import CompanyInformation
from utils.db_interactors import get_record_by_filters, get_record_by_id, get_single_record_by_filters, \
    get_select_related_object_list
from utils.helpers import get_image_path
from .models import (
    Product, Category, ProductVariant,
    ProductConfig, SupplierProducts,
    Manufacturer, ProductReview,
    ProductRatings, ProductImages,
    ShippingAndOrdering
)


class ProductCreateSerializer(ModelSerializer):

    class Meta:
        model = Product
        exclude = ('created', 'updated')


class ProductListSerializer(ModelSerializer):
    manufacturer_name = CharField(source='manufacturer.name')
    supplier_name = SerializerMethodField()
    supplier_address = SerializerMethodField()
    image = SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'description', 'advance_payment', 'shelf_life', 
            'packaging_details', 'grade', 'bar_code', 'bar_code_type',
            'is_private_label_available', 'manufacturer_name', 'supplier_name',
            'supplier_address', 'image'
        )

    def get_supplier_name(self, obj):
        _, supplier_obj = get_single_record_by_filters(SupplierProducts, filters={'product_id': obj.id})
        if isinstance(supplier_obj, SupplierProducts):
            return supplier_obj.name

    def get_supplier_address(self, obj):
        _, supplier = get_single_record_by_filters(CompanyInformation, filters={'product_id': obj.id})
        if isinstance(supplier, CompanyInformation):
            return supplier.legal_address

    def get_image(self, obj):
        _, prod_image_obj = get_single_record_by_filters(ProductImages, filters={'product_id': obj.id})
        if isinstance(prod_image_obj, ProductImages):
            return get_image_path(prod_image_obj.image)


class ProductDetailsSerializer(ModelSerializer):
    name = CharField(required=True)
    description = CharField(required=True)
    advance_payment = CharField(required=False)
    shelf_life = CharField(required=True)
    packaging_details = CharField(required=True)
    grade = CharField(required=False)
    bar_code = CharField(required=True)
    bar_code_type = CharField(required=True)
    is_private_label_available = BooleanField(default=False)
    manufacturer_name = CharField(source='manufacturer.name')
    supplier_name = SerializerMethodField()
    supplier_address = SerializerMethodField()
    image = CharField(required=False)

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'description', 'advance_payment', 'shelf_life', 
            'packaging_details', 'grade', 'bar_code', 'bar_code_type',
            'is_private_label_available', 'manufacturer_name', 'supplier_name',
            'supplier_address', 'image'
        )

    def get_supplier_name(self, obj):
        _, supplier_obj = get_single_record_by_filters(SupplierProducts, filters={'product_id': obj.id})
        if isinstance(supplier_obj, SupplierProducts):
            return supplier_obj.name

    def get_supplier_address(self, obj):
        _, supplier = get_single_record_by_filters(CompanyInformation, filters={'product_id': obj.id})
        if isinstance(supplier, CompanyInformation):
            return supplier.legal_address

    def get_image(self, obj):
        _, prod_image_obj = get_single_record_by_filters(ProductImages, filters={'product_id': obj.id})
        if isinstance(prod_image_obj, ProductImages):
            return get_image_path(prod_image_obj.image)


class ManufacturerSerializer(ModelSerializer):

    class Meta:
        model = Manufacturer
        exclude = ('created', 'updated')


class ProductReviewSerializer(ModelSerializer):

    class Meta:
        model = ProductReview
        exclude = ('created', 'updated')


class ProductRatingsSerializer(ModelSerializer):

    class Meta:
        model = ProductRatings
        exclude = ('created', 'updated')


class ProductImagesSerializer(ModelSerializer):

    class Meta:
        model = ProductImages
        exclude = ('created', 'updated')


class ShippingAndOrderingSerializer(ModelSerializer):

    class Meta:
        model = ShippingAndOrdering
        fields = '__all__'
