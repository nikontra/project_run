from rest_framework import serializers
from django.contrib.auth.models import User

from app_run.models import Run


class RunSerializer(serializers.ModelSerializer):
    class Meta:
        model = Run
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()

    def get_type(self, obj):
        if obj.is_staff:
            return 'coach'
        return 'athlete'

    class Meta:
        model = User
        fields = ('id', 'date_joined',
                  'username', 'last_name',
                  'first_name', 'type')


