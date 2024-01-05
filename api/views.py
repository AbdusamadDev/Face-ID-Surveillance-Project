#  ############## Django and Django Rest Framework imports ################
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import api_view
from rest_framework.request import HttpRequest
from django.db.utils import OperationalError
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework import status

#  ######################### Local apps imports ###########################
from api.utils import host_address, find_nearest_location
from api.pagination import (
    CriminalsRecordsPagination,
    CriminalsPagination,
    CameraPagination,
)
from api.serializers import (
    TempClientLocationsSerializer,
    CriminalsRecordsSerializer,
    TempRecordsSerializer,
    CriminalsSerializer,
    CameraSerializer,
)
from api.filters import (
    CriminalsRecordFilter,
    CriminalsFilter,
    CameraFilter,
)
from api.models import (
    TempClientLocations,
    CriminalsRecords,
    TempRecords,
    Criminals,
    Camera,
)

#  #################### Standard libraries imports ########################
from math import ceil
import shutil
import time
import os


class CameraAPIView(ModelViewSet):
    """Class for CRUD operation of Camera details"""

    model = Camera
    serializer_class = CameraSerializer
    queryset = Camera.objects.all().order_by("-id")
    lookup_field = "pk"
    filterset_class = CameraFilter
    pagination_class = CameraPagination
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


class CriminalsAPIView(ModelViewSet):
    """
    Class for CRUD operation of Criminals details
    Added some AI functionality to validate the image
    in serializers
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    model = Criminals
    serializer_class = CriminalsSerializer
    queryset = Criminals.objects.all()
    lookup_field = "pk"
    filterset_class = CriminalsFilter
    pagination_class = CriminalsPagination

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(
            instance, data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(
            instance, data=request.data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        path = os.path.join("media", "criminals", kwargs.get("pk"))
        image = serializer.validated_data.get("image")
        if image:
            if os.path.exists(path):
                shutil.rmtree(path)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        path = os.path.join("media", "criminals", kwargs.get("pk"))
        if os.path.exists(path):
            shutil.rmtree(path)
        return super().destroy(request, *args, **kwargs)


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


class CriminalsRecordsAPIView(ModelViewSet):
    serializer_class = CriminalsRecordsSerializer
    queryset = CriminalsRecords.objects.all().order_by("-date_recorded")
    pagination_class = CriminalsRecordsPagination
    filterset_class = CriminalsRecordFilter
    http_method_names = ["get", "head", "options", "post", "delete"]


class AndroidRequestHandlerAPIView(ModelViewSet):
    authentication_classes = [TokenAuthentication]
    model = TempRecords
    lookup_field = "pk"
    queryset = TempRecords.objects.all()
    serializer_class = TempRecordsSerializer

    def create(self, request, *args, **kwargs):
        headers = request.headers
        if not headers:
            return Response({"msg": "location lgt & ltd not provided in headers"})
        longitude = headers.get("longitude", None)
        latitude = headers.get("latitude", None)
        clients = list(TempClientLocations.objects.all().values())
        if {"longitude": longitude, "latitude": latitude} not in clients:
            try:
                TempClientLocations.objects.create(
                    longitude=longitude, latitude=latitude
                )
                return Response({"msg": "Client connected"}, status=201)
            except:
                pass
        return Response({"msg": "Error occured!"}, status=422)

    def list(self, request, *args, **kwargs):
        try:
            query = self.queryset.first()
            headers = request.headers
            longitude = headers.get("longitude", None)
            latitude = headers.get("latitude", None)
            if longitude is None or latitude is None:
                return Response(
                    {"msg": "Longitude or Latitude is not provided in headers"}
                )

            clients = list(TempClientLocations.objects.all().values())
            camera = self.queryset.first()
            if camera is not None:
                camera = camera.record.camera
            else:
                return Response({})
            camera_object = Camera.objects.get(pk=camera.pk)
            target_location = {
                "longitude": camera_object.longitude,
                "latitude": camera_object.latitude,
            }
            nearest_location = find_nearest_location(target_location, clients)
            if (float(nearest_location.get("longitude")) == float(longitude)) and (
                float(nearest_location.get("latitude") == float(latitude))
            ):
                self.model.objects.all().delete()
                return Response(self.serializer_class(query).data)
            return Response({})
        except OperationalError:
            return Response({})

    def destroy(self, request, pk, *args, **kwargs):
        headers = request.headers
        if "longitude" not in headers.keys() or "latitude" not in headers.keys():
            return Response(
                {"msg": "Required headers not provided: longitude & latitude"}
            )

        client = TempClientLocations.objects.get(pk=pk)
        if not client:
            return Response({"msg": f"Client with id: {pk} not found!"}, status=404)
        client.delete()
        return Response(status=204)


@api_view(http_method_names=["GET"])
def fully_fetched_data(request):
    clients = TempClientLocations.objects.all()
    serializer = TempClientLocationsSerializer(instance=clients, many=True)
    return Response(serializer.data, status=200)
