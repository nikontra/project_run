
from debug_toolbar.toolbar import debug_toolbar_urls
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from app_run.views import (company_details, RunViewSet,
                           UserViewSet, RunStartAPIView,
                           RunStopAPIView, AthleteInfoAPIView,
                           ChallengeView, PositionViewSet, CollectibleItemAPIView)

router = routers.DefaultRouter()
router.register('api/runs', RunViewSet)
router.register('api/users', UserViewSet)
router.register('api/positions', PositionViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/company_details/', company_details),
    path('api/runs/<int:run_id>/start/', RunStartAPIView.as_view()),
    path('api/runs/<int:run_id>/stop/', RunStopAPIView.as_view()),
    path('api/athlete_info/<int:athlete_id>/', AthleteInfoAPIView.as_view()),
    path('api/challenges/', ChallengeView.as_view()),
    path('api/collectible_item/', CollectibleItemAPIView.as_view()),
    path('api/upload_file/', CollectibleItemAPIView.as_view()),
    path('', include(router.urls)),
] + debug_toolbar_urls()