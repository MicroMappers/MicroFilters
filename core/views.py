from django.shortcuts import render, redirect
import hashlib, os
import utils

def index(request):
	
	return render(request, "core/index.html")

def download_page(request):
	if request.method == "POST":
		if request.FILES.get('data-file'):
			return utils.generateData(request.FILES.get('data-file'), "file")
		elif request.POST.get("data-url"):
			return utils.generateData(request.POST.get("data-url"), "url")
	else:
		redirect('index')