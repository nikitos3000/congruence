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

def main():
	history = sys.argv[1]
	actual = sys.argv[2]
	with open(history, 'r') as hfile:
		hjson = json.load(hfile)
	with open(actual, 'r') as afile:
		ajson = json.load(afile)
	people = ajson["people"]
	H = hjson["matrix"]	  	# historical
	T = ajson["requirements"] 	# technical
	E = ajson["comments"]		# explicit
	H2T = diff(H, T)
	T2E = diff(T, E)
	for i in len(H):
		print people[i], "\t", H2T[i], T2E[i]

main()
