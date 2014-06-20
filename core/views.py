from django.shortcuts import render, redirect
import hashlib, os
import utils

def index(request):
	
	return render(request, "core/index.html")

def download_page(request):
	if request.method == "POST":
		datafile = request.FILES.get('data-file')
		return utils.generateData(datafile)
	else:
		redirect('index')