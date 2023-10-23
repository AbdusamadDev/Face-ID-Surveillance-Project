# Django and Django Rest Framework imports
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.request import HttpRequest
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework import status

# Local apps imports
from api.filters import CameraFilter, CriminalsFilter
from api.models import Camera, Criminals, Encodings
from api.pagination import CameraPagination, CriminalsPagination
from api.serializers import CameraSerializer, CriminalsSerializer
from api.utils import host_address, process_image, is_already_in

# Standard libraries imports
from math import ceil
import numpy as np
import os
import time
import cv2


class CameraAPIView(ModelViewSet):
    """Class for CRUD operation of Cmaera details"""

    model = Camera
    serializer_class = CameraSerializer
    queryset = Camera.objects.all().order_by("name")
    lookup_field = "pk"
    filterset_class = CameraFilter
    pagination_class = CameraPagination


class CriminalsAPIView(ModelViewSet):
    """
    Class for CRUD operation of Criminals details
    Added some AI functionality to validate the image
    """

    model = Criminals
    serializer_class = CriminalsSerializer
    queryset = Criminals.objects.all()
    lookup_field = "pk"
    filterset_class = CriminalsFilter
    pagination_class = CriminalsPagination

    def create(self, request, *args, **kwargs):
        # Get serializers and prepare image for validation
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        first_name = serializer.validated_data.get("first_name")
        image = serializer.validated_data.get("image")
        nparr = np.frombuffer(image.read(), np.uint8)
        img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        encoding = process_image(img_np)
        # Image validation goes here
        if encoding is None:
            return Response(
                data={
                    "msg": "No face found in entered image, djangoni jinni kurissilami"
                },
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        elif len(encoding) != 1:
            return Response(
                data={"msg": "Only one face is allowed in one image!"},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        else:
            new_encoding = encoding[0].embedding
            if is_already_in(new_encoding):
                return Response(
                    data={"msg": "This criminal is already in database!"},
                    status=status.HTTP_409_CONFLICT,
                )
            else:
                new_encoding = list(new_encoding)
        Encodings.objects.create(criminal=first_name, encoding=encoding)
        self.perform_create(serializer=serializer)
        return Response({"ADsad": "ASDASDad"})


class BaseScreenshotsAPIView(APIView):
    """Base View for handling image files and returning File responses"""

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
    """Get all screenshots paths"""

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
