#!/bin/bash

export PYTHONPATH=$(pwd)/requirements:$PYTHONPATH
mkdir -p db
echo https://yys.cbg.163.com/cgi/mweb/equip/$(echo $1|cut -d"-" -f2)/$1
if [ ! -f db/$1.json ]; then
python calculator_of_Onmyoji/pull_mitama.py $1 -O db/$1.xls 2>/dev/null || echo $?
cat db/$1.json|python -m json.tool|grep '\<price\>'
#cat db/$1.json |jq -r '.equip.equip_desc'|jq -r '.hero_fragment'|grep ' 325\| 316' -B2|awk '{print $NF}'|xargs
cat db/$1.json |jq -r '.equip.equip_desc'|jq -r '.yzg.open'
cat db/$1.json|jq -r '.equip.equip_desc'|python -m json.tool|grep '901240.. .,\|901130.. .,\|\<901226\> ' #|| exit 0
python calculator_of_Onmyoji/cal_mitama.py db/$1.xls res.xls
sleep 11
fi

#if [ -f db/$1.xls ]; then
#fi
