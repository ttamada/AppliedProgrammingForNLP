declare -a arr=("beer" "wine" "word")
declare -a arr2=("thing" "boat" "vision")


## now loop through the above array
for i in "${arr[@]}" 
do
   ./src/k_nearest_neighbor.py -w "$i" 
   # or do whatever with individual element of the array
done

for i in "${arr2[@]}" 
do
   ./src/k_nearest_neighbor.py -w "$i"
done

./src/k_nearest_neighbor.py -w not good
