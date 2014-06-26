import json, csv, time, urllib2, os, hashlib, tweepy
from django.http import HttpResponse
from django.core.cache import cache
from core.models import *

def generateData(dataFile, app, source, cacheKey):
	if source == "file":
		extension = getFileExtension(dataFile)
	elif source == "url":
		dataFile, extension = fetchFileFromURL(dataFile, cacheKey)
		if dataFile == 'error':
			return HttpResponse(status=400)
	
	#sha256_hash = str(hashfile(dataFile, hashlib.sha256()))
	# if ProcessedFile.objects.filter(sha256_hash=sha256_hash).exists():
	# 	return HttpResponse("{'status': 400, 'error_message': 'This file appears to have been processed already' }", status=400, content_type="application/json")
	# else:
	# 	ProcessedFile.objects.create(sha256_hash=sha256_hash)

	if extension == ".json":
		processJSONInput(dataFile, app, cacheKey)
	elif extension == ".csv":
		processCSVInput(dataFile, app, cacheKey)

	return HttpResponse(status=200)

def processJSONInput(dataFile, app, cacheKey):
	jsonObject = json.loads(dataFile.read())
	tweetIds = []
	lineModifier = 0
	line_limit = 1500
	data = []
	offset = ""
	
	cacheData = cache.get(cacheKey)
	cacheData['state'] = 'processing'
	cacheData['progress'] = 50
	cache.set(cacheKey, cacheData)

	for index, row in enumerate(jsonObject):
		tweetData = parseTweet(row.get("id"), row.get("text"), row.get("user").get("screen_name"), row.get("created_at"), tweetIds, app)
		if tweetData:
			data.append(tweetData)
		else:
			lineModifier = lineModifier + 1
			continue

		if index-lineModifier == line_limit:
			offset = "_"+str(line_limit/1500)
			writeFile(data, app, cacheKey, offset)
			line_limit += 1500
			data = []
			print "file written at", index

	writeFile(data, app, cacheKey, offset)

def processCSVInput(dataFile, app, cacheKey):
	csvDict = csv.DictReader(dataFile)
	line_limit = 1500
	data = []
	tweetIds = []
	lineModifier = 0
	offset = ""

	cacheData = cache.get(cacheKey)
	cacheData['state'] = 'processing'
	cacheData['progress'] = 50
	cache.set(cacheKey, cacheData)

	for index, row in enumerate(csvDict):
		tweetData = parseTweet(row["tweetID"], row["message"], row["userName"], row["createdAt"], tweetIds, app)
		if tweetData:
			data.append(tweetData)
		else:
			lineModifier = lineModifier + 1
			continue

		if index-lineModifier == line_limit:
			offset = "_"+str(line_limit/1500)
			writeFile(data, app, cacheKey, offset)
			line_limit += 1500
			data = []

	writeFile(data, app, cacheKey, offset)

def parseTweet(tweetID, message, userName, creationTime, tweetIds, app):
	datarow = {}

	if tweetID:
		if tweetID in tweetIds:
			return None
		datarow["TweetID"] = tweetID

	if message:
		if 'RT ' in message:
			return None
		datarow["Tweet"] = message

	if app == 'imageclicker':
		mediaLink = checkForPhotos(tweetID)
	elif app == 'videoclicker':
		mediaLink = checkForYoutube(tweetID)

	# if mediaLink:
	# 	datarow["Location"] = mediaLink
	# 	datarow["Image-Link"] = mediaLink
	# elif app == 'imageclicker' or app == 'videoclicker':
	# 	print 'none'
	# 	return None

	if userName:
		datarow["User-Name"] = userName
	if creationTime:
		try:
			datarow["Time-stamp"] = time.strftime("%Y-%m-%d %H:%M:%S" ,time.strptime(creationTime, "%Y-%m-%dT%H:%MZ"))
		except:
			datarow["Time-stamp"] = time.strftime("%Y-%m-%d %H:%M:%S" ,time.strptime(creationTime, "%a %b %d %H:%M:%S +0000 %Y"))

	tweetIds.append(tweetID)
	return datarow

def checkForPhotos(tweetID):
	auth = tweepy.OAuthHandler('fl3lIOuMV1PJX83AbJn7cahyt', 'Kj0Qe7nmnpPAuCZH9tVpwfyT1TkA6hyZmnM4s1Wo7M0nFYxYiU')
	auth.set_access_token('161080682-fRATWfZAKIqE0DKDwJcBAoQx7Yto5q60UM2otBDl', 'a8HzOnEqDX4FkIjvl0OvFpnVQHcu9acmZR1wy9Xh2Y6wu')
	api = tweepy.API(auth)
	try:
		tweet = api.get_status(tweetID)
		media = tweet.entities['media']
		for m in media:
			if m['type'] == 'photo':
				return m['media_url']
	except Exception as e:
		print e
		print 'fail... continuing'
	return None

def checkForYoutube(tweetID):
	auth = tweepy.OAuthHandler('fl3lIOuMV1PJX83AbJn7cahyt', 'Kj0Qe7nmnpPAuCZH9tVpwfyT1TkA6hyZmnM4s1Wo7M0nFYxYiU')
	auth.set_access_token('161080682-fRATWfZAKIqE0DKDwJcBAoQx7Yto5q60UM2otBDl', 'a8HzOnEqDX4FkIjvl0OvFpnVQHcu9acmZR1wy9Xh2Y6wu')
	api = tweepy.API(auth)
	try:
		tweet = api.get_status(tweetID)
		urls = tweet.entities['urls']
		for url in urls:
			if "youtube" in url['display_url'] or "youtu.be" in url['display_url']:
				return url['display_url']
	except Exception as e:
		print e
		print 'fail... continuing'
	return None

def writeFile(data, app, cacheKey, offset=""):
	filename = app+time.strftime("%Y%m%d%H%M%S",time.localtime())+offset+'.csv'
	outputfile = open("static/output/"+filename, "w")

	cacheData = cache.get(cacheKey)
	cacheData['state'] = 'writing'
	cacheData['progress'] = 75
	cache.set(cacheKey, cacheData)

	writer = csv.DictWriter(outputfile, ["User-Name","Tweet","Time-stamp","Location","Latitude","Longitude","Image-link","TweetID"])
	writer.writeheader()
	for row in data:
		writer.writerow(row)

	cacheData = cache.get(cacheKey)
	cacheData['state'] = 'done'
	cacheData['progress'] = 100
	cache.set(cacheKey, cacheData)

	outputfile.close()

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
