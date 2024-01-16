from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter
from django.urls import path, include, re_path
from django.conf.urls.static import static
from rest_framework import permissions
from django.contrib import admin
from django.conf import settings

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from api.views import *


schema_view = get_schema_view(
    openapi.Info(
        title="Your API",
        default_version="v1",
        description="Your API description",
        terms_of_service="https://www.yourapp.com/terms/",
        contact=openapi.Contact(email="contact@yourapp.com"),
        license=openapi.License(name="Your License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

router = DefaultRouter()
router.register(r"criminals", CriminalsAPIView)
router.register(r"camera", CameraAPIView)
router.register(r"records", CriminalsRecordsAPIView)
router.register(r"mud", AndroidRequestHandlerAPIView),
router.register(r"web-results", WebTempRecordsViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path(
        "screenshots/<username>/",
        ScreenshotImagesAPIView.as_view(),
    ),
    path(
        "suspends/",
        SuspendedScreenshotsAPIView.as_view(),
    ),
    path("api/clients/", fully_fetched_data),
    path("auth/token/", obtain_auth_token),
    path(
        "docs/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path("android/auth/token/", generate_token),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
