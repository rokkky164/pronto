from django.urls import path
from rest_framework.routers import SimpleRouter
from django.conf import settings
from django.conf.urls.static import static

from accounts.constants import (
	PASSWORD_PREFIX, PASSWORD_BASENAME, USER_PREFIX, USER_BASENAME, APP_NAME,
	LOGIN_URL_NAME, TOKEN_REFRESH_URL_NAME, REGISTER_URL_NAME, ACCOUNT_VERIFY_URL_NAME,
	RESEND_VERIFICATION_CODE_URL_NAME, SEND_MAIL_FOR_REGISTRATION,COMPANY_INFORMATION_URL_NAME, ACCOUNT_MANAGER_DETAILS_URL_NAME
)
from accounts.views import CompanyInformationView, AccountManagerDetailsView, AccountVerifyView,\
	PasswordViewSet, UserViewSet, CustomLoginView, CustomTokenRefreshView, ResendVerificationCodeView

router = SimpleRouter(trailing_slash=False)
router.register(PASSWORD_PREFIX, PasswordViewSet, basename=PASSWORD_BASENAME)
router.register(USER_PREFIX, UserViewSet, basename=USER_BASENAME)

app_name = APP_NAME

urlpatterns = [
	path('auth/company-information', CompanyInformationView.as_view(), name=COMPANY_INFORMATION_URL_NAME),
	path('auth/company-information/<company_info_id>', CompanyInformationView.as_view(), name=COMPANY_INFORMATION_URL_NAME),
	path('auth/account-mgr-details', AccountManagerDetailsView.as_view(), name=ACCOUNT_MANAGER_DETAILS_URL_NAME),
	path('auth/login', CustomLoginView.as_view(), name=LOGIN_URL_NAME),
	path('auth/refresh-token', CustomTokenRefreshView.as_view(), name=TOKEN_REFRESH_URL_NAME),
	path(
		'register/resend-verification-code',
		ResendVerificationCodeView.as_view(),
		name=RESEND_VERIFICATION_CODE_URL_NAME
	)
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + router.urls

