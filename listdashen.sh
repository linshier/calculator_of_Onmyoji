#!/bin/sh
#https://ds.163.com/2019/yys/dj-rank/
#https://cbg-yys.res.netease.com/game_res/hero/330/330.png

date="$(date +%s)"
server=all
server=10000
function jq_all()
{
    jq -r '.result|(.[])'
}
function jq_simple()
{
    #jq -r '.result'
    jq -r '.result|map(.|[.role_id,(.small_extra.count_win*100/.small_extra.count_all|floor),.small_extra.count_all,.rank,.small_extra.role_name,((500+(.score-18000)/30)|floor)])' \
        |sed 's/ //g' \
        |awk '{if($0~"\\],"){print $0}else{printf $0}}' \
        |sed 's/^\[\["//;s/\["//;s/\]\]//;s/\],//;s/",/ /;s/,/ /g;' \

}
function output_simple()
{
    sed "s/^/server=${server}\&roleid=/"
}
function output_all()
{
    grep .
}
function one_server()
{
    server=$1
    numpage=$2
    for ((pn=1;pn<=${numpage};pn++))
    do
        (([ -f dbds/${server}/topuid${pn} ] && cat dbds/${server}/topuid${pn}) || (\
        curl 'https://bdapi.gameyw.netease.com/ky59/v1/g37_charts/topuids?server='${server}'&page='${pn}'&_='${date}'057&callback=Zepto'${date}'173' \
            --compressed 2>/dev/null \
            |sed 's/^Zepto[0-9]*(//;s/)$//' \
        ))\
            |jq_simple \
            |output_simple
	printf "\n"
        #sleep 1
    done
}
if [ $# -eq 2 ]; then
    one_server $1 $2
    exit 0
fi
one_server 10009 10
exit 0
for ((server=10001;server<=15033;server++))
do
    if [ ${server} -eq 10031 ]; then
        server=15001
    fi
    one_server ${server} 10
done
