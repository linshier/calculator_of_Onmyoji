#!/bin/sh

function getjson() {
price='&price_min=150000&price_max=200000'
speed='270'
serverid='&serverid=11'
heroid='&hero_id=339'
#heroid='&hero_id=300'

curl -s \
'https://recommd.yys.cbg.163.com/cgi-bin/recommend.py?callback=jQuery331005339417346521924_1573004345929&act=recommd_by_role&search_type=role&count=15'${serverid}'&platform_type=1'${heroid}'&order_by=price%20ASC&pass_fair_show=1'${price}'&page='$1 \
-H 'authority: recommd.yys.cbg.163.com' \
-H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36' --compressed \
|sed 's/^jQ[^{]*(//;s/)$//;'
return $?
}
for ((i=1;i<100;i++))
do
res=$(getjson $i|python -m json.tool|grep 'game_ordersn\|is_last_page'|awk '{print $NF}'|sed 's;[",];;g')
echo $res|grep '^true[ ]*$' >/dev/null && break
echo $res|xargs -n1|grep 201
sleep 5
done
