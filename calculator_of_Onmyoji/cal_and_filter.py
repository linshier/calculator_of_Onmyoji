# coding: utf-8

import itertools
import sys

from calculator_of_Onmyoji import data_format

attack_buf  = data_format.MITAMA_PROPS[1]
crit_rate   = data_format.MITAMA_PROPS[4]
crit_damage = data_format.MITAMA_PROPS[5]
speed       = data_format.MITAMA_PROPS[10]
suit        = data_format.MITAMA_COL_NAME_ZH[1]

speed_1p_limit = 3
#speed_1p_limit = 9

selected = set()

def filter_loc_prop(data_list, prop_type, prop_min_value):
    def prop_value_le_min(mitama):
        mitama_info = mitama.values()[0]
        if (mitama_info[prop_type] and
                mitama_info[prop_type] >= prop_min_value):
            return True
        else:
            return False
    return filter(prop_value_le_min, data_list)

def filter_1st_speed(data_dict):
    done = set()

    def prop_value_speed(mitama):
        if mitama.keys()[0] in done:
            return False
        mitama_info = mitama.values()[0]
        if (mitama_info[speed] and mitama_info[speed] >= speed_1p_limit):
            return True
        return False
    def prop_value_l2_speed(mitama):
        if mitama.keys()[0] in done:
            return False
        mitama_info = mitama.values()[0]
        if (mitama_info[speed] and mitama_info[speed] >= 57):
            return True
        return False
    def build_mask_none():
        return [], int(0), int(0)
    def build_mask_fortune():
        soul = []
        soul_2p_fortune_mask = int(0)
        soul_4p_fortune_mask = int(0)
        for (k, v) in data_format.MITAMA_ENHANCE.items():
            enhance_type = v[u"加成类型"]
            if k == data_format.MITAMA_TYPES[18]:
                print(k)
                soul_2p_fortune_mask |= (2 << (3 * len(soul)))
                soul_4p_fortune_mask |= (4 << (3 * len(soul)))
                soul.append(k)
                break
        return soul, soul_2p_fortune_mask, soul_4p_fortune_mask
    def build_mask_fire():
        soul = []
        soul_2p_fortune_mask = int(0)
        soul_4p_fortune_mask = int(0)
        for (k, v) in data_format.MITAMA_ENHANCE.items():
            enhance_type = v[u"加成类型"]
            if k == data_format.MITAMA_TYPES[25]:
                print(k)
                soul_2p_fortune_mask |= (2 << (3 * len(soul)))
                soul_4p_fortune_mask |= (4 << (3 * len(soul)))
                soul.append(k)
                break
        return soul, soul_2p_fortune_mask, soul_4p_fortune_mask
    def test_limit_1p_speed(n):
        return (n & 0xff) < speed_1p_limit
    def test_suit_buf_max_speed(buf_max, n):
        if buf_max == 0:
            buf_max = 1
        if buf_max > (n & 0xff):
            return buf_max, True
        return (n & 0xff) + 1, False

    if 1:
        res = filter_soul(prop_value_speed,
                          prop_value_l2_speed,
                          build_mask_none,
                          speed,
                          True,
                          test_suit_buf_max_speed,
                          data_dict)
        for x in res:
            done.add(x)

    res = filter_soul(prop_value_speed,
                      prop_value_l2_speed,
                      build_mask_fire,
                      speed,
                      True,
                      test_suit_buf_max_speed,
                      data_dict)
    for x in res:
        done.add(x)

