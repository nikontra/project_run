from django.db.models import Sum
from geopy.distance import geodesic
from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, generics
from rest_framework.decorators import api_view
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from openpyxl import load_workbook

from app_run.models import Run, AthleteInfo, Challenge, Position, CollectibleItem
from app_run.serializers import RunSerializer, UserSerializer, AthleteInfoSerializer, ChallengeSerializer, \
    PositionSerializer, ColletibleItemSerializer

CHALLENGES = [
    'Сделай 10 Забегов!',
    'Пробеги 50 километров!'
]

COLLECTIBLE_ITEM_FIELDS = {
    'Name': 'name',
    'UID': 'uid',
    'Latitude': 'latitude',
    'Longitude': 'longitude',
    'Value': 'value',
    'URL': 'picture'
}


class Pagination(PageNumberPagination):
    page_size_query_param = 'size'


# Create your views here.
@api_view(['GET'])
def company_details(request):
    details  = {
        'company_name': settings.COMPANY_NAME,
        'slogan': settings.SLOGAN,
        'contacts': settings.CONTACTS
    }
    return Response(details)


class ChallengeView(generics.ListAPIView):
    queryset = Challenge.objects.all()
    serializer_class = ChallengeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('athlete',)


class RunViewSet(viewsets.ModelViewSet):
    queryset = Run.objects.all().select_related('athlete')
    serializer_class = RunSerializer
    pagination_class = Pagination
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_fields = ('status', 'athlete',)
    ordering_fields = ('created_at',)


class RunStartAPIView(APIView):
    def post(self, request, run_id):
        run = get_object_or_404(Run, id=run_id)
        if run.status != 'init':
            return Response(status=status.HTTP_400_BAD_REQUEST)
        run.status = 'in_progress'
        run.save()
        serializer = RunSerializer(run)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RunStopAPIView(APIView):
    def post(self, request, run_id):
        run = get_object_or_404(Run.objects.select_related('athlete'), id=run_id)
        if run.status != 'in_progress':
            return Response(status=status.HTTP_400_BAD_REQUEST)
        run.status = 'finished'

        positions = Position.objects.filter(run=run.id)
        if len(positions) > 1:
            distance = 0
            for i in range(len(positions) - 1):
                distance += geodesic(
                    (positions[i].latitude, positions[i].longitude),
                    (positions[i + 1].latitude, positions[i + 1].longitude)).km
            run.distance = round(distance, 3)
        run.save()

        serializer = UserSerializer(run.athlete)
        if serializer.data['runs_finished'] % 10 == 0:
            Challenge.objects.create(
                full_name=CHALLENGES[0],
                athlete=run.athlete
            )

        sum_distance = Run.objects.filter(athlete=run.athlete).aggregate(Sum('distance'))
        if sum_distance['distance__sum'] >= 50:
            Challenge.objects.create(
                full_name=CHALLENGES[1],
                athlete=run.athlete
            )

        serializer = RunSerializer(run)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.filter(is_superuser=False)
    serializer_class = UserSerializer
    pagination_class = Pagination
    filter_backends = (SearchFilter, OrderingFilter,)
    search_fields = ('first_name', 'last_name',)
    ordering_fields = ('date_joined',)

    def get_queryset(self):
        qs = self.queryset
        type = self.request.query_params.get('type', None)
        if type == 'coach':
            qs = qs.filter(is_staff=True)
        if type == 'athlete':
            qs = qs.filter(is_staff=False)
        return qs


class AthleteInfoAPIView(APIView):
    def get(self, request, athlete_id):
        get_object_or_404(User, id=athlete_id)
        athlete_info, created = AthleteInfo.objects.get_or_create(pk=athlete_id)
        serializer = AthleteInfoSerializer(athlete_info)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, athlete_id):
        try:
            weight = int(request.data['weight'])
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        goals = request.data['goals']
        if not(0 < weight < 900) or type(goals) != str:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        get_object_or_404(User, id=athlete_id)
        athlete_info, created = AthleteInfo.objects.update_or_create(
            pk=athlete_id,
            defaults={
                "weight": weight,
                "goals": goals
            }
        )
        serializer = AthleteInfoSerializer(athlete_info)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all().select_related('run')
    serializer_class = PositionSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('run',)


class CollectibleItemAPIView(APIView):
    def get(self, request):
        items = CollectibleItem.objects.all()
        serializer = ColletibleItemSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "Файл с данными не передан"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            wb = load_workbook(file, read_only=True)
            ws = wb.active
        except Exception as e:
            return Response({"error": f"Ошибка чтения файла: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        rows = [i for i in ws.rows]
        failed_rows = []
        for row in rows[1:]:
            row = [i.value for i in row]
            serializer = ColletibleItemSerializer(data=row, many=True)
            if serializer.is_valid():
                serializer.save()
            else:
                failed_rows.append(row)
            return Response(failed_rows, status=status.HTTP_200_OK)

