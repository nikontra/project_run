from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from app_run.models import Run, AthleteInfo
from app_run.serializers import RunSerializer, UserSerializer, AthleteInfoSerializer


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
        run = get_object_or_404(Run, id=run_id)
        if run.status != 'in_progress':
            return Response(status=status.HTTP_400_BAD_REQUEST)
        run.status = 'finished'
        run.save()
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
        user = get_object_or_404(User, id=athlete_id)
        athlete_info, created = AthleteInfo.objects.get_or_create(user_id=user)
        serializer = AthleteInfoSerializer(athlete_info)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, athlete_id):
        if not(0 < request.data['weight'] < 900):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user = get_object_or_404(User, id=athlete_id)
        athlete_info, created = AthleteInfo.objects.update_or_create(
            user_id=user,
            defaults={
                "weight": request.data['weight'],
                "goals": request.data['goals']
            }
        )
        serializer = AthleteInfoSerializer(athlete_info)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

