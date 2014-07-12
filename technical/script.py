#!/usr/bin/python
from github import Github
from collections import defaultdict
import sys
import json


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
			if n.type == 'tree':
				path = '{}{}/'.format(prefix, n.path)
				subnode = repo.get_git_tree(n.sha)
				process_tree(subnode, path)
			else:
				files.append(prefix + n.path)
	process_tree(root, '')
	return files

def build_matrix(repo , fileindex):
	l = len(fileindex)
	matrix = [[0]*l for i in range(l)]
	commits = defaultdict(list)
	peopleindex  = [] 
	commit2author = {} 
	for path,idx in fileindex.iteritems():
		for c in repo.get_commits(path=path):
			commits[c.sha].append(idx)
			if c.author is None:
				sys.stderr.write(
					"{}@{} has no author\n".format(path, c.sha))
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
				matrix[i][j] +=  1
			if sha in commit2author:
				author_idx = peopleindex[commit2author[sha]]
				people2file[author_idx][i] += 1
	return matrix, people2file, peoplelist

def main():
	g = Github(login_or_token='74ff4320f6b54cc4bf74dc4f006661a782e31418')
	user_str, repo_str = sys.argv[1].split("/")
	u = g.get_user(user_str)
	repo = u.get_repo(repo_str)
	print "## List all files in {} repo for the latest commit in master".format(repo_str)
	filelist = list_files(repo)
	print "## Build filepath-to-number index"
	fileindex = {path: idx for idx, path in enumerate(filelist)}
	for idx, path in enumerate(filelist):
		print idx, "\t", path
	print "## Iterating over files and commits. Please wait." 
	matrix, people2file, peoplelist = build_matrix(repo, fileindex)
	print "## Requirements matrix: files to files"
	for row in matrix:
		print ''.join('%4s' % i for i in row)
	print "## Authors to files matrix"
	for row in people2file:
		print ''.join('%4s' % i for i in row)
	sys.stderr.write('Rate limit: {}\n'.format(g.rate_limiting))
	print "## Calculating requirement natrix and writing results to file"
	# requirements = p2f * f2f * f*p
	result = matmult(people2file, matmult(matrix, trans(people2file)))
	print result
	data = {}
	data["files"] = filelist
	data["people"] = peoplelist
	data["people2files"] = people2file
	data["files2files"] = matrix
	data["requirements"] = result
	filename = "output_data/" + sys.argv[1].replace("/","-")
	with open(filename, 'w+') as f:
		json.dump(data, f)
	print "## Results written to {}".format(filename)
main()

