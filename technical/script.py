#!/usr/bin/python
from github import Github
from collections import defaultdict
import sys
import json
import time
from datetime import datetime as dt 

gh = None

def check():
	global gh
	gh.get_rate_limit()
	rate = gh.rate_limiting
	if rate[0] > 100: return
	reset = gh.rate_limiting_resettime 
	t = dt.fromtimestamp(reset).strftime('%Y-%m-%d %H:%M:%S')
	sys.stdout.write("\nOut of limits. [{}] Waiting".format(t)) 
	while (True):
		sys.stdout.flush()
		gh.get_rate_limit()
		rate = gh.rate_limiting
		if rate[0] > 100: break
		time.sleep(60)
		sys.stdout.write(".")
	sys.stdout.write("\n")


# Naive matrix mul
# numpy is intentionally not used here
def matmult(a,b):
	zip_b = zip(*b)
	return [[sum(ele_a*ele_b for ele_a, ele_b in zip(row_a, col_b)) 
			     for col_b in zip_b] for row_a in a]

# Naive matrix trans
# numpy is intentionally not used here
def trans(m):
	height = len(m)
	width = len(m[0])
	return [[ m[row][col] for row in range(0,height) ] for col in range(0,width) ]

def list_files(repo):
	master = repo.get_branch('master')
	root = master.commit.commit.tree
	files = []
	def process_tree(node, prefix):
		for n in node.tree:
			check()
			if n.type == 'tree':
				path = '{}{}/'.format(prefix, n.path)
				subnode = repo.get_git_tree(n.sha)
				process_tree(subnode, path)
			else:
				files.append(prefix + n.path)
	process_tree(root, '')
	return files

def collect_comments(repo, matrix, peoplelist):
	idx = {author:id for id, author in enumerate(peoplelist)}
	def process(comments):
		users = set()
		for c in comments: 
			check()
			login = c.user.login
			if login in idx:
				users.add(idx[login])
			else: print("Who's this guy: " + login)
		for i in users:
			for j in users:
				matrix[i][j] += 1
	
	#iterate pull requests
	for pull in repo.get_pulls():
		check()
		process(pull.get_comments())
	#iterate comments
	for issue in repo.get_issues():
		check()
		process(issue.get_comments())
	return matrix

def build_matrix(repo , fileindex):
	l = len(fileindex)
	# files changed within the same commit
	files2files = [[0]*l for i in range(l)]
	# list of files changed in the commit
	commits = defaultdict(list)
	# list of people commented this commit
	comments = defaultdict(set)
	# list of people
	peopleindex  = []
	# commit to author mapping
	commit2author = {} 
	# for each file in the repo
	# iterate over its history commits
	for path,idx in fileindex.iteritems():
		for c in repo.get_commits(path=path):
			for comm in c.get_comments():
				check()
				comments[c.sha].add(comm.user.login)
			commits[c.sha].append(idx)
			if c.author is None:
				sys.stderr.write("{}@{} has no author\n".format(path, c.sha))
				continue
			commit2author[c.sha] = c.author.login
	peoplelist = list(set(commit2author.values()))
	peopleindex = {author:idx for idx, author in enumerate(peoplelist)} 
	for idx, author in enumerate(peoplelist): 
		print idx, "\t", author
	n = len(peopleindex)
	# people2file[i][j] for person i and file j
	people2file = [[0]*l for i in range(n)]
	for sha, items in commits.iteritems():
		for i in items:
			for j in items:
				files2files[i][j] +=  1
			if sha in commit2author:
				author_idx = peopleindex[commit2author[sha]]
				people2file[author_idx][i] += 1
	# comments_matrix[i][j] = counter 
	# means:
	# person i has interacted with person j counter times
	comments_matrix = [[0]*n for i in range(n)]
	for sha, people in comments.iteritems():
		for dev1 in people:
			i = peopleindex[dev1]
			for dev2 in people:
				j = peopleindex[dev2]
				comments_matrix[i][j] += 1

	return files2files, people2file, peoplelist, comments_matrix

def main():
	g = Github(login_or_token='74ff4320f6b54cc4bf74dc4f006661a782e31418')
	global gh
	gh = g
	user_str, repo_str = sys.argv[1].split("/")
	check()
	u = g.get_user(user_str)
	check()
	repo = u.get_repo(repo_str)
	print "## List all files in {} repo for the latest commit in master".format(repo_str)
	check()
	filelist = list_files(repo)
	print "## Build filepath-to-number index"
	fileindex = {path: idx for idx, path in enumerate(filelist)}
	for idx, path in enumerate(filelist):
		print idx, "\t", path
	print "## Iterating over files and commits. Please wait." 
	check()
	matrix, people2file, peoplelist, comments_matrix  = build_matrix(repo, fileindex)
	print "## Collecting comments."
	check()
	comments_matrix = collect_comments(repo, comments_matrix, peoplelist)
	print "## Requirements matrix: files to files"
	for row in matrix:
		print ''.join('%4s' % i for i in row)
	print "## Authors to files matrix"
	for row in people2file:
		print ''.join('%4s' % i for i in row)
	sys.stderr.write('Rate limit: {}\n'.format(g.rate_limiting))
	print "## Comments interaction" 
	for row in comments_matrix:
		print ''.join('%4s' % i for i in row)
	print "## Calculating requirement natrix and writing results to file"
	# requirements = p2f * f2f * f*p
	result = matmult(people2file, matmult(matrix, trans(people2file)))
	for row in result:
		print ''.join('%6s' % i for i in row)
	## Writing everything to json
	data = {}
	data["files"] = filelist
	data["people"] = peoplelist
	data["people2files"] = people2file
	data["files2files"] = matrix
	data["requirements"] = result
	data["comments_matrix"] = comments_matrix
	filename = "output_data/" + sys.argv[1].replace("/","-")
	with open(filename, 'w+') as f:
		json.dump(data, f)
	print "## Results written to {}".format(filename)
main()

