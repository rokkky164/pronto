from .models import (
    Product, Category, ProductVariant,
    ProductConfig, SupplierProducts,
    Manufacturer, ProductReview,
    ProductRatings, ProductImages,
    ShippingAndOrdering
)


def db_get_all_products():
    return Product.objects.defer("created", "updated").order_by("-id")