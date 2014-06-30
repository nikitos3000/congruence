Given a repository, construct square matrix A,
such as A_{ij} shows the measure of technical requirements between elements i and j

Each element is a unit of work -- currently decided to be a single file.

The measure of 'interaction' between files is how many times these two files appeared to be in the same commit.

# How to use

`./script.py cmu440/p2 > cmu440-p2` where `cmu440/p2` is a repo and `cmu440-p2` is output file
