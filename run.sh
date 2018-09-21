#!/bin/bash

export PYTHONPATH=$(pwd)/requirements:$PYTHONPATH
mkdir -p db
if [ ! -f db/$1.xls ]; then
python calculator_of_Onmyoji/pull_mitama.py $1 -O db/$1.xls
fi
time python calculator_of_Onmyoji/cal_mitama.py db/$1.xls res.xls
