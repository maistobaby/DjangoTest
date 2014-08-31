from django.db import models
from django.utils import dateparse
import datetime, time, re
#from datetime import datetime

# Create your models here.
class Post(models.Model):
    created_time = models.DateTimeField()
    from_id = models.BigIntegerField()
    from_name = models.CharField(max_length=300)
    link = models.URLField()
    message = models.TextField()
    object_id = models.BigIntegerField(primary_key=True)
    image_url = models.URLField()
    image_width = models.SmallIntegerField(default=0)
    image_height = models.SmallIntegerField(default=0)
    likes_count = models.IntegerField(default=0)
    shares_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    status_type = models.CharField(max_length=32)
    hot_score = models.FloatField(default=0.0)

    class Meta:
        ordering = ('-created_time',)

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.message

    def parseJSONObj(self, obj):
        self.created_time = strtotime( obj['created_time'] )
        self.from_id = int( obj['from']['id'] )
        self.from_name = obj['from']['name']
        self.link = existOrDefault( '', obj, ['link'] )
        self.message = existOrDefault( '', obj, ['message'] )
        self.object_id = int( obj['object_id'] )
        self.image_url = existOrDefault( '', obj, ['image_url'] )
        self.image_width = existOrDefault( 0, obj, ['image_width'] )
        self.image_height = existOrDefault( 0, obj, ['image_height'] )
        self.likes_count = existOrDefault( 0, obj, ['likes','summary','total_count'] )
        self.shares_count = existOrDefault( 0, obj, ['shares','count'])
        self.comments_count = existOrDefault( 0, obj, ['comments','summary','total_count'] )
        self.status_type= existOrDefault( 'None', obj, ['status_type'] )
        self.hot_score = 5*self.shares_count+ 2*self.comments_count + self.likes_count
        return self

    def unix_timestamp(self):
        return dtUnixTS(self.created_time)

def existOrDefault(value, obj, keys):
    for key in keys:
        try:
            obj=v = obj[key]
        except:
            v = value
            break
    return v

def strtotime(str):
    return dateparse.parse_datetime(str)
#    format = '%Y-%m-%d %H:%M:%S'
#    return datetime.strptime(str, format)

def dtUnixTS(dt):
    return time.mktime(dt.utctimetuple())

