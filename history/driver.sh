#/bin/bash

repos="../congruence/$1"
(cd ../history && cat $repos | xargs -L1 python run.py)
