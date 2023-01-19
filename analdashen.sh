#!/bin/sh
#https://ds.163.com/2019/yys/dj-rank/
#https://cbg-yys.res.netease.com/game_res/hero/330/330.png
function jq_all()
{
    #grep .
    jq -r '.result.extra.bl' 
}
function jq_name()
{
    jq -r '.result.extra.bl|map(.|[.battle_result,.role_name,.d_role_name,(.battle_list|map(.|.shishen_id)),(.d_battle_list|map(.|.shishen_id))])' 
}
function jq_time()
{
    jq -r '.result.extra.bl|map(.|[.battle_result,.role_name,.d_role_name,.total_battle_time,.score,(.battle_list|map(.|.shishen_id)),(.d_battle_list|map(.|.shishen_id))])' 
}
function jq_simple()
{
    jq -r '.result.extra.bl|map(.|[.battle_result,(.battle_list|map(.|.shishen_id)),(.d_battle_list|map(.|.shishen_id))])' 
}
function output_role_id()
{
    sed -e "s;^\(\[[01]\);\1,${role_id/&/\&};"
}
function output_simple()
{
    grep .
}
function format()
{
    sed 's/ //g' \
        |awk '{if($0~"\\],"){print $0}else{printf $0}}' \
        |awk '{if($0~"\\]\\],"){print $0}else{printf $0}}' \
        |grep -v '\[\]' \
        |sed 's/\[\[/\[\
        \[/;s/\]\]\]$/\]\]\
        \]/' 
}
function format_none()
{
    grep .
}
function zepto()
{
    #grep .
    grep 'Zepto'|sed 's/^Zepto[1-9][0-9]*(//;s/)$//'
}
function main()
{
    awk '{print $1}' \
    |while read role_id; do
        date="$(date +%s)"
        (([ -f $1.raw ] && cat $1.raw) || \
            (sleep $[RANDOM % 5 + 1] && \
            curl -m 5 -s 'https://bdapi.gameyw.netease.com/ky59/v1/g37_charts/oneuid?'${role_id}'&_='${date}'748&callback=Zepto'${date}'559' \
            --compressed|tee $1.raw)) \
        |zepto \
        |jq_time \
        |format_none \
        |output_simple
    done
}
if [ $# -eq 2 ]; then
    echo $1|main $2|tee $2 2>&1|wc -l
    exit 0
fi
cat xxx|main|tee test.txt 2>&1|wc -l
exit 0
