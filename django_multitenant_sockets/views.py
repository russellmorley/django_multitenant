from rest_framework import viewsets, permissions
from django.http import Http404

from .models import PublicGroup, OrgGroup
from .serializers import PublicGroupSerializer, OrgGroupSerializer

class CanAccessOrgGroup(permissions.BasePermission):
  def has_permission(self, request, view):
    if request.user.is_staff or view.org_pk() == request.user.org_pk():
      return True
    else:
      return False
  def has_object_permission(self, request, view, obj):
    if request.user.is_staff or obj.org_pk() == request.user.org_pk():
      return True
    else:
      return False

class PublicGroupViewSet(viewsets.ModelViewSet):
  permission_classes = (permissions.IsAuthenticated,)
  queryset = PublicGroup.objects.all()
  serializer_class = PublicGroupSerializer

class OrgGroupViewSet(viewsets.ModelViewSet):
  permission_classes = (permissions.IsAuthenticated, CanAccessOrgGroup)
  serializer_class = OrgGroupSerializer

  def org_pk(self):
    return self.kwargs.get('org_pk')

  def get_queryset(self):
    org_pk = self.org_pk() 
    if org_pk is not None:
      org_groups = OrgGroup.objects.filter(org=self.org_pk())
      if org_groups.count() > 0:
        return org_groups
      else:
        raise Http404()
    else:
      return OrgGroup.objects.all()
       
  def perform_create(self, serializer):
    serializer.save(org=self.org_pk())
