#!/bin/bash

export PYTHONPATH=$(pwd)/requirements:$PYTHONPATH
mkdir -p db
if [ ! -f db/$1.xls ]; then
echo https://yys.cbg.163.com/cgi/mweb/equip/$(echo $1|cut -d"-" -f2)/$1
python calculator_of_Onmyoji/pull_mitama.py $1 -O db/$1.xls 2>/dev/null || echo $?
python calculator_of_Onmyoji/cal_mitama.py db/$1.xls res.xls
sleep 10
fi
