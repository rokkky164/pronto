from rest_framework.routers import SimpleRouter

from authorization.views import RoleViewSet

router = SimpleRouter(trailing_slash=False)
router.register(r'role', RoleViewSet, basename='role')

app_name = 'authorization'

urlpatterns = [] + router.urls
