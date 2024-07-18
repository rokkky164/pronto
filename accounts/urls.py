from django.urls import path
from rest_framework.routers import SimpleRouter
from django.conf import settings
from django.conf.urls.static import static

from accounts.constants import (
	PASSWORD_PREFIX, PASSWORD_BASENAME, USER_PREFIX, USER_BASENAME, SCHOOL_PREFIX, SCHOOL_BASENAME, APP_NAME,
	LOGIN_URL_NAME, TOKEN_REFRESH_URL_NAME, REGISTER_URL_NAME, ACCOUNT_VERIFY_URL_NAME,
	RESEND_VERIFICATION_CODE_URL_NAME, SEND_MAIL_FOR_REGISTRATION, FETCH_RANDOM_USERNAME_PASSWORD
)
from accounts.views import AccountVerifyView, RegisterView, PasswordViewSet, UserViewSet, \
	CustomLoginView, CustomTokenRefreshView, ResendVerificationCodeView, SchoolViewSet, \
	SendMailForRegistrationView, FetchRandomUserNamePasswordView

router = SimpleRouter(trailing_slash=False)
router.register(PASSWORD_PREFIX, PasswordViewSet, basename=PASSWORD_BASENAME)
router.register(USER_PREFIX, UserViewSet, basename=USER_BASENAME)
router.register(SCHOOL_PREFIX, SchoolViewSet, basename=SCHOOL_BASENAME)

app_name = APP_NAME

urlpatterns = [
	path('auth/login', CustomLoginView.as_view(), name=LOGIN_URL_NAME),
	path('auth/refresh-token', CustomTokenRefreshView.as_view(), name=TOKEN_REFRESH_URL_NAME),
	path('register', RegisterView.as_view(), name=REGISTER_URL_NAME),
	path('register/verify-account/<str:verification_code>', AccountVerifyView.as_view(), name=ACCOUNT_VERIFY_URL_NAME),
	path(
		'register/resend-verification-code',
		ResendVerificationCodeView.as_view(),
		name=RESEND_VERIFICATION_CODE_URL_NAME
	),
	path('send-mail-for-registration', SendMailForRegistrationView.as_view(), name=SEND_MAIL_FOR_REGISTRATION),
	path('fetch-random-username-pwd', FetchRandomUserNamePasswordView.as_view(), name=FETCH_RANDOM_USERNAME_PASSWORD),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + router.urls

