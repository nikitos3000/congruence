Given a repository, construct square matrix A,
such as A{ij} shows the measure of technical requirements between elements i and j

Each element is a unit of work -- currently decided to be a single file.

The measure of 'interaction' between files is how many times these two files appeared to be in the same commit.

# How to use

`./script.py cmu440/p2` 

where `cmu440/p2` is a repo

The output will be written as json in `output_data/cmu440-p2` file with the following structure:
```
{
	"files": [],
	"files2files": [matrix],
	"people2files": [matrix],
	"requirements": [matrix],
	"people": []
}

```

where `files` is list of files in the repo
`files2files` matrix (array of arrays) where each cell is how many times file i was changed together with file j
`people2files` matrix (array of arrays) where each cell is how many times a developer has touched this file
`people` is a list of all developers in the repo
`requirements` is a matrix with coordination requirements in the repo
