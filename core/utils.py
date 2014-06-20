import json, csv, time, urllib2
from django.http import HttpResponse
import os

def generateData(dataFile, source):
	if source == "file":
		extension = getFileExtension(dataFile)
	elif source == "url":
		dataFile, extension = fetchFileFromURL(dataFile)
		if dataFile == 'error':
			return HttpResponse("{'status': 400, 'error_message': 'URL does not have a csv of json endpoint' }",status=400, content_type="application/json")
	data = []
	if extension == ".json":
		datarow = {}
		jsonObject = json.loads(dataFile.read())
		if jsonObject.get("user").get("screen_name"):
			datarow["User-Name"] = jsonObject.get("user").get("screen_name")
		if jsonObject.get("text"):
			datarow["Tweet"] = jsonObject.get("text")

		if jsonObject.get("created_at"):
			datarow["Time-stamp"] = time.strftime("%Y-%m-%d %H:%M:%S" ,time.strptime(jsonObject.get('created_at'), "%a %B %d %H:%M:%S +0000 %Y"))

		if jsonObject.get("id"):
			datarow["TweetID"] = jsonObject.get("id")

		data.append(datarow)

		response = writeFile(data)

	elif extension == ".csv":
		csvDict = csv.DictReader(dataFile)
		for row in csvDict:
			datarow = {}
			if row["userName"]:
				datarow["User-Name"] = row["userName"]
			if row["message"]:
				datarow["Tweet"] = row["message"]
			if row["createdAt"]:
				datarow["Time-stamp"] = time.strftime("%Y-%m-%d %H:%M:%S" ,time.strptime(row["createdAt"], "%Y-%m-%dT%H:%MZ"))
			if row["tweetID"]:
				datarow["TweetID"] = row["tweetID"]
			data.append(datarow)

			response = writeFile(data)
	return response

def writeFile(data):
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="output.csv"'

	writer = csv.DictWriter(response, ["User-Name","Tweet","Time-stamp","Location","Latitude","Longitude","Image-link","TweetID"])
	writer.writeheader()
	for row in data:
		writer.writerow(row)

	return response

def fetchFileFromURL(url):
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