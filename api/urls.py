from django.urls import path


from api.views import CameraAPIView, CriminalsAPIView


urlpatterns = [
    path(
        "camera/",
        CameraAPIView.as_view({"get": "list", "post": "create"}),
    ),
    path(
        "camera/<int:pk>/",
        CameraAPIView.as_view(
            {"get": "retrieve", "put": "update", "delete": "destroy"}
        ),
    ),
    path(
        "criminals/",
        CriminalsAPIView.as_view({"get": "list", "post": "create"}),
    ),
    path(
        "criminals/<int:pk>/",
        CriminalsAPIView.as_view(
            {"get": "retrieve", "put": "update", "delete": "destroy"}
        ),
    ),
    
]



