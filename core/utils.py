import json, csv, time, urllib2, os, hashlib, re, logging
from django.conf import settings
from django.http import HttpResponse
from django.core.cache import cache
from core.models import *

logger = logging.getLogger(__name__)
APPID = {'textclicker': 78, 'imageclicker': 80, 'videoclicker': 82}
AIDRTRAINERAPI = "http://qcricl1linuxvm1.cloudapp.net:8084/AIDRTrainerAPI/rest/deployment/active"

def generateData(dataFile, app, source, cacheKey):
	if source == "file":
		extension = getFileExtension(dataFile)
		logger.info("uploading local AIDR file: " + dataFile.name)
	elif source == "url":
		logger.info("fetching remote AIDR file: " + dataFile)
		dataFile, extension = fetchFileFromURL(dataFile, cacheKey)
		if dataFile == 'error':
			return HttpResponse(status=400)
	
	#sha256_hash = str(hashfile(dataFile, hashlib.sha256()))
	# if ProcessedFile.objects.filter(sha256_hash=sha256_hash).exists():
	# 	return HttpResponse("{'status': 400, 'error_message': 'This file appears to have been processed already' }", status=400, content_type="application/json")
	# else:
	# 	ProcessedFile.objects.create(sha256_hash=sha256_hash)

	updateCacheData(cacheKey, 'Processing', 50)
	if extension == ".json":
		processJSONInput(dataFile, app, cacheKey)
	elif extension == ".csv":
		processCSVInput(dataFile, app, cacheKey)

	return HttpResponse(status=200)

def processJSONInput(dataFile, app, cacheKey):
	jsonObject = json.loads(dataFile.read())
	tweetIds = []
	aidr_json = []
	lineModifier = 0
	line_limit = 1500
	data = []
	offset = ""
	
	for index, row in enumerate(jsonObject):
		tweetData = parseTweet(row.get("id"), row.get("text"), row.get("user").get("screen_name"), row.get("created_at"), tweetIds, app)
		if tweetData:
			data.append(tweetData)
		else:
			lineModifier = lineModifier + 1
			continue

		updateCacheData(cacheKey, 'Writing Files', 75)

		if index-lineModifier == line_limit:
			offset = "_"+str(line_limit/1500)
			aidr_json.append(writeFile(data, app, cacheKey, offset))
			line_limit += 1500
			data = []
			print "file written at", index

	if offset:
		offset = "_"+str(line_limit/1500)
	aidr_json.append(writeFile(data, app, cacheKey, offset))
	updateAIDR(aidr_json, cacheKey)

def processCSVInput(dataFile, app, cacheKey):
	csvDict = csv.DictReader(dataFile)
	line_limit = 1500
	data = []
	tweetIds = []
	aidr_json = []
	lineModifier = 0
	offset = ""

	for index, row in enumerate(csvDict):
		tweetData = parseTweet(row["tweetID"], row["message"].decode("utf-8"), row["userName"], row["createdAt"], tweetIds, app)
		if tweetData:
			data.append(tweetData)
		else:
			lineModifier = lineModifier + 1
			continue

		updateCacheData(cacheKey, 'Writing Files', 75)

		if index-lineModifier == line_limit:
			offset = "_" + str(line_limit/1500)
			aidr_json.append(writeFile(data, app, cacheKey, offset))
			line_limit += 1500
			data = []

	if offset:
		offset = "_"+str((line_limit/1500))
	aidr_json.append(writeFile(data, app, cacheKey, offset))
	updateAIDR(aidr_json, cacheKey)

