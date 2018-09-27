# coding: utf-8

import itertools
import sys

from calculator_of_Onmyoji import data_format

attack_buf  = data_format.MITAMA_PROPS[1]
crit_rate   = data_format.MITAMA_PROPS[4]
crit_damage = data_format.MITAMA_PROPS[5]
speed       = data_format.MITAMA_PROPS[10]
effect      = data_format.MITAMA_PROPS[8]
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

def filter_fast(data_dict):
    done = set()

    def prop_value_none(mitama):
        if mitama.keys()[0] in done:
            return False
        return True
    def prop_value_speed(mitama):
        if mitama.keys()[0] in done:
            return False
        mitama_info = mitama.values()[0]
        if (mitama_info[speed] and mitama_info[speed] >= speed_1p_limit):
            return True
        return False
    def prop_value_effect(mitama):
        if mitama.keys()[0] in done:
            return False
        mitama_info = mitama.values()[0]
        if (mitama_info[effect] and mitama_info[effect] > 0):
            return True
        return False
    def prop_value_damage(mitama):
        if mitama.keys()[0] in done:
            return False
        mitama_info = mitama.values()[0]
        return False
    def prop_value_l2_speed(mitama):
        if mitama.keys()[0] in done:
            return False
        mitama_info = mitama.values()[0]
        if (mitama_info[speed] and mitama_info[speed] >= 57):
            return True
        return False
    def prop_value_l4_effect(mitama):
        if mitama.keys()[0] in done:
            return False
        mitama_info = mitama.values()[0]
        if (mitama_info[effect] and mitama_info[effect] >= 55):
            return True
        return False
    def prop_value_l2_attack(mitama):
        if mitama.keys()[0] in done:
            return False
        mitama_info = mitama.values()[0]
        if (mitama_info[attack_buf] and mitama_info[attack_buf] >= 55):
            return True
        return False
    def prop_value_l6_crit_damage(mitama):
        if mitama.keys()[0] in done:
            return False
        mitama_info = mitama.values()[0]
        if (mitama_info[crit_damage] and mitama_info[crit_damage] >= 89):
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
                #print(k)
                soul_2p_fortune_mask |= (2 << (3 * len(soul)))
                soul_4p_fortune_mask |= (4 << (3 * len(soul)))
                soul.append(k)
                break
        return soul, soul_2p_fortune_mask, soul_4p_fortune_mask
    def build_mask_fortune_effect():
        soul = []
        soul_2p_fortune_mask = int(0)
        soul_4p_fortune_mask = int(0)
        for (k, v) in data_format.MITAMA_ENHANCE.items():
            enhance_type = v[u"加成类型"]
            if k == data_format.MITAMA_TYPES[18]:
                soul_2p_fortune_mask |= (2 << (3 * len(soul)))
                soul_4p_fortune_mask |= (4 << (3 * len(soul)))
                soul.append(k)
                continue
            if enhance_type == u'效果命中':
                soul_2p_fortune_mask |= (2 << (3 * len(soul)))
                soul.append(k)
                continue
        return soul, soul_2p_fortune_mask, soul_4p_fortune_mask
    def build_mask_sprite():
        soul = []
        soul_2p_fortune_mask = int(0)
        soul_4p_fortune_mask = int(0)
        for (k, v) in data_format.MITAMA_ENHANCE.items():
            if k == data_format.MITAMA_TYPES[2]:
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
                continue
            if enhance_type == u'效果命中':
                soul_2p_fortune_mask |= (2 << (3 * len(soul)))
                soul.append(k)
                continue
        return soul, soul_2p_fortune_mask, soul_4p_fortune_mask
    def build_mask_shadow():
        soul = []
        soul_2p_fortune_mask = int(0)
        soul_4p_fortune_mask = int(0)
        for (k, v) in data_format.MITAMA_ENHANCE.items():
            enhance_type = v[u"加成类型"]
            if k == data_format.MITAMA_TYPES[34]:
                soul_2p_fortune_mask |= (2 << (3 * len(soul)))
                soul_4p_fortune_mask |= (4 << (3 * len(soul)))
                soul.append(k)
                continue
            if enhance_type == u"暴击":
                #print(k)
                soul_2p_fortune_mask |= (2 << (3 * len(soul)))
                soul.append(k)
                continue
        return soul, soul_2p_fortune_mask, soul_4p_fortune_mask
    def build_mask_seductress():
        soul = []
        soul_2p_fortune_mask = int(0)
        soul_4p_fortune_mask = int(0)
        for (k, v) in data_format.MITAMA_ENHANCE.items():
            enhance_type = v[u"加成类型"]
            if k == data_format.MITAMA_TYPES[4]:
                #print(k)
                soul_2p_fortune_mask |= (2 << (3 * len(soul)))
                soul_4p_fortune_mask |= (4 << (3 * len(soul)))
                soul.append(k)
                continue
            if enhance_type == u"暴击":
                #print(k)
                soul_2p_fortune_mask |= (2 << (3 * len(soul)))
                soul.append(k)
                continue
        return soul, soul_2p_fortune_mask, soul_4p_fortune_mask
    def test_limit_1p_speed(n):
        return (n & 0xff) < speed_1p_limit

    def score_suit_buf_max_speed(soul_2p_mask, buf_max, n, t):
        if buf_max >= (n & 0xff):
            return buf_max, n, True
        return (n & 0xff), n, False
    def score_suit_buf_max_effect(soul_2p_mask, buf_max, n, t):
        #test effect with suit enhance
        if t & soul_2p_mask:
            n += (15 << 32)
        #test speed
        if (n & 0xff) < 11 or (n & 0xff) > 80:
            return buf_max, n, True
        if buf_max >= ((n >> 32) & 0xff):
            return buf_max, n, True
        return ((n >> 32) & 0xff), n, False
    damage_min_speed = 11
    def score_suit_buf_max_damage(soul_2p_mask, buf_max, n, t):
        #test speed
        if (n & 0xff) < damage_min_speed:
            return buf_max, n, True
        #test crit rate with suit enhance
        if t & soul_2p_mask == 0:
            return buf_max, n, True
        n += (30 << 16)
        #test crit rate
        if ((n >> 16) & 0xff) < 89:
            return buf_max, n, True
        attack_buf_base = 100
        crit_damage_base = 160
        ab = (n >> 24) & 0xff
        cd = (n >>  8) & 0xff
        d = (attack_buf_base + ab) * (crit_damage_base + cd)
        if buf_max >= d:
            return buf_max, n, True
        return d + 1, n, False

    if 1:
        res, com, n = filter_soul(prop_value_speed,
                          prop_value_l2_speed,
                          prop_value_speed,
                          prop_value_speed,
                          build_mask_fortune,
                          speed,
                          True,
                          score_suit_buf_max_speed,
                          data_dict)
        if len(res) > 0:
            comb_data = make_result(data_dict, res, com)
            print(('%d %s' % (n, comb_data['sum'])).decode('raw_unicode_escape'))
            yield comb_data
    if 1:
        res, com, n = filter_soul(prop_value_speed,
                          prop_value_l2_speed,
                          prop_value_speed,
                          prop_value_speed,
                          build_mask_none,
                          speed,
                          True,
                          score_suit_buf_max_speed,
                          data_dict)
        if len(res) > 0:
            for x in res:
                done.add(x)
            comb_data = make_result(data_dict, res, com)
            print(('%d %s' % (n, comb_data['sum'])).decode('raw_unicode_escape'))
            yield comb_data
    if 0:
        res, com, n = filter_soul(prop_value_speed,
                          prop_value_l2_speed,
                          prop_value_speed,
                          prop_value_speed,
                          build_mask_fire,
                          speed,
                          True,
                          score_suit_buf_max_speed,
                          data_dict)
        if len(res) > 0:
            for x in res:
                done.add(x)
            comb_data = make_result(data_dict, res, com)
            print(('%d %s' % (n, comb_data['sum'])).decode('raw_unicode_escape'))
            yield comb_data
    soul_crit = []
    for (k, v) in data_format.MITAMA_ENHANCE.items():
        enhance_type = v[u"加成类型"]
        if enhance_type == u"暴击":
            soul_crit.append(k)
            continue
    if 0:
        type_shadow = u'破势'
        damage = 0
        res = []
        com = {}
        for s in soul_crit:
            print('4%s + 2%s' % (type_shadow, s))
            def prop_value_crit(mitama):
                if mitama.keys()[0] in done:
                    return False
                enhance_type = mitama.values()[0][u'御魂类型']
                return enhance_type == type_shadow or enhance_type == s

            r, c, n = filter_soul(prop_value_crit,
                                    prop_value_l2_attack,
                                    prop_value_l2_attack,
                                    prop_value_l6_crit_damage,
                                    build_mask_shadow,
                                    crit_rate,
                                    False,
                                    score_suit_buf_max_damage,
                                    data_dict)
            if n > damage:
                damage = n
                res = r
                com = c
        if len(res) > 0:
            comb_data = make_result(data_dict, res, com)
            print(('%d %s' % (damage, comb_data['sum'])).decode('raw_unicode_escape'))
            yield comb_data
    if 1:
        damage_min_speed = 11
        type_seductress = u'针女'
        damage = 0
        res = []
        com = {}
        for s in soul_crit:
            print('4%s + 2%s' % (type_seductress, s))
            def prop_value_type(mitama):
                if mitama.keys()[0] in done:
                    return False
                enhance_type = mitama.values()[0][u'御魂类型']
                return enhance_type == type_seductress or enhance_type == s

            r, c, n = filter_soul(prop_value_type,
                                  prop_value_l2_speed,
                                  prop_value_l2_attack,
                                  prop_value_l6_crit_damage,
                                  build_mask_seductress,
                                  speed,
                                  False,
                                  score_suit_buf_max_damage,
                                  data_dict)
            if n > damage:
                damage = n
                res = r
                com = c
        if len(res) > 0:
            comb_data = make_result(data_dict, res, com)
            print(('%d %s' % (damage, comb_data['sum'])).decode('raw_unicode_escape'))
            yield comb_data
    if 0:
        damage_min_speed = 11
        type_seductress = u'针女'
        damage = 0
        res = []
        com = {}
        for s in soul_crit:
            print('4%s + 2%s' % (type_seductress, s))
            def prop_value_crit(mitama):
                if mitama.keys()[0] in done:
                    return False
                enhance_type = mitama.values()[0][u'御魂类型']
                return enhance_type == type_seductress or enhance_type == s

            r, c, n = filter_soul(prop_value_crit,
                                    prop_value_l2_attack,
                                    prop_value_l2_attack,
                                    prop_value_l6_crit_damage,
                                    build_mask_seductress,
                                    crit_rate,
                                    False,
                                    score_suit_buf_max_damage,
                                    data_dict)
            if n > damage:
                damage = n
                res = r
                com = c
        if len(res) > 0:
            for x in res:
                done.add(x)
            comb_data = make_result(data_dict, res, com)
            print(('%d %s' % (damage, comb_data['sum'])).decode('raw_unicode_escape'))
            yield comb_data
    if 1:
        res, com, n = filter_soul(prop_value_none,
                          prop_value_speed,
                          prop_value_none,
                          prop_value_none,
                          build_mask_sprite,
                          speed,
                          True,
                          score_suit_buf_max_speed,
                          data_dict)
        if len(res) > 0:
            for x in res:
                done.add(x)
            comb_data = make_result(data_dict, res, com)
            print(('%d %s' % (n, comb_data['sum'])).decode('raw_unicode_escape'))
            yield comb_data
    soul_effect = []
    for (k, v) in data_format.MITAMA_ENHANCE.items():
        enhance_type = v[u"加成类型"]
        if enhance_type == u'效果命中':
            soul_effect.append(k)
            continue
    for i in xrange(2):
        effect_buf = 0
        res = []
        com = {}
        for s in soul_effect:
            print('4%s + 2%s' % ('Fortune', s))
            r, c, n = filter_soul(prop_value_effect,
                                  prop_value_effect,
                                  prop_value_l4_effect,
                                  prop_value_effect,
                                  build_mask_fortune_effect,
                                  effect,
                                  False,
                                  score_suit_buf_max_effect,
                                  data_dict)
            if n > effect_buf:
                effect_buf = n
                res = r
                com = c
        if len(res) > 0:
            for x in res:
                done.add(x)
            comb_data = make_result(data_dict, res, com)
            print(('%d %s' % (effect_buf, comb_data['sum'])).decode('raw_unicode_escape'))
            yield comb_data
    if 0:
        res, com, n = filter_soul(prop_value_none,
                          prop_value_none,
                          prop_value_none,
                          prop_value_none,
                          build_mask_fire,
                          speed,
                          True,
                          score_suit_buf_max_effect,
                          data_dict)
        if len(res) > 0:
            comb_data = make_result(data_dict, res, com)
            print(('%d %s' % (n, comb_data['sum'])).decode('raw_unicode_escape'))
            yield comb_data


