set -eu

cat tocopy.txt | while read I
do
    echo "RUNNING: $I"
   ./copy_file_and_deps.py "$I" ../data/xml
done
