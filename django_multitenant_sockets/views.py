
from .decorators import get_user_org_pk
from .models import OrgGroup
from .models import PublicGroup
from .serializers import OrgGroupSerializer
from .serializers import PublicGroupSerializer
from django.http import Http404
from rest_framework import permissions
from rest_framework import viewsets


class CanAccessOrgGroup(permissions.BasePermission):

  def has_permission(self, request, view):
    if request.user.is_staff or view.org_pk() == get_user_org_pk(request.user):
      return True
    else:
      return False

  def has_object_permission(self, request, view, obj):
    if request.user.is_staff or obj.org.pk == get_user_org_pk(request.user):
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
    return self.kwargs.get("org_pk")

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
