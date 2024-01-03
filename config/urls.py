from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin
from django.conf import settings

from api.views import *

router = DefaultRouter()
router.register(r"criminals", CriminalsAPIView)
router.register(r"camera", CameraAPIView)
router.register(r"records", CriminalsRecordsAPIView)
router.register(r"mud", AndroidRequestHandlerAPIView)

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
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
