#!/bin/bash


lines1=()
for line in $(cat $1)
do 	
	lines1+=($line)
done 

for line in $(cat $2)
do 
	lines2+=($line)
done 

eq=0
diff=0
for ((i=1; i<=${#lines1[@]};i++))
do 
	if [ "${lines1[i]}" = "${lines2[i]}" ];
	then
		eq=$(($eq+1))
	else
		diff=$(($diff+1))
	fi
done

echo "Equal: $eq, Different: $diff"







	
