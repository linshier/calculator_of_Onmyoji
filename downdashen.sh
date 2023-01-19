#!/bin/bash
#https://ds.163.com/2019/yys/dj-rank/
#hero
#https://cbg-yys.res.netease.com/game_res/hero/330/330.png
#hero backup
#https://yys.res.netease.com/pc/zt/20161108171335/data/before_awake/395.jpg
#yuhun
#https://cbg-yys.res.netease.com/game_res/suit/300076.png
function one_server() {
    server=$1
    topn0=$2
    filter=$3
    mkdir -p dbds/${server}/
    while read id rank; do
        r=$(printf "%03d" ${rank})
        echo ${r} ${id}
        ./analdashen.sh ${id} dbds/${server}/${r}
    done < <( \
        (([ -f dbds/${server}/list ] && cat dbds/${server}/list) || ./listdashen.sh ${server} ${topn0}|tee dbds/${server}/list) \
        |grep ${filter}|awk '($2>=40){print $1,$4}' \
    )
}
function fast()
{
#    one_server 10009 10 Canon
    one_server all 10 .
}
function quick()
{
   #one_server 10009 10 Canon
   one_server 10009 10 .
   #one_server all 10 .
   #one_server 15006 10 .
}
function allserver()
{
    one_server all 10 .
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
        one_server ${server} 10 .
    done
}
fast
#quick
#allserver
date -R
exit 0
