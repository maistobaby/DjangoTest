from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from api import views

urlpatterns = patterns('',
#    url(r'^$', views, name='index'),
    url(r'^posts/$', views.PostsAPIView.as_view(), name='posts'),
)
apipatterns = patterns('',
    url(r'^posts/(?P<action>\w+)\??$', views.PostsAPIView.as_view(), name='posts'),
)

urlpatterns = urlpatterns+format_suffix_patterns(apipatterns)
