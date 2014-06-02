#!/usr/bin/python
from github import Github
import sys

g = Github(login_or_token='74ff4320f6b54cc4bf74dc4f006661a782e31418')
u = g.get_user(sys.argv[1])
for repo in u.get_repos():
	print repo.name

print '-'*23 + "\nRate limit: %s" % (g.rate_limiting,)
