from django.shortcuts import render, redirect
from django.http import HttpResponse
import utils
import urllib2

def index(request):
	return render(request, "core/index.html")

def downloadPage(request):
	if request.method == "POST":
		if request.FILES.get('data-file'):
			return utils.generateData(request.FILES.get('data-file'), "file")
		elif request.POST.get("data-url"):
			return utils.generateData(request.POST.get("data-url"), "url")
	else:
		redirect('index')

# Fetch the applist from AIDR API
# CORS issue, can't fetch directly from front-end
def getAppList(request):
	try:
		appList = urllib2.urlopen("http://pybossa-dev.qcri.org/AIDRTrainerAPI/rest/deployment/active")
		responseString = appList.read()
		
		#backup the applist locally
		appListFile = open('static/fallback/applist.json', 'w')
		appListFile.write(responseString)
		appListFile.close()

		return HttpResponse(responseString, status=200, content_type="application/json")
	except:
		appList = urllib2.urlopen("http://localhost:8000/static/fallback/applist.json")
		return HttpResponse(appList.read(), status=200, content_type="application/json")