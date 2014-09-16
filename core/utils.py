import json, csv, time, urllib2, os, hashlib, re, logging
from urllib2 import Request, urlopen, URLError
from django.conf import settings
from django.http import HttpResponse
from django.core.cache import cache
from celery import Celery
from core.tasks import *
from core.models import *

logger = logging.getLogger(__name__)

def generateData(dataFile, app, appId, source, cacheKey):
	if source == "file":
		extension = getFileExtension(dataFile)
		logger.info("uploading local AIDR file: " + dataFile.name)
	elif source == "url":
		logger.info("fetching remote AIDR file: " + dataFile)
		dataFile, extension = fetchFileFromURL(dataFile, cacheKey)
		if dataFile == 'error':
			return HttpResponse(status=400)

	if appId == 'undefined':
		appId = 0 

	#sha256_hash = str(hashfile(dataFile, hashlib.sha256()))
	# if ProcessedFile.objects.filter(sha256_hash=sha256_hash).exists():
	# 	return HttpResponse("{'status': 400, 'error_message': 'This file appears to have been processed already' }", status=400, content_type="application/json")
	# else:
	# 	ProcessedFile.objects.create(sha256_hash=sha256_hash)

	updateCacheData(cacheKey, 'Processing', 50)

	if app == 'textclicker':
		return processInput(dataFile, extension, app, appId, cacheKey)
	else:
		result = async_processInput.delay(dataFile, extension, app, appId, cacheKey)
		# print result.debug_task()
		return HttpResponse("/listFiles/" + result.id, status=303)

def processInput(dataFile, extension, app, appId, cacheKey):
	tweetIds = []
	aidr_json = []
	lineModifier = 0
	line_limit = 1500
	data = []
	offset = ""
	has_entries = False

	if extension == ".json":
		parsable_object  = json.loads(dataFile.read())
	elif extension == ".csv":
		parsable_object = csv.DictReader(dataFile)

	for index, row in enumerate(parsable_object):
		has_entries = True

		tweetData = parseRow(row, extension, tweetIds, app);
		
		if tweetData:
			data.append(tweetData)
		else:
			lineModifier = lineModifier + 1
			continue

		updateCacheData(cacheKey, 'Writing Files', 75)

		if index-lineModifier == line_limit:
			offset = "_" + str(line_limit/1500)
			aidr_json.append(writeFile(data, app, appId, cacheKey, offset))
			line_limit += 1500
			data = []
			
	if not has_entries:
		updateCacheData(cacheKey, 'Error', 100)
		return HttpResponse(status=400)

	if offset:
		offset = "_"+str(line_limit/1500)
	aidr_json.append(writeFile(data, app, appId, cacheKey, offset))
	updateAIDR(aidr_json, cacheKey)
	return HttpResponse(status=200)

def fetchFileFromURL(url, cacheKey):
	cache.set(cacheKey, {
        'state': 'Uploading',
        'progress': 25
    })
	req = Request(url)
	try:
		response = urllib2.urlopen(url)
		if response.headers.type == 'application/json':
			return response, '.json'
		elif response.headers.type == 'text/csv':
			return response, '.csv'
		elif response.headers.type == 'application/octet-stream' and url[-4:] == 'json':
			return response.read(), '.json'
		elif response.headers.type == 'application/octet-stream' and url[-3:] == 'csv':
			return response, '.csv'
	except Exception as e:
		logger.error("Failed attempting to get file from url: " + url + ". Error was " + e)
	return 'error', 'error'

def getFileExtension(dataFile):
		dataFileName, extension = os.path.splitext(dataFile.name)
		return extension

def hashfile(afile, hasher, blocksize=65536):
	buf = afile.read(blocksize)
	while len(buf) > 0:
		hasher.update(buf)
		buf = afile.read(blocksize)
	return hasher.hexdigest()

def getCSVRowCount(csvDict):
	rows = list(csvDict)
	return len(rows)
