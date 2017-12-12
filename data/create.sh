
set -eu

cd xml_stage

# Convert all XML files
# for now, skip REF and AGG
for F in *xml
do
    if [[ $F != *"-REF.xml" && \
          $F != *"-AGG.xml" ]]
    then
        echo $F
        ../../convert_xml.py $F
    fi
done

# Create element,table entries for all that are listed
# in a tmp file
cat ../$1 | while read I
do
    F=`basename "$I"`
    echo $F
    if [[ $F == *"-AGG.xml" ]]
    then
       ../../convert_xml_agg.py $F 
    else
       ../../create_simple_agg.py $F 
    fi
done

cd ../
