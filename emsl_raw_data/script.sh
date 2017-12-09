set -eu

cat tocopy.txt | while read I
do
   ./copy_file_and_deps.py "$I" ../data/xml
done
