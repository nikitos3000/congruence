#!/usr/bin/python
from github import Github
from collections import defaultdict
import sys


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
	return matrix, people2file

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
	matrix, people2file = build_matrix(repo, fileindex)
	print "## Requirements matrix: files to files"
	for row in matrix:
		print ''.join('%4s' % i for i in row)
	print "## Authors to files matrix"
	for row in people2file:
		print ''.join('%4s' % i for i in row)
	sys.stderr.write('Rate limit: {}'.format(g.rate_limiting))
main()

