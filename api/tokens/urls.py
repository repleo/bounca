from rest_framework.routers import DefaultRouter

from api.tokens.views import AuthorisedAppViewSet

router = DefaultRouter()
router.register(r"tokens", AuthorisedAppViewSet, basename="token")
urlpatterns = router.urls