def filter_soul(prop_value, prop_value_l2, build_mask, sortkey,
                find_one,
                test_suit_buf_max,
                data_dict):
    d1, d2, d3, d4, d5, d6 = data_dict.values()

    d2 = filter(prop_value_l2, d2)
    d4 = filter(prop_value, d4)
    d6 = filter(prop_value, d6)
    d1 = filter(prop_value, d1)
    d3 = filter(prop_value, d3)
    d5 = filter(prop_value, d5)
    #print('%d x %d x %d x %d x %d x %d' % (len(d1), len(d2), len(d3), len(d4), len(d5), len(d5)))
    #for i in d1:
    #    print('%s' % i.values()[0][suit])
    #    #print(('%s' % i.values()[0][suit]).decode('raw_unicode_escape'))
    #return []

    d1.sort(lambda x, y: cmp(x.values()[0][sortkey], y.values()[0][sortkey]), reverse=True)
    d2.sort(lambda x, y: cmp(x.values()[0][sortkey], y.values()[0][sortkey]), reverse=True)
    d3.sort(lambda x, y: cmp(x.values()[0][sortkey], y.values()[0][sortkey]), reverse=True)
    d4.sort(lambda x, y: cmp(x.values()[0][sortkey], y.values()[0][sortkey]), reverse=True)
    d5.sort(lambda x, y: cmp(x.values()[0][sortkey], y.values()[0][sortkey]), reverse=True)
    d6.sort(lambda x, y: cmp(x.values()[0][sortkey], y.values()[0][sortkey]), reverse=True)

    soul, soul_2p_mask, soul_4p_mask = build_mask()
    #print('%s %s %s' % (soul, soul_2p_mask, soul_4p_mask))

    l1 = map2list(soul, d1)
    l2 = map2list(soul, d2)
    l3 = map2list(soul, d3)
    l4 = map2list(soul, d4)
    l5 = map2list(soul, d5)
    l6 = map2list(soul, d6)

    suit_buf_max = 0
    result_num = 0
    result = []
    for i2 in l2:
        for i4 in l4:
            t2 = i2[1] + i4[1]
            n2 = i2[0] + i4[0]
            for i6 in l6:
                t3 = t2 + i6[1]
                n3 = n2 + i6[0]
                for i1 in l1:
                    t4 = t3 + i1[1]
                    n4 = n3 + i1[0]
                    if soul_4p_mask and (t4 & soul_2p_mask) == 0 and (t4 & soul_4p_mask) == 0:
		        continue
                    for i3 in l3:
                        t5 = t4 + i3[1]
                        n5 = n4 + i3[0]
                        for i5 in l5:
                            n6 = n5 + i5[0]
                            t6 = t5 + i5[1]
                            if soul_4p_mask == 0 or (t6 & soul_4p_mask):
                                suit_buf_max, ok = test_suit_buf_max(suit_buf_max, n6)
                                if ok:
                                    continue
                            else:
                                continue
                            d = 0
                            result_num += 1
                            result = [i1[2], i2[2], i3[2], i4[2], i5[2], i6[2]]
                            comb_sum = list2map(soul,
                                                n6, t6 & soul_4p_mask, '',
                                                4, '')
                            print(('%s %s' % (d, comb_sum)).decode('raw_unicode_escape'))
                            if find_one:
                                print('result: %s' % result)
                                return result
    print('result: %s' % result)
    return result

def filter_loc(data_dict):
    if len(data_dict) != 6:
        raise KeyError("combination dict source must have 6 keys")

    d1, d2, d3, d4, d5, d6 = data_dict.values()
    print('mitama nums by loc is %s %s %s %s %s %s' % (len(d1), len(d2),
                                                       len(d3), len(d4),
                                                       len(d5), len(d6)))
    def prop_value_quick(mitama):
        mitama_info = mitama.values()[0]
        if (mitama_info[speed] and mitama_info[speed] >= speed_1p_limit):
            return True
        enhance_type = data_format.MITAMA_ENHANCE[mitama_info[suit]][u"加成类型"]
        if (enhance_type != u"攻击加成" and enhance_type != u"暴击"):
            return False
        if (mitama_info[attack_buf] and mitama_info[attack_buf] > 0):
            return True
        if (mitama_info[crit_rate] and mitama_info[crit_rate] > 0):
            return True
        if (mitama_info[crit_damage] and mitama_info[crit_damage] > 0):
            return True
        return False
    d1 = filter(prop_value_quick, d1)
    d2 = filter(prop_value_quick, d2)
    #for i in d2:
    #    print(('%s' % i).decode('raw_unicode_escape'))
    d3 = filter(prop_value_quick, d3)
    d4 = filter(prop_value_quick, d4)
    d5 = filter(prop_value_quick, d5)
    d6 = filter(prop_value_quick, d6)
    def prop_value_attack_buf(mitama):
        mitama_info = mitama.values()[0]
        if (mitama_info[speed] and mitama_info[speed] >= speed_1p_limit):
            return True
        if (mitama_info[attack_buf] and mitama_info[attack_buf] >= 55):
            return True
        return False
    d2 = filter(prop_value_attack_buf, d2)
    d4 = filter(prop_value_attack_buf, d4)

    print('after filter by loc prop %s %s %s %s %s %s' % (len(d1), len(d2),
                                                          len(d3), len(d4),
                                                          len(d5), len(d6)))
    return dict(zip(range(1, 7), [d1, d2, d3, d4, d5, d6]))


