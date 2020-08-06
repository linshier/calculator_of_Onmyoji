#!/bin/sh

date="$(date +%s)"
server=all
server=10000
for ((server=10001;server<=15033;server++))
do
    if [ ${server} -eq 10031 ]; then
        server=15001
    fi
    for ((pn=1;pn<=1;pn++))
    do
        curl 'https://bdapi.gameyw.netease.com/ky59/v1/g37_charts/topuids?server='${server}'&page='${pn}'&_='${date}'057&callback=Zepto'${date}'235' \
            --compressed 2>/dev/null \
            |sed 's/^Zepto[0-9]*(//;s/)$//'|jq -r '.result|.[].role_id' \
            |sed "s/^/server=${server}\&roleid=/"
    done
done
