from django.http import FileResponse, JsonResponse
from django.conf import settings
from rest_framework.response import Response
from rest_framework.request import HttpRequest
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework import status

from api.utils import host_address
from api.models import Camera, Criminals
from api.serializers import CameraSerializer, CriminalsSerializer
from api.filters import CameraFilter, CriminalsFilter
from api.pagination import CameraPagination, CriminalsPagination

from math import ceil
import os
import time


class CameraAPIView(ModelViewSet):
    model = Camera
    serializer_class = CameraSerializer
    queryset = Camera.objects.all().order_by("name")
    lookup_field = "pk"
    filterset_class = CameraFilter
    pagination_class = CameraPagination


class CriminalsAPIView(ModelViewSet):
    model = Criminals
    serializer_class = CriminalsSerializer
    queryset = Criminals.objects.all()
    lookup_field = "pk"
    filterset_class = CriminalsFilter
    pagination_class = CriminalsPagination


class BaseScreenshotsAPIView(APIView):
    def get_path(self):
        raise NotImplementedError()

    def get(self, request: HttpRequest, *args, **kwargs):
        start = time.time()
        query_params = request.query_params
        year = query_params.get("year", None)
        month = query_params.get("month", None)
        day = query_params.get("day", None)
        page = int(query_params.get("page", 1))
        page_size = int(query_params.get("page_size", 50))

        steps = ()
        if year:
            steps += (year,)
            if day and not month:
                return self.bad_request("Month must be provided before day")
        if month:
            if not year:
                return self.bad_request("Year must be provided before month")
            steps += (month,)
        if day:
            if not (month and year):
                return self.bad_request("Month and Year must be provided before day")
            steps += (day,)

        path = os.path.join(self.get_path(*args, **kwargs), *steps)
        response_list = []

        for root, _, files in os.walk(path):
            response_list.extend(
                [host_address + str(os.path.join(root, file))[1:] for file in files]
            )

        total_images = len(response_list)
        total_pages = ceil(total_images / page_size)
        start_index = (page - 1) * page_size
        end_index = start_index + page_size

        end = time.time()
        return Response(
            data={
                "path": response_list[start_index:end_index],
                "elapsed": end - start,
                "total_images": total_images,
                "total_pages": total_pages,
                "current_page": page,
            }
        )

    @staticmethod
    def bad_request(text):
        return Response(data={"msg": text}, status=status.HTTP_400_BAD_REQUEST)


class ScreenshotImagesAPIView(BaseScreenshotsAPIView):
    def get_path(self, username, *args, **kwargs):
        return os.path.join("./media/screenshots/criminals", username)


class SuspendedScreenshotsAPIView(BaseScreenshotsAPIView):
    def get_path(self, *args, **kwargs):
        return "./media/screenshots/suspends"


class UnknownFacesImageView(APIView):
    def get(self, request):
        directory = "./media/unknown_faces/"
        response_list = []
        start = time.time()

        for path in os.listdir(directory):
            path_dir = directory + path
            for year in os.listdir(path_dir):
                year_dir = f"{path_dir}/{year}"
                for month in os.listdir(year_dir):
                    month_dir = f"{year_dir}/{month}"
                    for day in os.listdir(month_dir):
                        day_dir = f"{month_dir}/{day}"
                        response_list.extend(
                            [f"{day_dir}/{image}" for image in os.listdir(day_dir)]
                        )

        end = time.time()

        return JsonResponse(
            {
                "image_list": response_list,
                "elapsed_time": str(end - start),
                "ip_address": host_address,
            }
        )


# 939110925