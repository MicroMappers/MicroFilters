from __future__ import absolute_import
from celery import shared_task, task, app, Task, current_task
from celery.result import AsyncResult
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse
from django.core.cache import cache
import zipfile, os, shutil, re, time, logging, json, csv, urllib2, hashlib
from core.models import *

logger = logging.getLogger(__name__)
AIDRTRAINERAPI = "http://qcricl1linuxvm2.cloudapp.net:8081/AIDRTrainerAPI/rest/source/save"

@shared_task
def async_processInput(dataFile, extension, app, appId, cacheKey):
	tweetIds = []
	aidr_json = []
	lineModifier = 0
	line_limit = 1500
	data = []
	offset = ""
	has_entries = False

	print 'hello there'
	print async_processInput.request.id

	if extension == '.csv':
		parsable_object = list(csv.DictReader(dataFile))
		total_lines = len(parsable_object)
	else:
		parsable_object = json.loads(dataFile.read())
		total_lines = len(parsable_object)

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

		current_task.update_state(state='PROGRESS', meta={'current': index, 'total': total_lines})
	
	if not has_entries:
		updateCacheData(cacheKey, 'Error', 100)
		return HttpResponse(status=400)

	if offset:
		offset = "_"+str(line_limit/1500)
	aidr_json.append(writeFile(data, app, appId, cacheKey, offset))
	updateAIDR(aidr_json, cacheKey)
	return HttpResponse(status=200)

def parseRow(row, extension, tweetIds, app):
	if extension == ".json":
		return parseTweet(row.get("id"), row.get("text"), row.get("user").get("screen_name"), row.get("created_at"), tweetIds, app)
	elif extension == ".csv":
		return parseTweet(row["tweetID"], row["message"].decode("utf-8"), row["userName"], row["createdAt"], tweetIds, app)

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
				logger.error("Failed to parse time of tweet: " + str(e) + ". Original data was: " + str(creationTime))

	tweetIds.append(tweetID)
	return datarow

def checkForPhotos(message):
	url = getActualURL(message)
	if url:
		photoPattern = re.compile("(http(s)?://(twitter\.com)\S*(photo)\S*)")
		instagramPattern = re.compile("(http(s)?://(instagram\.com)\S*)")
		match1 = photoPattern.search(url)
		match2 = instagramPattern.search(url)
		if match1 or match2:
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
		try:
			expandedUrl = urllib2.urlopen(link, timeout=7).geturl()
			return expandedUrl
		except Exception as e:
			print e
	return None

def writeFile(data, app, appId, cacheKey, offset="", taskId=""):
	filename = app + time.strftime("%Y%m%d%H%M%S", time.localtime()) + offset + '.csv'
	outputfile = open("static/output/" + taskId + filename, "w")

	writer = csv.DictWriter(outputfile, ["User-Name","Tweet","Time-stamp","Location","Latitude","Longitude","Image-Link","TweetID"])
	writer.writeheader()
	for row in data:
		try:
			writer.writerow(row)
		except Exception as e:
			print e

	outputfile.close()
	logger.info("Successfully wrote file. Name: " + filename)
	return { "fileURL": str(settings.SITE_URL + "static/output/" + filename), "appID":  int(appId) }

def updateAIDR(data, cacheKey):
	updateCacheData(cacheKey, 'Updating AIDR', 90)
	json_data = json.dumps(data)
	data_len = len(json_data)
	req = urllib2.Request(AIDRTRAINERAPI, json_data, {'Content-Type': 'application/json', 'Content-Length': data_len})
	try:
		f = urllib2.urlopen(req, timeout=15)
		response = f.read()
		print 'AIDR Responded with:'
		print response
		f.close()
		logger.info("Successfully sent file(s) information to AIDR API. Information sent: " + str(data))
	except Exception as e:
		logger.error("Failed to send file(s) information to AIDR API. Error was: " + str(e) + ". Information not sent: " + str(data))
	updateCacheData(cacheKey, 'Done', 100)

def updateCacheData(cacheKey, state, progress):
	try:
		cacheData = cache.get(cacheKey)
		cacheData['state'] = state
		cacheData['progress'] = progress
		cache.set(cacheKey, cacheData)
	except:
		pass