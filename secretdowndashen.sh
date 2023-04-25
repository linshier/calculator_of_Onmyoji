#!/bin/bash
source config #import role_id,token,secret

function getjson_by_url() {
    url=$1
    host="$(echo $1|sed 's;^https://\([^/]*\)/.*$;\1;')"
    curl -s ${url} \
        -H "Host: ${host}" \
        -H 'Origin: https://act.ds.163.com' \
        -H 'Connection: keep-alive' \
        -H 'Accept: application/json, text/plain, */*' \
        -H 'User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 16_0_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Godlike/3.46.0 UEPay/com.netease.godlike/iOS_7.9.9' \
        -H 'Accept-Language: zh-CN,zh-Hans;q=0.9' \
        -H 'Referer: https://act.ds.163.com/' \
        -H 'Accept-Encoding: gzip, deflate, br' \
        --compressed 
    return $?
}
function getjson_dj_list() {
    dts="&dts=$(date +%Y%m%d)"
    getjson_by_url 'https://bdapi.gameyw.netease.com/data_report/g37_ud/douji_list?server=10009'${role_id}${dts}${token}
    return $?
}
function getjson_dj_detail() {
    dts="&dts=$(date +%Y%m%d)"
    team_id="$1"
    getjson_by_url 'https://bdapi.gameyw.netease.com/data_report/g37_ud/douji_detail?server=10009'${role_id}${dts}${token}'&team_id='${team_id} 
    return $?
}
function getjson_dj_mine() {
    mkdir -p mine
    while read team_id; do
        (([ -f mine/${team_id} ] && cat mine/${team_id}) || (sleep $[RANDOM % 10 + 1] && getjson_dj_detail ${team_id}|tee mine/${team_id})) >/dev/null
    done < <( \
        (([ -f mine/list ] && cat mine/list) || (getjson_dj_list|tee mine/list)) \
            |jq '.result.douji_list|map(.|.team_id)'|grep -o '[a-z0-9]*' \
    )
    return $?
}
function getjson_topuid() {
    server=$1
    pn=$2
    getjson_by_url 'https://a19-v3-bigdata.gameyw.netease.com/a19-bigdata/ky59/v1/g37_charts/topuids?server='${server}'&page='${pn}${secret} 
    return $?
}
function getjson_topuid_oneserver() {
    server=$1
    mkdir -p dbds/${server}/
    for ((pn=1; pn<=10; pn++)); do
        (([ -f dbds/${server}/topuid${pn} ] && cat dbds/${server}/topuid${pn}) || (sleep $[RANDOM % 5 + 1] && getjson_topuid ${server} ${pn}|tee dbds/${server}/topuid${pn})) > /dev/null
    done
    return $?
}
function getjson_oneuid() {
    server_and_roleid=$1
    getjson_by_url 'https://a19-v3-bigdata.gameyw.netease.com/a19-bigdata/ky59/v1/g37_charts/oneuid?'${server_and_roleid}${secret}
    return $?
}
function getjson_oneuid_zepto1() {
    printf 'Zepto1('
    getjson_oneuid $1
    ret=$?
    printf ')'
    return ${ret}
}
function getjson_oneuid_oneserver() {
    server=$1
    topn0=$2
    filter=$3
    getjson_topuid_oneserver ${server}
    mkdir -p dbds/${server}/
    while read id rank; do
        r=$(printf "%03d" ${rank})
        raw="dbds/${server}/${r}.raw"
        echo ${r} ${id}
        (([ -f ${raw} ] && cat ${raw}) || (sleep $[RANDOM % 15 + 1] && getjson_oneuid_zepto1 ${id}|tee ${raw})) >/dev/null
        ./analdashen.sh ${id} dbds/${server}/${r}
    done < <( \
        (([ -f dbds/${server}/list ] && cat dbds/${server}/list) || ./listdashen.sh ${server} ${topn0}|tee dbds/${server}/list) \
        |grep ${filter}|awk '($2>=0){print $1,$4}'|sort \
    )
}
getjson_oneuid_oneserver all 10 .
#getjson_topuid all 1

#getjson_dj_list
#getjson_dj_mine
