from rest_framework.routers import DefaultRouter

from api.tokens.views import AuthorisedAppViewSet

router = DefaultRouter()
router.register(r"delete", AuthorisedAppViewSet, basename="delete-account")
urlpatterns = router.urls
