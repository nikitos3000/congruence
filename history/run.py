#!/usr/bin/python
import utils
import sys
from github import Github
g = Github(login_or_token='74ff4320f6b54cc4bf74dc4f006661a782e31418')
repo = g.get_repo("xoxco/jQuery-Tags-Input") #https://github.com/CocoaPods/Specs
users = []
for u in repo.get_contributors():
	users.append(u.login)
	print u.login





query = """
SELECT repository_url
FROM [githubarchive:github.timeline]
WHERE (type="PushEvent" OR type="PullRequestEvent" OR type="MemberEvent") AND actor_attributes_login="{}"
GROUP BY repository_url
IGNORE CASE;"""

#users = ['kevinsawicki','jdalton','substack', 'mikermcneil', 'jonathanong', 'michalbe', 'balupton']
#users = ['michaelklishin','irrationalfab', 'youknowone', 'siuying', 'Keithbsmiley', 'mattt','seivan','romaonthego']
user_repos = {}

sc = utils.SimpleClient()
for user in users:
	repos = set()
	for x in  sc.runSyncQuery(query.format(user)):
		repos.add(x[0])
	user_repos[user] = repos


def measure_history(u1, u2):
	return len(u1.intersection(u2))
	


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
