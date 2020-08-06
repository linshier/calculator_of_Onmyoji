#!/bin/sh
#https://cbg-yys.res.netease.com/game_res/hero/330/330.png
cat xxx|while read role_id; do
date="$(date +%s)"
curl -s 'https://bdapi.gameyw.netease.com/ky59/v1/g37_charts/oneuid?'${role_id}'&_='${date}'748&callback=Zepto'${date}'559' \
    --compressed \
    |grep 'Zepto'|sed 's/^Zepto.*(//;s/)$//'\
    |jq -r '.result.extra.bl|map(.|[.battle_result,.role_name,.d_role_name,(.battle_list|map(.|.shishen_id)),(.d_battle_list|map(.|.shishen_id))])' \
    |sed 's/ //g' \
    |awk '{if($0~"\\],"){print $0}else{printf $0}}' \
    |awk '{if($0~"\\]\\],"){print $0}else{printf $0}}' \
    |grep -v '\[\]' \
    |sed 's/\[\[/\[\
\[/;s/\]\]\]$/\]\]\
\]/' \
    |sed -e "s;^\(\[[01]\);\1,${role_id/&/\&};"
done
exit 0
