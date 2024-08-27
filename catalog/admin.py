from django.contrib import admin

from catalog.models import (
	Category, ProductConfig, Product, Manufacturer,
	ProductReview, ProductRatings, ProductImages,
	ShippingAndOrdering
)
from utils.admin import CustomBaseModelAdmin

@admin.register(Category)
class CategoryAdmin(CustomBaseModelAdmin):
	list_display = ('id', 'name',)
	search_fields = ['id', 'name']
	model = Category
	verbose_name = "Category"


@admin.register(Product)
class ProductAdmin(CustomBaseModelAdmin):
	list_display = ('id', 'name',)
	search_fields = ['id', 'name']
	model = Product
	verbose_name = "Product"


@admin.register(Manufacturer)
class ManufacturerAdmin(CustomBaseModelAdmin):
	list_display = ('id', 'name',)
	search_fields = ['id', 'name']
	model = Manufacturer
	verbose_name = "Manufacturer"


@admin.register(ProductReview)
class ProductReviewAdmin(CustomBaseModelAdmin):
	list_display = ('id', 'buyer_name',)
	search_fields = ['id', 'buyer_name']
	model = ProductReview
	verbose_name = "ProductReview"


@admin.register(ProductRatings)
class ProductRatingsAdmin(CustomBaseModelAdmin):
	list_display = ('id', 'buyer_name',)
	search_fields = ['id', 'buyer_name']
	model = ProductRatings
	verbose_name = "ProductRatings"


@admin.register(ProductImages)
class ProductImagesAdmin(CustomBaseModelAdmin):
	list_display = ('id', 'product',)
	search_fields = ['id', 'product__name']
	model = ProductImages
	verbose_name = "ProductImages"


@admin.register(ShippingAndOrdering)
class ShippingAndOrderingAdmin(CustomBaseModelAdmin):
	list_display = ('id', 'moq',)
	search_fields = ['id', 'moq']
	model = ShippingAndOrdering
	verbose_name = "ShippingAndOrdering"
