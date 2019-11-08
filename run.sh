#!/bin/bash

export PYTHONPATH=$(pwd)/requirements:$PYTHONPATH
sn=$(echo $1|grep -o '2019[0-9A-Z\-]*')
mkdir -p db
echo https://yys.cbg.163.com/cgi/mweb/equip/$(echo $sn|cut -d"-" -f2)/$sn
if [ ! -f db/$sn.json ]; then
python calculator_of_Onmyoji/pull_mitama.py $sn -O db/$sn.xls 2>/dev/null || echo $?
cat db/$sn.json|python -m json.tool|grep 'price'
#cat db/$sn.json |jq -r '.equip.equip_desc'|jq -r '.hero_fragment'|grep ' 325\| 316' -B2|awk '{print $NF}'|xargs
#cat db/$sn.json |jq -r '.equip.equip_desc'|jq -r '.yzg.open'
#cat db/$sn.json|jq -r '.equip.equip_desc'|python -m json.tool|grep '901240.. .,\|901130.. .,\|\<901226\> ' #|| exit 0
python calculator_of_Onmyoji/cal_mitama.py db/$sn.xls res.xls
echo '...' && sleep 11
else
#exit 0
cp *.xls db/
python calculator_of_Onmyoji/cal_mitama.py db/$sn.xls res.xls
fi
