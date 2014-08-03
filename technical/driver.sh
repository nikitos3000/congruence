#/bin/bash

repos="../congruence/repos"
cat $repos | awk '{print $1}' | while read line
do
	now=$(date +"%a %T")
	echo "Begin:\t$now\t$line"
	python script.py $line > script.log 2>&1
	rc=$?
	now=$(date +"%a %T")
	if [[ $rc != 0 ]] ; then
		echo "ERROR:\t$now"
	else 
		echo "Done:\t$now"
	fi
done
