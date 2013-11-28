from django.utils.timezone import now
from rest_framework import serializers
from rest_framework import pagination
import time

from api.models import Post

class PostSerializer(serializers.ModelSerializer):
    """
    Serializes post querysets.
    """
    days_since_created = serializers.SerializerMethodField('get_days_since_created')
    created_unixts = serializers.SerializerMethodField('get_created_unixts')

    class Meta:
        model = Post

    def get_days_since_created(self, obj):
        return (now() - obj.created_time).days

    def get_created_unixts(self, obj):
        return int( time.mktime(obj.created_time.utctimetuple()) )

class PaginatedPostSerializer(pagination.PaginationSerializer):
    """
    Serializes page objects of post querysets.
    """
    class Meta:
        object_serializer_class = PostSerializer
