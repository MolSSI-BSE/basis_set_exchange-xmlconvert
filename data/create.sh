export PATH=${PATH}:../bse-xml
set -eu

convert_xml.py 6-31G.xml
convert_xml.py 6-31GS.xml
convert_xml.py 6-31GSS.xml

convert_xml.py 6-311G.xml
convert_xml.py 6-311GS.xml
convert_xml.py 6-311GSS.xml

convert_xml.py POPLDIFF.xml

convert_xml_agg.py 6-311GSS-AGG.xml

convert_xml_agg.py 6-311PPGSS-AGG.xml
convert_xml_agg.py 6-31PPGSS-AGG.xml
convert_xml_agg.py 6-31GSS-AGG.xml
convert_xml_agg.py 6-31PPG-AGG.xml
convert_xml_agg.py 6-31PPGSS-AGG.xml

create_simple_agg.py 6-311G.xml
create_simple_agg.py 6-31G.xml

#remove_duplicate.py 6-31GS.json
