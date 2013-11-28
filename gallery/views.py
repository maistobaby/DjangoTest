from django.shortcuts import render, get_object_or_404

# Create your views here.

def index(request):
    ctx = {}
    return render(request, 'gallery/index.html', ctx)

