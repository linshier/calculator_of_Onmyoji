#!/bin/sh
#'https://yys.cbg.163.com/cgi/api/role_search?pass_fair_show=1&platform_type=1&price_min=100000&price_max=150000&hero_id=312,322,325&hero_max_speed=200&order_by=selling_time%20DESC&page='$1 \
#'https://yys.cbg.163.com/cgi/api/role_search?goyu=70000&platform_type=1&hero_id=322,325&order_by=selling_time%20DESC&page='$1 \
#'https://yys.cbg.163.com/cgi/api/role_search?pass_fair_show=1&platform_type=1&price_min=99900&price_max=300000&hero_id=322,325&hero_max_speed=269&order_by=selling_time%20DESC&page='$1 \
#'https://yys.cbg.163.com/cgi/api/role_search?pass_fair_show=0&platform_type=1&price_min=250000&price_max=400000&order_by=collect_num%20DESC&page='$1 \
#-H 'cbg-safe-code: fELYlA3A' --compressed
#'https://yys.cbg.163.com/cgi/api/role_search?platform_type=1&heros=%5B%7B%22hero_id%22%3A261%2C%22speed%22%3A%22260%22%7D%5D&price_min=300000&price_max=800000&order_by=price%20ASC&page='$1 \
#curl 'https://yys.cbg.163.com/cgi/api/query?platform_type=1&pass_fair_show=1&heros=%5B%7B%22hero_id%22%3A261%2C%22speed%22%3A%22272%22%7D%5D&serverid=7&price_min=200000&price_max=600000&order_by=selling_time%20DESC&page=1'
#'https://yys.cbg.163.com/cgi/api/query?platform_type=1&pass_fair_show=1&heros=%5B%7B%22hero_id%22%3A261%2C%22speed%22%3A%22272%22%7D%5D&price_min=600000&price_max=700000&order_by=selling_time%20DESC&page='$1 \
#'https://yys.cbg.163.com/cgi/api/query?pass_fair_show=1&hero_id=322&serverid=7&price_min=30000&price_max=160000&order_by=selling_time%20DESC&page='$1 \

#'https://yys.cbg.163.com/cgi/api/query_topic_equips?topic_id=1-46&serverid=11&price_min=500000&price_max=900000&platform_type=1&order_by=selling_time%20DESC&page='$1 \

function getjson() {
price='&price_min=500000&price_max=1900000'
speed='270'

curl -s \
'https://recommd.yys.cbg.163.com/cgi-bin/recommend.py?callback=jQuery33108416587861223492_1569310704203&act=recommd_by_role&search_type=role&count=15&platform_type=1&order_by=price%20ASC'${price}'&heros=%5B%7B%22hero_id%22%3A261%2C%22speed%22%3A%22'${speed}'%22%7D%5D&page='$1 \
-H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36' --compressed \
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
