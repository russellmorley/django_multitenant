# from __future__ import absolute_import
#
# from .models import Practice
# from .models import User
# from rest_framework import serializers
#
#
# class PracticeSerializer(serializers.ModelSerializer):
#
#   class Meta:
#     model = Practice
#     fields = [
#       "id",
#       "name",
#       "url"
#     ]
#
#
# class UserSerializer(serializers.ModelSerializer):
#   password = serializers.CharField(write_only=True, required=False)
#
#   class Meta:
#     model = User
#     fields = [
#       "id",
#       "url",
#       "username",
#       "password",
#       "practice",
#       "email",
#     ]
