from rest_framework import serializers
from django.contrib.auth.models import User

from app_run.models import Run



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


