#!/usr/bin/python

import sys
import json


def main():
	history = sys.argv[1]
	actual = sys.argv[2]
	hfile = open(history, 'r')
	afile = open(actual, 'r')
	hjson = json.load(hfile)
	ajson = json.load(afile)
	hmatrix  = hjson["matrix"]
	amatrix = ajson["requirements"]

	print congruence(hmatrix, amatrix)

def congruence(h, a):
	return 0

main()
