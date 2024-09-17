from rest_framework.serializers import Serializer, ModelSerializer

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

    class Meta:
        model = Product
        exclude = ('created', 'updated')


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
