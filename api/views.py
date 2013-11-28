from rest_framework.pagination import PaginationSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
import urllib, urllib2, json, re, time

from api.models import Post
from api.serializers import PostSerializer, PaginatedPostSerializer

### Create your views here.

def unixts( dt ):
    return int( time.mktime(dt.utctimetuple()) )

def getObjectID( id ):
    return re.match(r'\d+_(\d+)', id).group(1)

def validateUrl( url ):
    valid = True
    try:
        validate(url)
    except ValidationError, e:
        valid = False
    return valid

def savePostsToDB(posts):
    for obj in posts['data']:
        try:
            try:
                obj['object_id']
            except:
                obj['object_id'] = getObjectID( obj['id'] )
            try:
                obj['picture']
            except:
                continue

            url = "http://graph.facebook.com/"+obj['object_id']+"?fields=source,height,width"
            rsp = HTTP_GET( url )
            if rsp['status']:
                image = json.loads( rsp['content'] )
                obj['image_url'] = image['source']
                obj['image_width'] = image['width']
                obj['image_height'] = image['height']
            post = Post.objects.get(object_id=obj['object_id'])
        except Post.DoesNotExist:
            try:
                if obj['image_url'] and obj['image_url']:
                    post = Post()
            except:
                None

        post.parseJSONObj(obj)
        post.save()

def HTTP_GET(url):
    req = urllib2.Request(url)
    req.add_header('Accept', 'application/json')
    rsp = { 'status':True, 'code':200, 'content':''}
    try:
        http = urllib2.urlopen(req, timeout=10)
        rsp['content'] = http.read()
    except urllib2.HTTPError, e:
        rsp['status'] = False
        rsp['code'] = e.code
        rsp['content'] = e.read()
    return rsp

from secrect_fb_api_id_sec import *
#Need fb_cid, fb_csec
def getFBAccessToken():
    url = "https://graph.facebook.com/oauth/access_token?client_id="+fb_cid+"&client_secret="+fb_csec+"&grant_type=client_credentials"
    rsp = HTTP_GET(url)
    fb_acctok = ''
    if rsp['status']:
        fb_acctok = rsp['content'].split('=')[1]
    return fb_acctok

class PostsAPIView(APIView):
    """
    List all posts, or sync posts from facebook.
    """
    def get(self, request, action='get', format='json'):
        content = {}
        statusCode = 200
        ExtraHeader = {}
        if action=='get':
            page = request.GET.get('page')
            page = int(page) if page else 1

            queryset = Post.objects.all()
            post_counts = queryset.count()
            NeedSync = True if (page*20)>=post_counts else False
            if NeedSync:
                try:
                    last_post = queryset[len(queryset)-1]
                    until = unixts(last_post.created_time)
                except:
                    until = None
                redirect_url = reverse('api:posts')+"?page="+str(page)
                url = reverse('api:posts',args=['sync'])+"?redirect="+urllib.quote(redirect_url)
                url = url+"&until="+str(until) if until else url
                return redirect(url)

            paginator = Paginator(queryset, 20)
#            offset = (page-1)*10
#            posts = PostSerializer(Post.objects.all()[offset:offset+10])
            posts = paginator.page(page)

            serializer_context = {'request': request}
            serializer = PaginatedPostSerializer(posts, context=serializer_context)
#            serializer = PaginationSerializer(instance=posts, context={'request':serializer_context})
            content = serializer.data

        elif action=='sync':
            fbid = "123103684386135"
            fb_access_token = getFBAccessToken()
            url = "https://graph.facebook.com/"+fbid+"/posts?"\
                  "fields=id,from,message,picture,link,type,status_type,object_id,created_time,likes.limit(1).summary(true),shares,"\
                  "comments.limit(1).summary(true)&access_token="+fb_access_token

            until = request.GET.get('until')
            url = url+"&until="+str(int(until)-1) if until else url
            rsp = HTTP_GET( url )
            if not rsp['status']:
                content = rsp['content']
                statusCode = rsp['code']
            else:
                posts = json.loads( rsp['content'] )
                savePostsToDB( posts )
                content['paging'] = posts['paging']
                redirect_url = urllib.unquote( request.GET.get('redirect') )
                if bool(redirect_url):
                    return redirect( redirect_url )

        else:
            content['error'] = 'unsupported action'

        response = Response(content, status=statusCode)
        for arg in ExtraHeader:
            response[arg] = ExtraHeader[arg]
        return response;

def Posts(request, action):
    format = request.GET.get('format')
    format = 'json'
    ctn_type = 'application/json; charset=UTF-8'

    fb_post_api = "https://graph.facebook.com/"+fbid+"/posts?"\
                  "fields=id,from,message,picture,link,type,status_type,object_id,created_time,likes.limit(1).summary(true),shares,"\
                  "comments.limit(1).summary(true)&access_token="+fb_access_token

    content = {}
    if action=='get':
#        posts = Post.objects.order_by('-created_time')[:10]
#        posts = Post.objects.all()[:10]
        posts = PostSerializer(Post.objects.all()[:10])
#        raw = serializers.serialize('python', posts)
#        content = [d['fields'] for d in raw]
        content = posts.data

    elif action=='sync':
        url = fb_posts_api+fb_access_token
        rsp = HTTP_GET( url )
        if rsp['code'] != 200:
            content['error'] = rsp
        else:
            posts = json.loads( rsp['content'] )
            content['paging'] = posts['paging']
            savePostsToDB( posts )

    else:
        content['error'] = 'unsupported action'

    response = HttpResponse( json.dumps(content,cls=DjangoJSONEncoder), content_type=ctn_type)
    return response
        

def detail(request, poll_id):
#    return HttpResponse("You're looking at poll %s." % poll_id)
#    try:
#        poll = Poll.objects.get(pk=poll_id)
#    except Poll.DoesNotExist:
#        raise Http404
    poll = get_object_or_404(Poll, pk=poll_id)
    return render(request, 'detail.html', {'poll': poll})


def results(request, poll_id):
#    return HttpResponse("You're looking at the results of poll %s." % poll_id)
    poll = get_object_or_404(Poll, pk=poll_id)
    return render(request, 'results.html', {'poll': poll})

def vote(request, poll_id):
#    return HttpResponse("You're voting on poll %s." % poll_id)
    p = get_object_or_404(Poll, pk=poll_id)
    try:
        selected_choice = p.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the poll voting form.
        return render(request, 'detail.html', {
            'poll': p,
            'error_message': "You didn't select a choice.",
        })
    else:
#        return HttpResponse("%s %s" % (request.POST['choice'], selected_choice) )
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(p.id,)))

