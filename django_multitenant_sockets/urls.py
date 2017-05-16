from django.conf.urls import include, url
from .views import PublicGroupViewSet, OrgGroupViewSet


api_urls = [
  url(
    r'^publicgroups/$', PublicGroupViewSet.as_view({
      'get': 'list', 
      'post': 'create'
    }), 
    name='publicgroup-list'
  ),
  url(
    r'^publicgroups/(?P<pk>[0-9]+)/$', PublicGroupViewSet.as_view({
      'get': 'retrieve', 
      'put': 'update', 
      'delete': 'destroy'
    }),
    name='publicgroup-detail'
  ),

  url(
    r'^orggroups/orgs/(?P<org_pk>[0-9]+)/$', OrgGroupViewSet.as_view({
      'get': 'list', 
      'post': 'create'
    }), 
    name='orggroup-list'
  ),
  url(
    r'^orggroups/(?P<pk>[0-9]+)/$', OrgGroupViewSet.as_view({
      'get': 'retrieve', 
      'put': 'update', 
      'delete': 'destroy'
    }),
    name='orggroup-detail'
  ),

]