mitama_codes = []
mitama_codes_2p_suit_mask = int(0)
mitama_codes_4p_suit_mask = int(0)
mitama_codes_2p_attack_buf_mask = int(0)
mitama_codes_2p_crit_rate_mask = int(0)
mitama_codes_4p_attack_buf_mask = int(0)
mitama_codes_4p_crit_rate_mask = int(0)
mitama_codes_2p_fortune_mask = int(0)
mitama_codes_4p_fortune_mask = int(0)
mitama_codes_4p_seductress_mask = int(0)
mitama_codes_4p_shadow_mask = int(0)

def build_type_list():
    global mitama_codes
    global mitama_codes_2p_suit_mask
    global mitama_codes_4p_suit_mask
    global mitama_codes_2p_attack_buf_mask
    global mitama_codes_4p_attack_buf_mask
    global mitama_codes_2p_crit_rate_mask
    global mitama_codes_4p_crit_rate_mask
    global mitama_codes_2p_fortune_mask
    global mitama_codes_4p_fortune_mask
    global mitama_codes_4p_seductress_mask
    global mitama_codes_4p_shadow_mask

    for (k, v) in data_format.MITAMA_ENHANCE.items():
        enhance_type = v[u"加成类型"]
        if k == u'鸣屋' or k == u'破势' or k == u'针女':
            mitama_codes_2p_suit_mask |= (2 << (3 * len(mitama_codes)))
            mitama_codes_4p_suit_mask |= (4 << (3 * len(mitama_codes)))
        if k == data_format.MITAMA_TYPES[4]:
            mitama_codes_4p_seductress_mask |= (4 << (3 * len(mitama_codes)))
        if k == data_format.MITAMA_TYPES[34]:
            mitama_codes_4p_shadow_mask |= (4 << (3 * len(mitama_codes)))
        if k == data_format.MITAMA_TYPES[18]:
            mitama_codes_2p_fortune_mask |= (2 << (3 * len(mitama_codes)))
            mitama_codes_4p_fortune_mask |= (4 << (3 * len(mitama_codes)))
            mitama_codes.append(k)
            continue
        if enhance_type == u"攻击加成":
            mitama_codes_2p_attack_buf_mask |= (2 << (3 * len(mitama_codes)))
            mitama_codes_4p_attack_buf_mask |= (4 << (3 * len(mitama_codes)))
            mitama_codes.append(k)
        if enhance_type == u"暴击":
            mitama_codes_2p_crit_rate_mask |= (2 << (3 * len(mitama_codes)))
            mitama_codes_4p_crit_rate_mask |= (2 << (3 * len(mitama_codes)))
            mitama_codes.append(k)

