from django.urls import include, path
from rest_framework import routers

from .views import UserViewSet, LanguageViewSet
from oauth.textapis.views import CustomAPIsViewSet
from tvsm.views import SeriesViewSet

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register("users", UserViewSet)
router.register("languages", LanguageViewSet, basename="languages")
router.register("customapis", CustomAPIsViewSet, basename="customapis")
router.register("tvsm", SeriesViewSet, basename="tvsm")

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
  path("", include(router.urls)),
  path("", include("oauth.urls")),
]
