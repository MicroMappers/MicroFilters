from django.shortcuts import render, redirect
from django.core.cache import cache
from celery.result import AsyncResult
from celery import Task
from django.http import HttpResponse, HttpResponseServerError 
import utils, urllib2, json, os

Progress = 0

def index(request):
	return render(request, "core/index.html")

def downloadPage(request):
	if request.method == "POST":
		cacheKey = "%s_%s" % (request.META['REMOTE_ADDR'], request.GET.get("X-Progress-ID") )
		if request.FILES.get('data-file'):
			return utils.generateData(request.FILES.get('data-file'), request.POST.get('app'), request.POST.get('appID'), "file", cacheKey)
		elif request.POST.get("data-url"):
			return utils.generateData(request.POST.get("data-url"), request.POST.get('app'), request.POST.get('appID'), "url", cacheKey)
		else:
			return HttpResponse(status=400)
	else:
		return 	HttpResponse(status=405)

def getFileList(request, userNo=None):
	# Task.update_state(task_id=Task(userNo), state='PROGRESS', meta={'current': 300, 'total': 3000})
	# AsyncResult(userNo).processing_progress(10)
	print AsyncResult(userNo).state.meta
	files = []
	top_path = os.path.dirname(os.path.abspath(__file__))
	path = os.path.join(top_path, '../static/output')
	os.chdir(path)
	for clicker_file in os.listdir("."):
		files.append({'name': clicker_file, 'url': '/static/output/' + clicker_file})

	return render(request, 'core/filelist.html', {'files': files})

# Fetch the applist from AIDR API
# CORS issue, can't fetch directly from front-end
def getAppList(request):
	try:
		appList = urllib2.urlopen("http://qcricl1linuxvm2.cloudapp.net:8081/AIDRTrainerAPI/rest/deployment/active", timeout=15)
		responseString = appList.read()
		if responseString == []:
			raise ValueError
		#backup the applist locally
		appListFile = open('static/fallback/applist.json', 'w')
		appListFile.write(responseString)
		appListFile.close()

		return HttpResponse(responseString, status=200, content_type="application/json")
	except:
		appList = urllib2.urlopen("http://localhost:8000/static/fallback/applist.json")
		return HttpResponse(appList.read(), status=200, content_type="application/json")


def uploadProgress(request, uuid=None):
	"""
	Return JSON object with information about the progress of an upload.
	"""
	global Progress
	cache_key = "%s_%s" % (request.META['REMOTE_ADDR'], uuid)
	data = cache.get(cache_key)
	if data:
		return HttpResponse(json.dumps(data))
	if Progress < 50:
		Progress += 1
	return HttpResponse(json.dumps({"progress": Progress, "received": 0, "size": 0, "state": "Processing"}))
