#!/bin/sh
#'https://yys.cbg.163.com/cgi/api/role_search?pass_fair_show=1&platform_type=1&price_min=100000&price_max=150000&hero_id=312,322,325&hero_max_speed=200&order_by=selling_time%20DESC&page='$1 \
#'https://yys.cbg.163.com/cgi/api/role_search?goyu=70000&platform_type=1&hero_id=322,325&order_by=selling_time%20DESC&page='$1 \
#'https://yys.cbg.163.com/cgi/api/role_search?pass_fair_show=1&platform_type=1&price_min=99900&price_max=300000&hero_id=322,325&hero_max_speed=269&order_by=selling_time%20DESC&page='$1 \
#'https://yys.cbg.163.com/cgi/api/role_search?pass_fair_show=0&platform_type=1&price_min=250000&price_max=400000&order_by=collect_num%20DESC&page='$1 \
#-H 'cbg-safe-code: fELYlA3A' --compressed
#'https://yys.cbg.163.com/cgi/api/role_search?platform_type=1&heros=%5B%7B%22hero_id%22%3A261%2C%22speed%22%3A%22260%22%7D%5D&price_min=300000&price_max=800000&order_by=price%20ASC&page='$1 \

function getjson() {
curl -s \
'https://yys.cbg.163.com/cgi/api/query?platform_type=1&price_min=100000&price_max=149900&hero_id=322&order_by=price%20ASC&page='$1 \
-H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36' \
--compressed
return $?
}
for ((i=1;i<100;i++))
do
res=$(getjson $i|python -m json.tool|grep 'game_ordersn\|is_last_page'|awk '{print $NF}'|sed 's;[",];;g')
echo $res|grep '^true[ ]*$' >/dev/null && break
echo $res|xargs -n1|grep 201
sleep 5
done
