from rest_framework.routers import SimpleRouter

from catalog.views import ProductViewSet

router = SimpleRouter(trailing_slash=False)
router.register(r'product', ProductViewSet, basename='product')

app_name = 'catalog'

urlpatterns = [] + router.urls
