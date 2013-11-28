from django.conf.urls.defaults import url, patterns, include
from django.contrib.auth.models import User, Group

from rest_framework import viewsets, routers

# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    model = User

class GroupViewSet(viewsets.ModelViewSet):
    model = Group

# Routers provide an easy way of automatically determining the URL conf
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'groups', GroupViewSet)

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'DjangoTest.views.home', name='home'),
    # url(r'^DjangoTest/', include('DjangoTest.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^polls/', include('polls.urls', namespace="polls")),
    url(r'^api-auth/', include('rest_framework.urls', namespace="rest_framework")),
    url(r'^api/', include('api.urls', namespace="api")),
    url(r'^gallery/', include('gallery.urls', namespace="gallery")),
)
