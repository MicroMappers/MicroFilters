import json, csv, time, urllib2
from django.http import HttpResponse
import os

def generateData(dataFile, app, source):
	if source == "file":
		extension = getFileExtension(dataFile)
	elif source == "url":
		dataFile, extension = fetchFileFromURL(dataFile)
		if dataFile == 'error':
			return HttpResponse("{'status': 400, 'error_message': 'URL does not have a csv of json endpoint' }",status=400, content_type="application/json")
	
	if extension == ".json":
		processJSONInput(dataFile, app)

	elif extension == ".csv":
		processCSVInput(dataFile, app)

	return HttpResponse("{ 'message': 'Files created succesfully' }",status=200, content_type="application/json")

def processJSONInput(dataFile, app):
	jsonObject = json.loads(dataFile.read())
	datarow = {}
	line_limit = 1500
	data = []
	offset = ""
	
	for index, row in enumerate(jsonObject):
		if row.get("user").get("screen_name"):
			datarow["User-Name"] = row.get("user").get("screen_name")
		if row.get("text"):
			datarow["Tweet"] = row.get("text")

		if row.get("created_at"):
			datarow["Time-stamp"] = time.strftime("%Y-%m-%d %H:%M:%S" ,time.strptime(row.get('created_at'), "%a %B %d %H:%M:%S +0000 %Y"))

		if row.get("id"):
			datarow["TweetID"] = row.get("id")
		data.append(datarow)

		if index == line_limit:
			offset = "_"+str(line_limit/1500)
			writeFile(data, app, offset)
			line_limit += 1500
			data = []
			print "file written at", index

	writeFile(data, app, offset)

def processCSVInput(dataFile, app):
	csvDict = csv.DictReader(dataFile)
	datarow = {}
	line_limit = 1500
	data = []
	offset = ""

	for index, row in enumerate(csvDict):
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

		if index == line_limit:
			offset = "_"+str(line_limit/1500)
			writeFile(data, app, offset)
			line_limit += 1500
			data = []

	writeFile(data, app, offset)


def writeFile(data, app, offset=""):
	filename = app+time.strftime("%Y%m%d%H%M%S",time.localtime())+offset+'.csv'
	outputfile = open("static/output/"+filename, "w")

	writer = csv.DictWriter(outputfile, ["User-Name","Tweet","Time-stamp","Location","Latitude","Longitude","Image-link","TweetID"])
	writer.writeheader()
	for row in data:
		writer.writerow(row)

	outputfile.close()
	

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

def getCSVRowCount(csvDict):
	rows = list(csvDict)
	return len(rows)