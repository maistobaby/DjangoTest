# Create your views here.

from django.http import HttpResponseRedirect, HttpResponse
# from django.template import RequestContext, loader
from django.http import Http404
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.utils import timezone

from polls.models import Poll, Choice
from django.core import serializers

class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_poll_list'
    def get_queryset(self):
        """Return the last five published polls."""
#        return Poll.objects.order_by('-pub_date')[:5]
        return Poll.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:5]

class DetailView(generic.DetailView):
    model = Poll
    template_name = 'polls/detail.html'
    def get(self, request, *args, **kwargs):
        session = request.session
        session['test'] = 'test~~~'
#        if 'test' in session:
#           del session['test']
        sdata = session.load()
        data = request.COOKIES.get('test')
        pk = kwargs.get(self.pk_url_kwarg, None)
        pb = kwargs.get('pb', None)
        kwarg = self.pk_url_kwarg
#        poll = Poll.objects.filter(pk=pk).get()
        poll = Poll.objects.all()
        json_serializer = serializers.get_serializer("json")()
#        json_serializer.serialize(poll, ensure_ascii=False, stream=response)
        data = serializers.serialize("json", poll)
        response = HttpResponse(data, content_type="application/json; charset=UTF-8")
        return response

        poll = Poll.objects.get(pk=pb)
        response = render(request, self.template_name, {'poll': poll, 'kwarg': kwarg, 'sdata':sdata, 'data':data } )

        response.set_cookie('test','YAYAY~', 5*60);
        return response;
    def get_queryset(self):
        """
        Excludes any polls that aren't published yet.
        """
        return Poll.objects.filter(pub_date__lte=timezone.now())

class ResultsView(generic.DetailView):
    model = Poll
    template_name = 'polls/results.html'


def index(request):
#    return HttpResponse("Hello, world. You're at the poll index.")
    latest_poll_list = Poll.objects.order_by('-pub_date')[:5]
#    output = ', '.join([p.question for p in latest_poll_list])
#    return HttpResponse(output)
#    template = loader.get_template('polls/index.html')
#    context = RequestContext(request, {
#        'latest_poll_list': latest_poll_list,
#    })
#    return HttpResponse(template.render(context))
    context = {'latest_poll_list': latest_poll_list}
    return render(request, 'polls/index.html', context)

def detail(request, poll_id):
#    return HttpResponse("You're looking at poll %s." % poll_id)
#    try:
#        poll = Poll.objects.get(pk=poll_id)
#    except Poll.DoesNotExist:
#        raise Http404
    poll = get_object_or_404(Poll, pk=poll_id)
    return render(request, 'polls/detail.html', {'poll': poll})


def results(request, poll_id):
#    return HttpResponse("You're looking at the results of poll %s." % poll_id)
    poll = get_object_or_404(Poll, pk=poll_id)
    return render(request, 'polls/results.html', {'poll': poll})

def vote(request, poll_id):
#    return HttpResponse("You're voting on poll %s." % poll_id)
    p = get_object_or_404(Poll, pk=poll_id)
    try:
        selected_choice = p.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the poll voting form.
        return render(request, 'polls/detail.html', {
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

