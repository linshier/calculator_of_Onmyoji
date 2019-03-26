#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse
import json
import traceback

import requests
import xlwt
import os

from calculator_of_Onmyoji import data_format

UASTRING = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) '
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 '
            'Safari/537.36')

parser = argparse.ArgumentParser()
parser.add_argument("acc_id",
                    type=str,
                    help=u'cbg id')
parser.add_argument("-O", "--output-file",
                    type=str,
                    default='mitama_data.xls',
                    help=u'db/filename.xls')


def download_data(acc_id, filename):
    server_id = int(acc_id.split('-')[1])
    post_data = 'serverid=%s&ordersn=%s' % (server_id, acc_id)
    post_header = {'User-Agent': UASTRING, 'Content-Type': 'application/x-www-form-urlencoded'}
    post_url = 'https://yys.cbg.163.com/cgi/api/get_equip_detail'

    try:
        #print(post_url, post_data, post_header)
        json_filename = filename[:-3] + 'json'
        text = ''
        if os.path.exists(json_filename):
            f = open(json_filename, 'r')
            text = f.read()
            f.close()
        else:
            req = requests.post(post_url, data=post_data, headers=post_header,
                    verify=False)
            text = req.text
            f = open(json_filename, 'w')
            f.write(text)
            f.close()
        return json.loads(text)
    except Exception:
        print('Unable to download the data. %s' % traceback.format_exc())
        return None


def generate_mitama_list(acc_id, filename,
                         header_row=data_format.MITAMA_COL_NAME_ZH):
    #print("Downloading data...")
    res = download_data(acc_id, filename)

    #print("Dumping mitama data...")
    if res is None:
        return

    enAttrNames = ['attackAdditionRate',
                   'attackAdditionVal',
                   'critPowerAdditionVal',
                   'critRateAdditionVal',
                   'debuffEnhance',
                   'debuffResist',
                   'defenseAdditionRate',
                   'defenseAdditionVal',
                   'maxHpAdditionRate',
                   'maxHpAdditionVal',
                   'speedAdditionVal']
    cnAttrNames = [u'攻击加成', u'攻击', u'暴击伤害', u'暴击',
                   u'效果命中', u'效果抵抗', u'防御加成',
                   u'防御', u'生命加成', u'生命', u'速度']
    basePropValue = {u'攻击加成': 3, u'攻击': 27, u'暴击伤害': 4, u'暴击': 3,
                     u'效果抵抗': 4,  u'效果命中': 4, u'防御加成': 3,
                     u'防御': 5, u'生命加成': 3, u'生命': 114, u'速度': 3}
    e2cNameMap = dict(list(zip(enAttrNames, cnAttrNames)))
    def calAddiAttrs(rattrs):
        res = {}
        for prop, v in rattrs:
            prop = e2cNameMap[prop]
            if prop not in res:
                res[prop] = 0
            res[prop] += v
        return [[p, res[p]*basePropValue[p]] for p in res]
    try:
        workbook = xlwt.Workbook(encoding='utf-8')
        mitama_sheet = workbook.add_sheet(u'御魂')
        acct_info = res['equip']
        acct_detail = json.loads(acct_info['equip_desc'])

        mitama_list = acct_detail['inventory']

        col_nums = len(header_row)

        # write header row
        for c in range(col_nums):
            mitama_sheet.write(0, c, label=header_row[c])

        mitama_num = 1
        for mitama_id in mitama_list:
            mitama_info = mitama_list[mitama_id]
            if int(mitama_info['level']) < 15:
                continue
            mitama_pos = str(mitama_info['pos'])
            mitama_name = mitama_info['name']
            mitama_attrs = dict()
            # 获取首领御魂独立属性
            single_prop = mitama_info.get('single_attr')
            if single_prop:
                mitama_attrs[single_prop[0]] = int(
                    single_prop[1].replace('%', ''))
            if 'rattr' in mitama_info:
                base_prop = mitama_info['attrs'][0]
                mitama_attrs[base_prop[0]] = float(base_prop[1].replace('%', ''))
                for prop, value in calAddiAttrs(mitama_info['rattr']):
                    if prop not in mitama_attrs:
                        mitama_attrs[prop] = value
                    else:
                        mitama_attrs[prop] += value
            else:
                for prop, value in mitama_info['attrs']:
                    value = int(value.replace('%', ''))
                    if prop not in mitama_attrs:
                        mitama_attrs[prop] = value
                    else:
                        mitama_attrs[prop] += value

            mitama_sheet.write(mitama_num, 0, label=mitama_id)
            mitama_sheet.write(mitama_num, 1, label=mitama_name)
            mitama_sheet.write(mitama_num, 2, label=mitama_pos)
            for i, prop in enumerate(data_format.MITAMA_PROPS):
                prop_value = mitama_attrs.get(prop, '')
                mitama_sheet.write(mitama_num, 3+i, label=prop_value)

            mitama_num += 1

        workbook.save(filename)
        #print("write finish, we got %s results" % mitama_num)
    except Exception as e:
        print(e.message)
        raise e


def main():
    args = parser.parse_args()
    test_acc_id = args.acc_id
    output_file = args.output_file
    #print('Start pulling mitama data, please wait')
    generate_mitama_list(test_acc_id, output_file)


if __name__ == '__main__':
    main()
    #input('Press any key to exit.')
