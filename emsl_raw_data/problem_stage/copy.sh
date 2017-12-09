#!/bin/bash

set -eu

FILE=$1
PREFIX=$2


BASE=`basename ${FILE}`
REFFILE=`echo ${FILE} | sed 's/.xml/-BS-REF.xml/g'`
REFBASE=`basename ${REFFILE}`

cp -iv ${FILE} ./${PREFIX}_${BASE}
cp -iv ${REFFILE} ./${PREFIX}_${REFBASE}
sed -i "s/${REFBASE}/${PREFIX}_${REFBASE}/g" ${PREFIX}_${BASE}

#vimdiff ${FILE} ${PREFIX}_${BASE}
#vimdiff ${REFFILE} ${PREFIX}_${REFBASE}