def make_result(data_dict, res, com):
    d1, d2, d3, d4, d5, d6 = data_dict.values()
    comb_data = {'sum': com,
                 'info': [find_item(d1, res[0]),
                          find_item(d2, res[1]),
                          find_item(d3, res[2]),
                          find_item(d4, res[3]),
                          find_item(d5, res[4]),
                          find_item(d6, res[5])]
                }
    return comb_data

def filter_soul(prop_value, prop_value_l2, prop_value_l4, prop_value_l6,
                build_mask, sortkey,
                find_one,
                score_suit_buf_max,
                data_dict):
    d1, d2, d3, d4, d5, d6 = data_dict.values()

    d2 = filter(prop_value_l2, d2)
    d4 = filter(prop_value_l4, d4)
    d6 = filter(prop_value_l6, d6)
    d1 = filter(prop_value, d1)
    d3 = filter(prop_value, d3)
    d5 = filter(prop_value, d5)
    #print('%d x %d x %d x %d x %d x %d' % (len(d1), len(d2), len(d3), len(d4), len(d5), len(d5)))
    #for i in d1:
    #    print('%s' % i.values()[0][suit])
    #    #print(('%s' % i.values()[0][suit]).decode('raw_unicode_escape'))
    #return []

    if sortkey is not None:
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

    suit_buf_max = 1
    result_num = 0
    result = []
    comb_sum = {}
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
                                suit_buf_max, n6, ok = score_suit_buf_max(soul_2p_mask,
                                                                          suit_buf_max,
                                                                          n6, t6)
                                if ok:
                                    continue
                            else:
                                continue
                            result_num += 1
                            result = [i1[2], i2[2], i3[2], i4[2], i5[2], i6[2]]
                            comb_sum = list2map(soul,
                                                n6, t6 & soul_4p_mask, '',
                                                4, '')
                            if find_one:
                                #print(('%s %s' % (d, comb_sum)).decode('raw_unicode_escape'))
                                #print('result: %s' % result)
                                return result, comb_sum, suit_buf_max
    #print('result: %s' % result)
    #print(('%s %s' % (d, comb_sum)).decode('raw_unicode_escape'))
    return result, comb_sum, suit_buf_max

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

