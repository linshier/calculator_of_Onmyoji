#!/bin/bash
server="all"
mkdir -p dbds/${server}/
while read id rank; do
    r=$(printf "%03d" ${rank})
    echo ${r} ${id}
    ./analdashen.sh ${id} dbds/${server}/${r}
done < <(./listdashen.sh ${server} 1|awk '{print $1,$4}')
