#!/usr/bin/python

import httplib2

from apiclient.discovery import build
from apiclient.errors import HttpError

from oauth2client.client import SignedJwtAssertionCredentials
from oauth2client.client import AccessTokenRefreshError

class IterableReply:
	def __init__(self, jobCollection, jobReference):
		self.jc = jobCollection
		self.jr = jobReference
		self.currentRow = 0
		self.currentBase = 0
		self.reply = self.getReply()
		
	def getReply(self):
		 q = self.jc.getQueryResults(
						projectId=self.jr['projectId'],
						jobId=self.jr['jobId'],
						startIndex=self.currentBase + self.currentRow).execute()
		 if 'rows' not in q:
			 self.data = []
		 else:
			 self.data = q["rows"]
		 self.currentBase += self.currentRow
		 self.currentRow = 0
		 return q

	def __iter__(self):	
		return self

	def next(self):
		if len(self.data) == 0:
			raise StopIteration
		if ('rows' in self.reply and self.currentRow + self.currentBase < self.reply['totalRows']):
			if self.currentRow == len(self.data):
				self.query = self.getReply()
				if len(self.data) == 0:
					raise StopIteration
			row = self.data[self.currentRow]
			rowVal = []
			for cell in row['f']:
				rowVal.append(cell['v'])
			self.currentRow += 1
			return rowVal
		else:
			raise StopIteration

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
		return IterableReply(jobCollection, jobReference)

