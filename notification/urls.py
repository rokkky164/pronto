from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import NotificationViewSet, EmailHistoryViewSet
from .constants import APP_NAME, BASENAME, URL_PREFIX, URL_PREFIX_EMAIL, BASENAME_EMAIL

app_name = APP_NAME

router = SimpleRouter(trailing_slash=False)
router.register(URL_PREFIX, NotificationViewSet, basename=BASENAME)
router.register(URL_PREFIX_EMAIL, EmailHistoryViewSet, basename=BASENAME_EMAIL)

urlpatterns = router.urls