def map2list(codes, dx):
    l = []
    mitama_codes_num = len(codes)
    for i in dx:
        code = -1
	k = i.keys()[0]
        v = i.values()[0]
	#print(('map2list: %s' % v).decode('raw_unicode_escape'))
        for j in xrange(mitama_codes_num):
            if codes[j] == v[suit]:
                code = j
                break
        val = int(2)
        val += int(v[attack_buf])
        val <<= 8
        val += int(v[crit_rate])
        val <<= 8
        val += int(v[crit_damage])
        val <<= 8
        val += int(v[speed])
        l.append([val,
                  (1 << (3 * code)) if (code >= 0) else 0,
                  k])
    return l
def list2map(codes, nx, ny, nz, mask, soul):
    mitama_type = soul
    if ny:
        for i in xrange(len(codes)):
            if ny & (mask << (3 * i)):
                mitama_type = codes[i]
    return {data_format.MITAMA_COL_NAME_ZH[0]: nz,
            attack_buf:  (nx>>24)&0xff,
            crit_rate:   (nx>>16)&0xff,
            crit_damage: (nx>> 8)&0xff,
            speed:       (nx>> 0)&0xff,
            suit:        mitama_type}


def make_combination(mitama_data, mitama_type_limit={}, all_suit=True):
    d1, d2, d3, d4, d5, d6 = mitama_data.values()
    build_type_list()
    print(('build %x %d %s' % (mitama_codes_4p_suit_mask, len(mitama_codes), mitama_codes)).decode('raw_unicode_escape'))
    l1 = map2list(mitama_codes, d1)
    d2.sort(lambda x, y: cmp(x.values()[0][speed], y.values()[0][speed]), reverse=True)
    #for i2 in d2:
    #    print(('%s' % i2).decode('raw_unicode_escape'))
    l2 = map2list(mitama_codes, d2)
    l3 = map2list(mitama_codes, d3)
    l4 = map2list(mitama_codes, d4)
    l5 = map2list(mitama_codes, d5)
    l6 = map2list(mitama_codes, d6)

    result_num = 0
    suit_num = 0
    attack_buf_base = 100
    crit_damage_base = 160
    #fast_damage_max = (attack_buf_base + 55) * (crit_damage_base + 104)
    #damage_max = (attack_buf_base + 55) * (crit_damage_base + 111)
    damage_max = 60000
    fast_damage_max = 60000
    fast_shadow_damage_max = 59000
    fast_seductress_damage_max = 59000

    #fast_crit_damage_max = 104
    #crit_damage_max = 111
    #attack_buf_max = 55

    fortune_speed_max = 120
    speed_max = 145
    for i2 in l2:
        speedsuit = ((i2[0] & 0xff) >= 57)
        for i4 in l4:
            if speedsuit:
                if ((i4[0] & 0xff) < speed_1p_limit):
                    continue
            else:
                if ((i4[0] >> 24) & 0xff) < 55:
                    continue
                if i4[0] & 0xffffff00 == 0:
                    continue
            t2 = i2[1] + i4[1]
            n2 = i2[0] + i4[0]
            for i6 in l6:
                if speedsuit:
                    if ((i6[0] & 0xff) < speed_1p_limit):
                        continue
                else:
                    if i6[0] & 0xffffff00 == 0:
                        continue
                    if ((i6[0] >> 16) & 0xff) < 55 and ((i6[0] >> 8) & 0xff) < 89:
                        continue
                t3 = t2 + i6[1]
                n3 = n2 + i6[0]
                for i1 in l1:
                    t4 = t3 + i1[1]
                    if speedsuit:
                        if ((i1[0] & 0xff) < speed_1p_limit):
                            continue
                        #if (t4 & mitama_codes_2p_fortune_mask) == 0 and (t4 & mitama_codes_4p_fortune_mask) == 0:
                        #    continue
                    else:
                        if i1[0] & 0xffffff00 == 0:
                            continue
                        if (t4 & mitama_codes_2p_suit_mask) == 0 and (t4 & mitama_codes_4p_suit_mask) == 0:
                            continue
                    n4 = n3 + i1[0]
                    for i3 in l3:
                        if speedsuit:
                            if ((i3[0] & 0xff) < speed_1p_limit):
                                continue
                        else:
                            if i3[0] & 0xffffff00 == 0:
                                continue
                        t5 = t4 + i3[1]
                        n5 = n4 + i3[0]
                        for i5 in l5:
                            if speedsuit:
                                if (i5[0] & 0xff) < speed_1p_limit:
                                    continue
                                n6 = n5 + i5[0]
                                t6 = t5 + i5[1]
                                if (t6 & mitama_codes_4p_fortune_mask):
                                    if fortune_speed_max > (n6 & 0xff):
                                        continue
                                    fortune_speed_max = (n6 & 0xff) + 1
                                else:
                                    if speed_max > (n6 & 0xff):
                                        continue
                                    speed_max = (n6 & 0xff) + 1
                                    t6 = 0
                                d = 0
                            else:
                                if i5[0] & 0xffffff00 == 0:
                                    continue
                                t6 = t5 + i5[1]
                                if (t6 & mitama_codes_4p_suit_mask) == 0:
                                    continue
                                suit_num += 1
                                n6 = n5 + i5[0]
                                #test crit rate with suit enhance
                                if t6 & mitama_codes_2p_crit_rate_mask:
                                    n6 += (15 << 16)
                                if t6 & mitama_codes_4p_crit_rate_mask:
                                    n6 += (15 << 16)
                                if ((n6 >> 16) & 0xff) < 89:
                                    continue
                                #test attack
                                if t6 & mitama_codes_2p_attack_buf_mask:
                                    n6 += (15 << 24)
                                if t6 & mitama_codes_4p_attack_buf_mask:
                                    n6 += (15 << 24)
                                #test speed
                                #test crit damage
                                ab = (n6 >> 24) & 0xff
                                cd = (n6 >> 8) & 0xff
                                d = (attack_buf_base + ab) * (crit_damage_base + cd)
                                if (n6 & 0xff) < 11:
                                    if d < damage_max:
                                        continue
                                    damage_max = d + 1
                                    #if cd < crit_damage_max:
                                    #    continue
                                    #if attack_buf_max <= ab:
                                    #    attack_buf_max = ab + 1
                                    #    crit_damage_max = cd + 1
                                else:
                                    if t6 & mitama_codes_4p_seductress_mask:
                                        if d < fast_seductress_damage_max:
                                            continue
                                        fast_seductress_damage_max = d + 1
                                    elif t6 & mitama_codes_4p_shadow_mask:
                                        if d < fast_shadow_damage_max:
                                            continue
                                        fast_shadow_damage_max = d + 1
                                    else:
                                        if d < fast_damage_max:
                                            continue
                                        fast_damage_max = d + 1
                                    #if cd < fast_crit_damage_max:
                                    #    continue
                                    #if 1:
                                    #    fast_crit_damage_max = cd + 1
                                    #    if crit_damage_max < fast_crit_damage_max:
                                    #        crit_damage_max = fast_crit_damage_max

                            result_num += 1
                            comb_sum = list2map(mitama_codes, n6, t6 & (mitama_codes_4p_suit_mask | mitama_codes_4p_fortune_mask), '', 4, '')
                            print(('%s %s' % (d, comb_sum)).decode('raw_unicode_escape'))
                            mitama_comb = [{'1': list2map(mitama_codes, i1[0], i1[1], i1[2], 1, i1[2])},
                                           {'2': list2map(mitama_codes, i2[0], i2[1], i2[2], 1, i2[2])},
                                           {'3': list2map(mitama_codes, i3[0], i3[1], i3[2], 1, i3[2])},
                                           {'4': list2map(mitama_codes, i4[0], i4[1], i4[2], 1, i4[2])},
                                           {'5': list2map(mitama_codes, i5[0], i5[1], i5[2], 1, i5[2])},
                                           {'6': list2map(mitama_codes, i6[0], i6[1], i6[2], 1, i6[2])}]
                            comb_data = {'sum': comb_sum,
                                         'info': mitama_comb}
                            yield comb_data
    #print('res:%d suit:%d' % (result_num, suit_num))

