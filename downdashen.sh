#!/bin/bash
#https://ds.163.com/2019/yys/dj-rank/
#https://cbg-yys.res.netease.com/game_res/hero/330/330.png
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
one_server all 10
#exit 0
for ((server=10001;server<=15031;server++))
do
    if [ ${server} -eq 10010 ]; then
        server=10014
    fi
    if [ ${server} -eq 10015 ]; then
        server=10016
    fi
    if [ ${server} -eq 10031 ]; then
        server=15001
    fi
    if [ ${server} -eq 15010 ]; then
        server=15014
    fi
    if [ ${server} -eq 15015 ]; then
        server=15023
    fi
    if [ ${server} -eq 15025 ]; then
        server=15026
    fi
    if [ ${server} -eq 15027 ]; then
        server=15028
    fi
    if [ ${server} -eq 15030 ]; then
        server=15031
    fi
    one_server ${server} 10
done
exit 0

one_server 10009 10
exit 0
