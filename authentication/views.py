'''
from .models import Practice, User
from rest_framework import viewsets

from .serializers import UserSerializer, PracticeSerializer

class PracticeViewSet(viewsets.ModelViewSet):
  queryset = Practice.objects.all()
  serializer_class = PracticeSerializer

class UserViewSet(viewsets.ModelViewSet):
  queryset = User.objects.all()
  serializer_class = UserSerializer
'''
