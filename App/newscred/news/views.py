from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse


def newsview(request):
	tweets = ['asdasd','awerqwr','tag']
	return render(request,'tweet.html',{'tweets':tweets})
