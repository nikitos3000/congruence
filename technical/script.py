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

def build_matrix(repo, fileindex):
	l = len(fileindex)
	matrix = [[0]*l for i in range(l)]
	commits = defaultdict(list)
	for path,idx in fileindex.iteritems():
		for c in repo.get_commits(path=path):
			commits[c.sha].append(idx)
	for items in commits.values():
		for i in items:
			for j in items:
				matrix[i][j] += 1  

	return matrix
	latest = repo.get_branch('master').commit
	def process_commit(current):
		idxs = [fileindex[f.filename] for f in current.files]
		for i in idxs:
			for j in idxs:
				matrix[i][j]+=1
		print current.sha, idxs
		for c in current.parents:
			process_commit(c)
	process_commit(latest)
	return matrix

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
	print "## Build requirements matrix"
	matrix = build_matrix(repo, fileindex)
	for row in matrix:
		print ''.join('%4s' % i for i in row)
	sys.stderr.write('Rate limit: {}'.format(g.rate_limiting))
main()

