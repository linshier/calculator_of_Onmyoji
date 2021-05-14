#!/bin/bash
function one_server() {
    server=$1
    topn0=$2
    mkdir -p dbds/${server}/
    while read id rank; do
        r=$(printf "%03d" ${rank})
        echo ${r} ${id}
        ./analdashen.sh ${id} dbds/${server}/${r}
        sleep $[RANDOM % 5 + 1]
    done < <(./listdashen.sh ${server} ${topn0}|tee dbds/${server}/list|awk '($NF>=40){print $1,$4}')
}
one_server 10009 10
exit 0
one_server all 10
#for ((server=10001;server<=15033;server++))
for ((server=10021;server<=15033;server++))
do
    if [ ${server} -eq 10031 ]; then
        server=15001
    fi
    one_server ${server} 10
done
