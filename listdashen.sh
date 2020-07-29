#!/bin/sh

#curl 'https://bdapi.gameyw.netease.com/ky59/v1/g37_charts/oneuid?server=10009&roleid=F3lbUpIBk8762GY_k84EdzlFC1jEGNT0R1RHsEWlJ0bDKweRZG-JmMkuVRFjNg%3D%3D&_=1595848055584&callback=Zepto1595848055253' \
#  --compressed

#curl 'https://bdapi.gameyw.netease.com/ky59/v1/g37_charts/topuids?server=all&page=1&_=1595851353675&callback=Zepto1595851353532' \
#  --compressed


date="$(date +%s)"
#echo $date
#curl 'https://bdapi.gameyw.netease.com/ky59/v1/g37_charts/oneuid?server=all&roleid=B3kr7ZIBk87Sf7mfk84EdzlFC1nEGL_oRGG27rStiN7DceZwqPVKR9vfek5Taw%3D%3D&_='${date}'&callback=Zepto1595851573180' \
#  --compressed

#curl 'https://bdapi.gameyw.netease.com/ky59/v1/g37_charts/topuids?server=all&page=1&_=1595851875057&callback=Zepto1595851874819' \
#  --compressed

#curl 'https://bdapi.gameyw.netease.com/ky59/v1/g37_charts/topuids?server=all&page=1&_=1595851875057&callback=Zepto1595851874819' \
#  --compressed
#curl 'https://bdapi.gameyw.netease.com/ky59/v1/g37_charts/oneuid?server=all&roleid=wOV_nZIBk84iCjuPk84EdzlFCzbEGPjmG4qo1l1vR5vC8CVvML62JLFdR7Hmvg%3D%3D&_=1595902898748&callback=Zepto1595902898559' \
#  --compressed
#exit 0

for ((pn=1;pn<5;pn++))
do
curl 'https://bdapi.gameyw.netease.com/ky59/v1/g37_charts/topuids?server=all&page='${pn}'&_='${date}'057&callback=Zepto'${date}'235' \
  --compressed 2>/dev/null \
|sed 's/^Zepto[0-9]*(//;s/)$//'|jq -r '.result|.[].role_id'
done

