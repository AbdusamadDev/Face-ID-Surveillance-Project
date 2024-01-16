#  ############## Django and Django Rest Framework imports ################
from rest_framework.authentication import TokenAuthentication
from django.http import JsonResponse, StreamingHttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.request import HttpRequest
from rest_framework.response import Response
from django.db.utils import OperationalError
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)

#  ######################### Local apps imports ###########################
from api.utils import host_address, find_nearest_location, get_unique_key
from api.pagination import (
    CriminalsRecordsPagination,
    WebTempRecordsPagination,
    CriminalsPagination,
    CameraPagination,
)
from api.serializers import (
    TempClientLocationsSerializer,
    CriminalsRecordsSerializer,
    WebTempRecordsSerializer,
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
    WebTempRecords,
    TempRecords,
    Criminals,
    UniqueKey,
    Camera,
)

#  #################### Standard libraries imports ########################
from imutils.video import VideoStream
from math import ceil
import shutil
import time
import uuid
import os
import cv2


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
    model = TempClientLocations
    lookup_field = "pk"
    queryset = TempClientLocations.objects.all()
    serializer_class = TempClientLocationsSerializer
    clients = dict()

    def create(self, request, *args, **kwargs):
        uuid_key = request.headers.get("token", None)
        if uuid_key is None:
            return Response({"msg": "Token is not provided!"}, status=400)
        try:
            uuid_object = UniqueKey.objects.get(uuid=uuid_key)
        except UniqueKey.DoesNotExist:
            return Response({"msg": "Invalid token provided!"}, status=400)
        # except Exception:

        # return Response({"msg": "Unknown error occued, try again"}, status=422)
        uuid_object.delete()
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        longitude = serializer.validated_data.get("longitude")
        latitude = serializer.validated_data.get("latitude")
        longitudes = [key.get("longitude") for key in self.clients.values()]
        latitudes = [key.get("latitude") for key in self.clients.values()]
        if (latitude not in latitudes) and (longitude not in longitudes):
            try:
                pk = get_unique_key(list(self.clients.keys()))
                self.clients[pk] = {"longitude": longitude, "latitude": latitude}
                return Response(
                    {"msg": "Client connected", "client_pk": pk}, status=201
                )
            except Exception as error:
                print("Passing delete because of: ", error)
                pass
        return Response({"msg": "Error occured!"}, status=422)

    def list(self, request, *args, **kwargs):
        try:
            query = TempRecords.objects.all().first()
            headers = request.headers
            longitude = headers.get("longitude", None)
            latitude = headers.get("latitude", None)
            client_id = headers.get("client-id", None)
            if longitude is None or latitude is None:
                return Response(
                    {"msg": "Longitude or Latitude is not provided in headers"}
                )
            if client_id is None:
                return Response({"msg": "Client ID is not provided"}, status=400)
            self.clients[client_id] = {"longitude": longitude, "latitude": latitude}
            clients = list(self.clients.values())
            camera = TempRecords.objects.all().first()
            if camera is not None:
                camera = camera.record.camera
            else:
                return Response({})
            camera_object = Camera.objects.get(pk=camera.pk)
            target_location = {
                "longitude": camera_object.longitude,
                "latitude": camera_object.latitude,
            }
            if not clients or clients is None:
                return Response({"msg": "No clients connected yet!"}, status=422)
            try:
                nearest_location = find_nearest_location(target_location, clients)
            except:
                return Response(
                    {"msg": "Longitude and Latitude must be in the [-90; 90] range."},
                    status=400,
                )

            if (float(nearest_location.get("longitude")) == float(longitude)) and (
                float(nearest_location.get("latitude")) == float(latitude)
            ):
                TempRecords.objects.all().delete()
                return Response(TempRecordsSerializer(query).data)
            else:
                return Response({})
        except OperationalError:
            return Response({})


class WebTempRecordsViewSet(ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    model = WebTempRecords
    queryset = WebTempRecords.objects.all()
    pagination_class = WebTempRecordsPagination
    serializer_class = WebTempRecordsSerializer

    def list(self, request, *args, **kwargs):
        query = self.queryset
        serializer = self.serializer_class(instance=query, many=True)
        stored_data = serializer.data
        query.delete()
        return Response(data={"data": stored_data})


@api_view(http_method_names=["GET"])
def fully_fetched_data(request):
    clients = TempClientLocations.objects.all()
    serializer = TempClientLocationsSerializer(instance=clients, many=True)
    return Response(serializer.data, status=200)


@api_view(http_method_names=["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def generate_token(request):
    token = uuid.uuid4()
    UniqueKey.objects.get_or_create(uuid=token)
    return Response({"token": token})


class VideoStreamAPIView(APIView):
    def get(self, request, *args, **kwargs):
        url = request.query_params.get("url")
        if not url:
            return StreamingHttpResponse(
                "URL parameter is missing", status=400, content_type="text/plain"
            )

        vs = VideoStream(url).start()
        time.sleep(0.5)  # Warm-up time for the camera

        def frame_generator():
            while True:
                frame = vs.read()
                if frame is None:
                    break

                (flag, encodedImage) = cv2.imencode(".jpg", frame)
                if not flag:
                    continue

                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n"
                    + bytearray(encodedImage)
                    + b"\r\n"
                )

        return StreamingHttpResponse(
            frame_generator(), content_type="multipart/x-mixed-replace; boundary=frame"
        )
