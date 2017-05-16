from rest_framework import serializers
from .models import PublicGroup, OrgGroup

class PublicGroupSerializer(serializers.ModelSerializer):
  class Meta:
    model = PublicGroup
    read_only_fields = ('id',)
    fields = ('name',)

class OrgGroupSerializer(serializers.ModelSerializer):
  class Meta:
    model = OrgGroup
    read_only_fields = ('id', 'org')
    fields = ('id', 'name', 'org')
