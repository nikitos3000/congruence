#!/usr/bin/python
import utils
import sys
from github import Github
from collections import defaultdict
import cache
import json

g = Github(login_or_token='74ff4320f6b54cc4bf74dc4f006661a782e31418')
repo = g.get_repo(sys.argv[1]) 
print repo
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
data = {}
data["users"] = users
data["repos"] = user_repos
data["timestamp"] = cache.timestamp()
l = len(users)
matrix = [[0]*l for i in range(l)]

for i, u1 in enumerate(users):
	sys.stdout.write("{}\t".format(u1.ljust(10)))
	for j, u2 in enumerate(users):
		r1 = user_repos[u1]
		r2 = user_repos[u2]
		m = measure_history(r1,r2)
		matrix[i][j] = m
		sys.stdout.write("| {}\t".format(m))
	sys.stdout.write("\n")
data["matrix"] = matrix
with open("output_data/" + sys.argv[1].replace("/","-") + ".json", 'w+') as f:
	json.dump(data, f)

