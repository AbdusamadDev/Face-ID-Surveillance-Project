############### Django and Django Rest Framework imports ################
from django.http import JsonResponse
from rest_framework.viewsets import ModelViewSet
from rest_framework.request import HttpRequest
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status  #

########################## Local apps imports ###########################
from api.models import Camera, Criminals, CriminalsRecords
from api.utils import host_address
from api.pagination import (
    CriminalsRecordsPagination,
    CriminalsPagination,
    CameraPagination,
)
from api.serializers import (
    CriminalsRecordsSerializer,
    CriminalsSerializer,
    CameraSerializer,
)
from api.filters import (
    CriminalsRecordFilter,
    CriminalsFilter,
    CameraFilter,
)

##################### Standard libraries imports ########################
from django.utils.timezone import make_aware
from calendar import monthrange
from datetime import datetime
from math import ceil
import shutil
import pytz
import time
import os


class CameraAPIView(ModelViewSet):
    """Class for CRUD operation of Camera details"""

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
    in serializers
    """

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


class FilterAPIView(ModelViewSet):
    model = CriminalsRecords
    serializer_class = CriminalsRecordsSerializer
    queryset = CriminalsRecords.objects.all()
    pagination_class = CriminalsRecordsPagination
    filterset_class = CriminalsRecordFilter
    http_method_names = ['get', 'head', 'options', "post", "delete"]

    def get_queryset(self):
        # Helper function to create an aware datetime object
        def create_aware_datetime(year, month, day, default_tz, end_of_day=False):
            dt = datetime(year, month, day)
            if end_of_day:
                dt = dt.replace(hour=23, minute=59, second=59, microsecond=999999)
            return make_aware(dt, default_tz)

        # Helper function to determine the last day of a month
        def last_day_of_month(year, month):
            return monthrange(year, month)[1]

        # Get query parameters
        byear = self.request.query_params.get('byear')
        bmonth = self.request.query_params.get('bmonth')
        bday = self.request.query_params.get('bday')
        eyear = self.request.query_params.get('eyear')
        emonth = self.request.query_params.get('emonth')
        eday = self.request.query_params.get('eday')

        # Set default timezone
        default_tz = pytz.timezone('Asia/Karachi')  # Replace with your default timezone

        # Determine the start date
        if byear:
            byear = int(byear)
            bmonth = int(bmonth) if bmonth else 1
            bday = int(bday) if bday else 1
            begin_date = create_aware_datetime(byear, bmonth, bday, default_tz)
        else:
            begin_date = None

        # Determine the end date
        if eyear:
            eyear = int(eyear)
            emonth = int(emonth) if emonth else 12
            eday = int(eday) if eday else last_day_of_month(eyear, emonth)
            end_date = create_aware_datetime(eyear, emonth, eday, default_tz, end_of_day=True)
        else:
            end_date = None

        # Filter based on the calculated start and end dates
        if begin_date and end_date:
            return self.queryset.filter(date_recorded__gte=begin_date, date_recorded__lte=end_date)
        elif begin_date:
            return self.queryset.filter(date_recorded__gte=begin_date)
        elif end_date:
            return self.queryset.filter(date_recorded__lte=end_date)
        else:
            # If no dates are provided, default to returning all records
            return self.queryset

# 939110925
