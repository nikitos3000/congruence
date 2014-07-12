#!/usr/bin/python
import utils
import sys
from github import Github
from collections import defaultdict
import cache

g = Github(login_or_token='74ff4320f6b54cc4bf74dc4f006661a782e31418')
repo = g.get_repo(sys.argv[1]) #https://github.com/CocoaPods/Specs
users = []
for u in repo.get_contributors():
	users.append(u.login)
	print u.login




QUERY = """
SELECT repository_url, actor_attributes_login
FROM [githubarchive:github.timeline]
WHERE type IN ("PushEvent", "PullRequestEvent", "MemberEvent") AND actor_attributes_login in ({})
GROUP BY repository_url, actor_attributes_login
IGNORE CASE;
"""
#users = ['michaelklishin','irrationalfab', 'youknowone', 'siuying', 'Keithbsmiley', 'mattt','seivan','romaonthego']
user_repos = defaultdict(list) 
# Trying to lookup in cache
newusers = cache.lookup(users, user_repos)
print "{} users found in cache".format(len(users) - len(newusers))

sc = utils.SimpleClient()
query = QUERY.format(','.join(["'{}'".format(x) for x in newusers]))
repos = set()
if len(newusers) != 0 :
	for x in  sc.runSyncQuery(query):
		repos.add(x[0])
		user_repos[x[1]].append(x[0])
	# Store users in cache
	cache.store(user_repos)


def measure_history(u1, u2):
	return len(set(u1).intersection(set(u2)))
	
sys.stdout.write("{}\t".format(' '.ljust(10)))
for u in users:
	sys.stdout.write("| {} ".format(u.ljust(5)[:5]))
sys.stdout.write("\n")
for u1 in users:
	sys.stdout.write("{}\t".format(u1.ljust(10)))
	for u2 in users:
		r1 = user_repos[u1]
		r2 = user_repos[u2]
		m = measure_history(r1,r2)
		sys.stdout.write("| {}\t".format(m))
	sys.stdout.write("\n")
