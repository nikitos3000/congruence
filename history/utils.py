#!/usr/bin/python

import httplib2

from apiclient.discovery import build
from apiclient.errors import HttpError

from oauth2client.client import SignedJwtAssertionCredentials
from oauth2client.client import AccessTokenRefreshError


class SimpleClient:
	def __init__(self):
		self.PROJECT_ID = 'astral-sunbeam-600'
		SAE = self.SERVICE_ACCOUNT_EMAIL = '766106295283-mvbdl76eduioip1aa96u9b0h6d9kut4n@developer.gserviceaccount.com'

		f = file('cefb7ce33f1376da26ff6f33a7c8397fbf8fee68-privatekey.p12', 'rb')
		key = self.key = f.read()
		f.close()

		cred = self.credentials = SignedJwtAssertionCredentials(
			SAE,
			key,
			scope='https://www.googleapis.com/auth/bigquery')

		http = self.http = httplib2.Http()
		self.http = cred.authorize(http)

		self.service = build('bigquery', 'v2', http=http)


	def runSyncQuery (self, query, timeout=0):
		projectId = self.PROJECT_ID
		service = self.service
		print 'timeout:%d' % timeout
		jobCollection = service.jobs()
		queryData = {'query':query,
				     'timeoutMs':timeout}

		queryReply = jobCollection.query(projectId=projectId,
				                         body=queryData).execute()

		jobReference=queryReply['jobReference']

		# Timeout exceeded: keep polling until the job is complete.
		while(not queryReply['jobComplete']):
		  print 'Job not yet complete...'
		  queryReply = jobCollection.getQueryResults(
				              projectId=jobReference['projectId'],
				              jobId=jobReference['jobId'],
				              timeoutMs=timeout).execute()

		# If the result has rows, print the rows in the reply.
		if('rows' in queryReply):
		  print 'has a rows attribute'
		  printTableData(queryReply, 0)
		  currentRow = len(queryReply['rows'])

		  # Loop through each page of data
		  while('rows' in queryReply and currentRow < queryReply['totalRows']):
			queryReply = jobCollection.getQueryResults(
				              projectId=jobReference['projectId'],
				              jobId=jobReference['jobId'],
				              startIndex=currentRow).execute()
			if('rows' in queryReply):
			  printTableData(queryReply, currentRow)
			  currentRow += len(queryReply['rows'])




def printTableData(data, startIndex):
  for row in data['rows']:
    rowVal = []
    for cell in row['f']:
        rowVal.append(cell['v'])
    print 'Row %d: %s' % (startIndex, rowVal)
    startIndex +=1


