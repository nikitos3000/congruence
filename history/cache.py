import unittest
import json
import sys
import os
import datetime
import time
FOLDER = "cached_data"

def timestamp():
	ts = time.time()
	return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

def lookup(users, user_repos):
	n_users = []
	for u in users:
		filepath = os.path.join(FOLDER, "{}.json".format(u))
		if os.path.exists(filepath):
			with open(filepath) as f:
				j = json.load(f)
				user_repos[u] = j["repos"]
		else:
			n_users.append(u)
	return n_users

def store(user_repos):
	for u, repos in user_repos.iteritems():
		filepath = os.path.join(FOLDER, "{}.json".format(u))
		if not os.path.exists(filepath):
			with open(filepath, 'w') as f:
				json.dump(
					{"repos": repos,
					 "login": u,
					 "time" : timestamp()}
					, f)


class UnitTesting(unittest.TestCase):
    def test_1(self):
	users = ['a', 'b', 'c']
	user_repos = {
		'a': ['1', '2', '3'],
		'b': ['2', '3', '4']
		}
	store(user_repos)
	repos = {}
	users = lookup(users, repos)
	self.assertEqual(repos, user_repos)
	self.assertEqual(users, ['c'])

if __name__ == '__main__':
    unittest.main()
