from django.db.models import Q
from rest_framework.permissions import BasePermission

from utils.db_interactors import get_record_by_filters, db_check_existing_record
from .constants import CATALOG_PERMISSION_ERROR_MESSAGE
from .models import (
    Product, Category, ProductVariant,
    ProductConfig, SupplierProducts,
    Manufacturer, ProductReview,
    ProductRatings, ProductImages,
    ShippingAndOrdering
)


class ProductPermission(BasePermission):

    message = CATALOG_PERMISSION_ERROR_MESSAGE

    def has_permission(self, request, view):
        if view.action in ['create', 'list', 'retrieve', 'update']:
            return True

        return False

    def has_object_permission(self, request, view, obj):
        return True
