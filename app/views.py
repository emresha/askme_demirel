from django.shortcuts import render
from askme_demirel.settings import BASE_DIR

# Create your views here.

def index(request):
    return render(request, "index.html")
