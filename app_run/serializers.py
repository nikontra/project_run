from django.shortcuts import get_object_or_404
from rest_framework import serializers
from django.contrib.auth.models import User

from app_run.models import Run, AthleteInfo, Challenge, Position


class UserRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username',
                  'first_name', 'last_name')


class RunSerializer(serializers.ModelSerializer):
    athlete_data = UserRunSerializer(source='athlete', read_only=True)

    class Meta:
        model = Run
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    runs_finished = serializers.SerializerMethodField()

    def get_runs_finished(self, obj):
        return obj.runs.filter(status='finished').count()

    def get_type(self, obj):
        if obj.is_staff:
            return 'coach'
        return 'athlete'

    class Meta:
        model = User
        fields = ('id', 'date_joined',
                  'username', 'last_name',
                  'first_name', 'type', 'runs_finished')


class AthleteInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AthleteInfo
        fields = '__all__'


class ChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Challenge
        fields = '__all__'


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = ('id', 'run', 'latitude', 'longitude')

    def validate_run(self, value):
        if value.status != 'in_progress':
            raise serializers.ValidationError(
                'Забег, для которого передается позиция, должен иметь статус "in_progress".')
        return value

    def validate_latitude(self, value):
        if not -90 <= value <= 90:
            raise serializers.ValidationError("Широта должна находиться в диапазоне [-90.0, 90.0].")
        return value

    def validate_longitude(self, value):
        if not -180 <= value <= 180:
            raise serializers.ValidationError("Долгота должна находиться в диапазоне [-180.0, 180.0].")
        return value




