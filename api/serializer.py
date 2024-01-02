from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Task


class UserSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = User
        fields = ['id', 'username', 'password', 'email']


class TaskSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Task
        fields = '__all__'
        read_only_fields = ['user']