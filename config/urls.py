from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

from api.views import *

router = DefaultRouter()
router.register(r"criminals", CriminalsAPIView)
router.register(r"camera", CameraAPIView)
router.register(r"records", FilterAPIView)

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
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
