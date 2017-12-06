

# Convert all XML files
# for now, skip ECP and REF
for F in xml/*xml
do
    if [[ $F != *"-REF.xml" && $F != *"-ECP.xml" ]]
    then
        echo $F
        ../convert_xml.py $F
    fi
done


# Create element,table entries for all that are listed
# in a tmp file
for F in `cat only-emsl-lib-names.txt`
do
    echo $F
    if [[ $F != *"-ECP.xml" ]]
    then
        if [[ $F == *"-AGG.xml" ]]
        then
           ../convert_xml_agg.py xml/$F 
        else
           ../create_simple_agg.py xml/$F 
        fi
    fi
done
