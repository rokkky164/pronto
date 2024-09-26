import logging

from django.utils.timezone import now, timedelta

from catalog.models import (
    Product, Category, ProductVariant,
    ProductConfig, SupplierProducts,
    Manufacturer, ProductReview,
    ProductRatings, ProductImages,
    ShippingAndOrdering
)
from pronto.celery import app
from utils.constants import (
     MAIL_DATE_TIME_FORMAT, CORPORATE_HOST_LIST, DEFAULT_SUPPORT_EMAIL,
     ONBOARD_EX_CANDIDATE_CRPORATE_TEMPLATE, ONBOARD_EX_CANDIDATE_TEMPLATE,
     DEFAULT_SUPPORT_EMAIL, ONBOARD_CRPORATE_ADMIN_TEMPLATE, DASHBOARD_HOST_DICT
)
from utils.helpers import notification_mail, get_required_details_for_mail
from utils.db_interactors import get_record_by_filters, get_record_by_id, db_create_record, db_update_instance, \
    db_update_records_with_filters
from utils.tasks import base_task


@app.task(name='InitiateAccountVerification')
def create_product(user_id: int):
    """
    This task creates an entry in product table in database
    """
    return