def updateAIDR(data, cacheKey):
	updateCacheData(cacheKey, 'Updating AIDR', 90)
	json_data = json.dumps(data)
	data_len = len(json_data)
	req = urllib2.Request(AIDRTRAINERAPI, json_data, {'Content-Type': 'application/json', 'Content-Length': data_len})
	try:
		f = urllib2.urlopen(req, timeout=15)
		response = f.read()
		print response
		f.close()
		logger.info("Successfully sent file(s) information to AIDR API. Information sent: " + str(data))
	except Exception as e:
		logger.error("Failed to send file(s) information to AIDR API. Error was: " + str(e) + ". Information not sent: " + str(data))
	updateCacheData(cacheKey, 'Done', 100)

def parseTweet(tweetID, message, userName, creationTime, tweetIds, app):
	datarow = {}

	if tweetID:
		if tweetID in tweetIds:
			return None
		datarow["TweetID"] = tweetID

	if message:
		if 'RT ' in message:
			return None
		try:
			datarow["Tweet"] = message.encode('ascii', 'ignore')
		except:
			try: 
				datarow["Tweet"] = message
			except Exception as e:
				logger.error("Failed to get tweet message:" + e)

		if app == 'imageclicker':
			mediaLink = checkForPhotos(message)
			if mediaLink:
				datarow["Location"] = mediaLink
				datarow["Image-Link"] = mediaLink
			else:
				return None
		elif app == 'videoclicker':
			mediaLink = checkForYoutube(message)
			if mediaLink:
				datarow["Location"] = mediaLink
				datarow["Image-Link"] = mediaLink
			else:
				return None
		
	if userName:
		datarow["User-Name"] = userName
	if creationTime:
		try:
			datarow["Time-stamp"] = time.strftime("%Y-%m-%d %H:%M:%S" ,time.strptime(creationTime, "%Y-%m-%dT%H:%MZ"))
		except:
			try:
				datarow["Time-stamp"] = time.strftime("%Y-%m-%d %H:%M:%S" ,time.strptime(creationTime, "%a %b %d %H:%M:%S +0000 %Y"))
			except Exception as e:
				logger.error("Failed to parse time of tweet: " + e + ". Original data was: " + creationTime)

	tweetIds.append(tweetID)
	return datarow

def checkForPhotos(message):
	url = getActualURL(message)
	if url:
		photoPattern = re.compile("(https://(twitter\.com)\S*(photo)\S*)")
		match = photoPattern.search(url)
		if match:
			return url
	return None

def checkForYoutube(message):
	url = getActualURL(message)
	if url:
		youtubePattern = re.compile("(http(s)?://(www\.youtube\.com)\S*)")
		match = youtubePattern.search(url)
		if match:
			return url
	return None

def getActualURL(message):
	pattern = re.compile("(http(s)?://(t\.co)\S*)")
	match = pattern.search(message)
	if match:
		link = match.group()
		return urllib2.urlopen(link).geturl()
	return None

def writeFile(data, app, cacheKey, offset=""):
	filename = app+time.strftime("%Y%m%d%H%M%S",time.localtime())+offset+'.csv'
	outputfile = open("static/output/"+filename, "w")

	writer = csv.DictWriter(outputfile, ["User-Name","Tweet","Time-stamp","Location","Latitude","Longitude","Image-link","TweetID"])
	writer.writeheader()
	for row in data:
		writer.writerow(row)

	outputfile.close()
	logger.info("Successfully wrote file. Name: " + filename)
	return { "fileUrl": str(settings.SITE_URL + "static/output/" + filename), "appId": APPID[app] }

def updateCacheData(cacheKey, state, progress):
	cacheData = cache.get(cacheKey)
	cacheData['state'] = state
	cacheData['progress'] = progress
	cache.set(cacheKey, cacheData)

def fetchFileFromURL(url, cacheKey):
	cache.set(cacheKey, {
            'state': 'uploading',
            'progress': 25
        })

	response = urllib2.urlopen(url)
	if response.headers.type == 'application/json':
		return response, '.json'
	elif response.headers.type == 'text/csv':
		return response, '.csv' 
	else:
		logger.error("Failed attempting to get file from url: " + url + ". Incorrect response type.")
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
