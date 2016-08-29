./src/dream_machine.py -n $2 -s $1 res/wsj/train-wsj-00-20.sent > tmp.txt

echo Generated $1 sentences:
cat tmp.txt

./src/dream_machine_test.py -n 2 -u $3 tmp.txt res/wsj/test-wsj-23-24.sent

rm tmp.txt