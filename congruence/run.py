#!/usr/bin/python

import sys
import json
import math

def get_cosine(vec1, vec2):
	n = len(vec1)
	if len(vec2) != n: raise Exception("Wrong length")

	numerator = sum([vec1[i] * vec2[i] for i in range(n)])

	sum1 = sum([vec1[i]**2 for i in range(n)]) 
	sum2 = sum([vec2[i]**2 for i in range(n)])
	denominator = math.sqrt(sum1) * math.sqrt(sum2)

	if not denominator:
		return 0.0
	else:
		return float(numerator) / denominator
def diff(A,B):
	n = len(A) # they expected to be of the same length
	return [get_cosine(A[i], B[i]) for i in range(n)]


def sparsity(m):
	l = len(m)
	total = l*l
	zero = 0
	for i in range(l):
		for j in range(l):
			if m[i][j] == 0:
				zero+=1
	return total - zero, total

def  transform(m, index, allowed):
	l = len(allowed)
	reverse_index = {user:idx for idx, user in enumerate(index)}
	out = [[0]*l for _ in range(l)]
	for i in range(l):
		user_i  = allowed[i]
		ii = reverse_index[user_i]
		for j in range(l):
			user_j  = allowed[j]
			jj = reverse_index[user_j]
			out[i][j] = m[ii][jj]
	return out

def main():
	repos = []
	HISTORY= "../history/output_data/{}.json"
	ACTUAL = "../technical/output_data/{}"
	with open(sys.argv[1]) as f:
		repos = f.readlines()
	for repo_line in repos:
		try:
			repo = repo_line.strip().replace("/","-")
			with open(HISTORY.format(repo), 'r') as hfile:
				hjson = json.load(hfile)
			with open(ACTUAL.format(repo), 'r') as afile:
				ajson = json.load(afile)
			hpeople = hjson["users"]
			apeople = ajson["people"]
			people = list(set(hpeople) & set(apeople))
			H = hjson["matrix"]	  	# historical
			T = ajson["requirements"] 	# technical
			E = ajson["comments_matrix"]		# explicit
			print sparsity(H), sparsity(T), sparsity(E)
			H = transform(H, hpeople, people)
			T = transform(T, apeople, people)
			E = transform(E, apeople, people)
			print sparsity(H), sparsity(T), sparsity(E)
			H2T = diff(H, T)
			T2E = diff(T, E)
			H2T_norm = math.sqrt(sum(i**2 for i in H2T))
			T2E_norm = math.sqrt(sum(i**2 for i in T2E))
			print "H2T", H2T_norm, "T2E", T2E_norm
		except Exception as e:
			print "Error with ", repo, ".", e

main()