def find_item(arr, k):
    for i in arr:
        if i.keys()[0] == k:
            return i
    return None

def map2list(codes, dx):
    l = []
    mitama_codes_num = len(codes)
    #print(('map2list: %s' % dx).decode('raw_unicode_escape'))
    for i in dx:
        code = -1
        k = i.keys()[0]
        v = i.values()[0]
	#print(('map2list: %s' % v).decode('raw_unicode_escape'))
        for j in xrange(mitama_codes_num):
            if codes[j] == v[suit]:
                code = j
                break
        val = int(0)
        val += int(v[effect])
        val <<= 8
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
        for i4 in l4:
            if ((i4[0] >> 24) & 0xff) < 55:
                continue
            if i4[0] & 0xffffff00 == 0:
                continue
            t2 = i2[1] + i4[1]
            n2 = i2[0] + i4[0]
            for i6 in l6:
                if i6[0] & 0xffffff00 == 0:
                    continue
                if ((i6[0] >> 16) & 0xff) < 55 and ((i6[0] >> 8) & 0xff) < 89:
                    continue
                t3 = t2 + i6[1]
                n3 = n2 + i6[0]
                for i1 in l1:
                    t4 = t3 + i1[1]
                    if i1[0] & 0xffffff00 == 0:
                        continue
                    if (t4 & mitama_codes_2p_suit_mask) == 0 and (t4 & mitama_codes_4p_suit_mask) == 0:
                        continue
                    n4 = n3 + i1[0]
                    for i3 in l3:
                        if i3[0] & 0xffffff00 == 0:
                            continue
                        t5 = t4 + i3[1]
                        n5 = n4 + i3[0]
                        for i5 in l5:
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

