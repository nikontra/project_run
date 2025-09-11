from django.conf import settings
from django.core.serializers import serialize
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView

from app_run.models import Run
from app_run.serializers import RunSerializer, UserSerializer


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


class RunStartAPIView(APIView):
    def post(self, request, run_id):
        run = get_object_or_404(Run, id=run_id)
        serializer = RunSerializer(run)
        if run.status != 'init':
            return Response(status=status.HTTP_400_BAD_REQUEST)
        run.status = 'in_progress'
        run.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class RunStopAPIView(APIView):
    def post(self, request, run_id):
        run = get_object_or_404(Run, id=run_id)
        serializer = RunSerializer(run)
        if run.status != 'in_progress':
            return Response(status=status.HTTP_400_BAD_REQUEST)
        run.status = 'finished'
        run.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.filter(is_superuser=False)
    serializer_class = UserSerializer
    filter_backends = [SearchFilter]
    search_fields = ['first_name', 'last_name']

    def get_queryset(self):
        qs = self.queryset
        type = self.request.query_params.get('type', None)
        if type == 'coach':
            qs = qs.filter(is_staff=True)
        if type == 'athlete':
            qs = qs.filter(is_staff=False)
        return qs

