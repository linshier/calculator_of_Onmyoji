# coding: utf-8

import itertools
import sys
import multiprocessing
import uuid
#from multiprocessing import Pool

from calculator_of_Onmyoji import data_format

attack      = data_format.MITAMA_PROPS[0]
attack_buf  = data_format.MITAMA_PROPS[1]
crit_rate   = data_format.MITAMA_PROPS[4]
crit_damage = data_format.MITAMA_PROPS[5]
speed       = data_format.MITAMA_PROPS[10]
effect      = data_format.MITAMA_PROPS[8]
soul_sn     = data_format.MITAMA_COL_NAME_ZH[0]
suit        = data_format.MITAMA_COL_NAME_ZH[1]

speed_1p_limit = 3
speed_1p_limit = 1

selected = set()

effect_min_speed = 0
effect_max_speed = 200
damage_min_speed = 11
damage_max_speed = 500
damage_limit = 0
damage_indirect = 0
damage_min_crit_rate = 90
attack_buf_base = 100
crit_damage_base = 160
attack_hero = 3350
effect_buf_base = 0
# |-effect(11)-|-attackbuf(14)-|-critrate(13)-|-critdamage(11)-|-speed(12)-|
# |-resit(11)--|-hpbuf(14)-----|-critrate(13)-|-critdamage(11)-|-speed(12)-|
bits_speed = 14
bits_critdamage = 11
bits_critrate = 13
bits_attackbuf = 14
bits_effect = 11
#
offset_speed = 0
offset_critdamage = offset_speed + bits_speed
offset_critrate = offset_critdamage + bits_critdamage
offset_attackbuf = offset_critrate + bits_critrate
offset_effect = offset_attackbuf + bits_attackbuf

def __decode(v, offset, bits):
    return (v >> offset) & ((1 << bits) - 1)

def score_suit_buf_max_speed(soul_2p_mask, buf_max, n, t):
    if __decode(n, offset_speed, bits_speed) <= buf_max:
        return buf_max, n, True
    return __decode(n, offset_speed, bits_speed), n, False
def score_suit_buf_max_effect(soul_2p_mask, buf_max, n, t):
    #test speed
    if __decode(n, offset_speed, bits_speed) < effect_min_speed * 100 or __decode(n, offset_speed, bits_speed) > effect_max_speed * 100:
        return buf_max, n, True
    #test effect with suit enhance
    if buf_max >= __decode(n, offset_effect, bits_effect):
        return buf_max, n, True
    return __decode(n, offset_effect, bits_effect), n, False

def score_suit_buf_max_damage(soul_2p_mask, buf_max, n, t):
    #test speed
    if __decode(n, offset_speed, bits_speed) < damage_min_speed * 100 or __decode(n, offset_speed, bits_effect) > damage_max_speed * 100:
        return buf_max, 1, True
    ##test crit rate with suit enhance
    if soul_2p_mask and (t & soul_2p_mask) == 0:
        return buf_max, 2, True
    #test crit rate
    if __decode(n, offset_critrate, bits_critrate) < damage_min_crit_rate * 10:
        return buf_max, 3, True
    ab = attack_buf_base * 10 + __decode(n, offset_attackbuf, bits_attackbuf)
    cd = crit_damage_base * 10 + __decode(n, offset_critdamage, bits_critdamage)
    d = ab * cd
    #print attack_buf_base + ab, crit_damage_base + cd, d
    #if (ab == 129) and (cd == 360): print 'score:', d, attack_buf_base, crit_damage_base
    if buf_max >= d:
        return buf_max, 4, True
    if 0 < damage_limit and damage_limit < int(attack_hero * d / 1000000 / 100):
        return buf_max, 5, True
    #print damage_limit, d
    return d + 1, n, False

def mprun(a):
    find_one = a[0]
    l1, i2, l3, l4, l5, l6 = a[1], a[2], a[3], a[4], a[5], a[6]
    soul, soul_2p_mask, soul_4p_mask = a[7], a[8], a[9]
    score_suit_buf_max = a[10]
    suit_buf_max_ = 1
    result_ = []
    comb_sum_ = {}
    n_ = 0
    ns = 0
    for i4 in l4:
        t2 = i2[1] + i4[1]
        n2 = i2[0] + i4[0]
        for i6 in l6:
            t3 = t2 + i6[1]
            n3 = n2 + i6[0]
            for i1 in l1:
                t4 = t3 + i1[1]
                n4 = n3 + i1[0]
                #if soul_2p_mask and soul_4p_mask \
                # and (t4 & soul_2p_mask) == 0 and (t4 & soul_4p_mask) == 0:
                #    continue
                for i3 in l3:
                    t5 = t4 + i3[1]
                    n5 = n4 + i3[0]
                    for i5 in l5:
                        n6 = n5 + i5[0]
                        t6 = t5 + i5[1]
                        ns += 1
                        if soul_4p_mask == 0 or (t6 & soul_4p_mask):
                            suit_buf_max_, n6, skip = score_suit_buf_max(soul_2p_mask, suit_buf_max_, n6, t6)
                            if skip:
                                continue
                            #print suit_buf_max_
                        else:
                            continue
                        #result_num += 1
                        result_ = [i1[2], i2[2], i3[2], i4[2], i5[2], i6[2]]
                        comb_sum_ = list2map(soul,
                                             n6, t6 & soul_4p_mask, '',
                                             4, '')
                        n_ = n6
                        if find_one:
                            return [result_, comb_sum_, suit_buf_max_, n_]
    r = [result_, comb_sum_, suit_buf_max_, n_]
    #print(r, ns)
    return r


def filter_loc_prop(data_list, prop_type, prop_min_value):
    def prop_value_le_min(mitama):
        mitama_info = mitama.values()[0]
        if (mitama_info[prop_type] and
                mitama_info[prop_type] >= prop_min_value):
            return True
        else:
            return False
    return filter(prop_value_le_min, data_list)

def filter_soul(prop_value, prop_value_l2, prop_value_l4, prop_value_l6,
                build_mask, sortkey,
                find_one,
                score_suit_buf_max,
                data_dict):
    d1, d2, d3, d4, d5, d6 = data_dict.values()

    d2 = filter(prop_value_l2, filter(prop_value, d2))
    d4 = filter(prop_value_l4, filter(prop_value, d4))
    d6 = filter(prop_value_l6, filter(prop_value, d6))
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
    comb_code = 0

    args = []
    for i2 in l2:
        args.append([find_one, l1, i2, l3, l4, l5, l6, soul, soul_2p_mask, soul_4p_mask, score_suit_buf_max])
    rarr = []
    if 0:
        for a in args:
            rarr.append(mprun(a))
    else:
        pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
        rarr = pool.map(mprun, args)
        pool.close()
        pool.join()
    for ra in rarr:
        r, c, b, v = ra[0], ra[1], ra[2], ra[3]
        #print(ra)
        if b > suit_buf_max:
            result, comb_sum, suit_buf_max, comb_code = r, c, b, v
            #print b, __decode(v, offset_attackbuf, bits_attackbuf), __decode(v, offset_critdamage, bits_critdamage)
    #print('result: %s' % result)
    #print(('%s %s' % (d, comb_sum)).decode('raw_unicode_escape'))
    return result, comb_sum, suit_buf_max, comb_code

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

def map2list(codes, dx):
    l = []
    mitama_codes_num = len(codes)
    #print(('map2list: %s' % dx).decode('raw_unicode_escape'))
    for i in dx:
        code = -1
        k = i.keys()[0]
        v = i.values()[0]
        #print(('map2list: %s %s' % (k, v)).decode('raw_unicode_escape'))
        for j in xrange(mitama_codes_num):
            if codes[j] == v[suit]:
                code = j
                break
        val = int(0)
        #if k == '5b47041108942d6ee02ea362': print 'map2list', v[attack], (int(v[attack_buf]) + int(v[attack]*100/attack_hero))
        val <<= bits_effect
        val += int(v[effect] * 10)
        val <<= bits_attackbuf
        val += (int(v[attack_buf] * 10) + int(v[attack]*100/attack_hero * 10))
        val <<= bits_critrate
        val += int(v[crit_rate] * 10)
        val <<= bits_critdamage
        val += int(v[crit_damage] * 10)
        val <<= bits_speed
        val += int(v[speed] * 100)
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
            attack_buf:  __decode(nx, offset_attackbuf, bits_attackbuf),
            crit_rate:   __decode(nx, offset_critrate, bits_critrate),
            crit_damage: __decode(nx, offset_critdamage, bits_critdamage),
            speed:       __decode(nx, offset_speed, bits_speed),
            suit:        mitama_type}

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

def filter_fast(data_dict):
    for i in xrange(6):
        v = data_dict[i+1][0].values()[0]
        f = {('%s' % uuid.uuid1()).decode('utf-8'): {k: 0 for k in v.keys()}}
        data_dict[i+1].append(f)

    type_none = 0
    type_sprite = data_format.MITAMA_TYPES[2]
    type_seductress = data_format.MITAMA_TYPES[4]
    type_spider = data_format.MITAMA_TYPES[6]
    type_skull = data_format.MITAMA_TYPES[8]
    type_jizo = data_format.MITAMA_TYPES[12]
    type_semisen = data_format.MITAMA_TYPES[15]
    type_fortune = data_format.MITAMA_TYPES[18]
    type_scarlet = data_format.MITAMA_TYPES[24]
    type_fire = data_format.MITAMA_TYPES[25]
    type_watcher = data_format.MITAMA_TYPES[28]
    type_claws = data_format.MITAMA_TYPES[31]
    type_crab = u'网切'
    type_phenix = data_format.MITAMA_TYPES[33]
    type_shadow = data_format.MITAMA_TYPES[34]
    type_tomb = data_format.MITAMA_TYPES[35]
    type_kyoukotsu = data_format.MITAMA_TYPES[36]
    __ = {
        type_none: 'none',
        type_sprite: 'sprite',
        type_seductress: 'seductress',
        type_spider: 'spider',
        type_skull: 'skull',
        type_jizo: 'jizo',
        type_semisen: 'semisen',
        type_fortune: 'fortune',
        type_scarlet: 'scarlet',
        type_fire: 'fire',
        type_watcher: 'watcher',
        type_claws: 'claws',
        type_phenix: 'phenix',
        type_shadow: 'shadow',
        type_tomb: 'tomb',
        type_kyoukotsu: 'kyoukotsu',
    }

    soul_crit = []
    for (k, v) in data_format.MITAMA_ENHANCE.items():
        enhance_type = v[u"加成类型"]
        if enhance_type == u"暴击":
            soul_crit.append(k)
            continue
    soul_attack = []
    for (k, v) in data_format.MITAMA_ENHANCE.items():
        enhance_type = v[u"加成类型"]
        if enhance_type == u'攻击加成':
            soul_attack.append(k)
            continue
    soul_free = set()
    for (k, v) in data_format.MITAMA_ENHANCE.items():
        if v.get(u'加成数值'):
            continue
        #if k != data_format.MITAMA_TYPES[8] and k != data_format.MITAMA_TYPES[6]:
        if k != data_format.MITAMA_TYPES[8]:
            continue
        #print k
        soul_free.add(k)
    soul_effect = []
    for (k, v) in data_format.MITAMA_ENHANCE.items():
        enhance_type = v[u"加成类型"]
        if enhance_type == u'效果命中':
            soul_effect.append(k)
            continue

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
    def prop_value_l6_crit_rate(mitama):
        if mitama.keys()[0] in done:
            return False
        mitama_info = mitama.values()[0]
        if (mitama_info[crit_rate] and mitama_info[crit_rate] >= 55):
            return True
        return False
    def build_mask_none():
        return [], int(0), int(0)
    def build_mask_x_free(soul_x_type):
        soul = []
        soul_2p_mask = int(0)
        soul_4p_mask = int(0)
        for (k, v) in data_format.MITAMA_ENHANCE.items():
            enhance_type = v[u"加成类型"]
            if k == soul_x_type:
                soul_4p_mask |= (4 << (3 * len(soul)))
                soul.append(k)
                continue
            if k in soul_free:
                soul.append(k)
                continue
        return soul, soul_2p_mask, soul_4p_mask
    # fortune type max speed
    #if cal_fortune_max_speed:
    def cal_x_max_speed(soul_x_type):
        def _build_mask():
            soul = []
            soul_2p_mask = int(0)
            soul_4p_mask = int(0)
            for (k, v) in data_format.MITAMA_ENHANCE.items():
                enhance_type = v[u"加成类型"]
                if k == soul_x_type:
                    soul_2p_mask |= (2 << (3 * len(soul)))
                    soul_4p_mask |= (4 << (3 * len(soul)))
                    soul.append(k)
                    break
            return soul, soul_2p_mask, soul_4p_mask
        res, com, n, _ = filter_soul(prop_value_speed,
                          prop_value_l2_speed,
                          prop_value_speed,
                          prop_value_speed,
                          _build_mask,
                          speed,
                          True,
                          score_suit_buf_max_speed,
                          data_dict)
        if len(res) > 0:
            for x in res:
                done.add(x)
            comb_data = make_result(data_dict, res, com)
            print('%s()maxspeed:%.2f,+%.2f' % (__[soul_x_type], n / 100.0, 117 + comb_data['sum'][speed] / 100.0))
            return comb_data
        return None
    def cal_fortune_max_speed():
        return cal_x_max_speed(type_fortune)
    def cal_fire_max_speed():
        return cal_x_max_speed(type_fire)
    # free type max speed
    def cal_freetype_max_speed():
        global effect_min_speed
        global effect_max_speed
        global damage_min_speed
        global damage_max_speed
        global damage_min_crit_rate
        global attack_buf_base
        global crit_damage_base
        res, com, n, _ = filter_soul(prop_value_speed,
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
            #print(('%d %s' % (n, comb_data['sum'])).decode('raw_unicode_escape'))
            print('freetype()maxspeed:%.2f,+%.2f' % (n / 100.0, 119 + n / 100.0))
            return comb_data
        # fast terminate
        if n < 148 * 100:
            print('speed test fail')
            return None

    def cal_x_effect(soul_type, soul_peer, base_speed, prop_value_l2):
        score = 0
        res = []
        com = {}
        cc = 0
        desc = ''
        p = type_none
        for s in soul_peer:
            def __build_mask():
                soul = []
                soul_2p_mask = int(0)
                soul_4p_mask = int(0)
                for (k, v) in data_format.MITAMA_ENHANCE.items():
                    enhance_type = v[u"加成类型"]
                    if k == soul_type:
                        soul_4p_mask |= (4 << (3 * len(soul)))
                    if k == s:
                        soul_2p_mask |= (2 << (3 * len(soul)))
                    if k == soul_type or k == s:
                        soul.append(k)
                        break
                return soul, soul_2p_mask, soul_4p_mask

            r, c, n, _ = filter_soul(prop_value_none,
                              prop_value_l2,
                              prop_value_effect,
                              prop_value_none,
                              __build_mask,
                              effect,
                              True,
                              score_suit_buf_max_effect,
                              data_dict)
            if n > score:
                score, res, com, p = n, r, c, s
        if len(res) > 0:
            for x in res:
                done.add(x)
            comb_data = make_result(data_dict, res, com)
            print('%s(+%s)maxeffect:%.1f,+%.2f' % (__[soul_type], __[p], n / 10.0 + effect_buf_base, base_speed + comb_data['sum'][speed] / 100.0))
            return comb_data
        return None
    def cal_fortune_effect_over200_119():
        global effect_min_speed
        global effect_max_speed
        global effect_buf_base
        effect_min_speed = 200 - 119
        effect_max_speed = 500
        effect_buf_base = 0 + 15
        return cal_x_effect(type_fortune, [type_fire], 119, prop_value_l2_speed)

    # seductress + crit_damage type max damage
    def cal_x_max_damage(soul_type, soul_peer, base_speed, prop_value_l6, buf_limit):
        global effect_min_speed
        global effect_max_speed
        global damage_limit
        damage = 0
        damage_limit = buf_limit
        res = []
        com = {}
        cc = 0
        desc = ''
        p = type_none
        for s in soul_peer:
            def __filter_type(mitama):
                if mitama.keys()[0] in done:
                    return False
                enhance_type = mitama.values()[0][u'御魂类型']
                return enhance_type == soul_type or enhance_type == s
            def __build_mask():
                soul = []
                soul_2p_mask = int(0)
                soul_4p_mask = int(0)
                for (k, v) in data_format.MITAMA_ENHANCE.items():
                    enhance_type = v[u"加成类型"]
                    if k == soul_type:
                        soul_4p_mask |= (4 << (3 * len(soul)))
                    if k == s:
                        soul_2p_mask |= (2 << (3 * len(soul)))
                    if k == soul_type or k == s:
                        soul.append(k)
                if s == type_none:
                    soul_2p_mask |= (2 << (3 * len(soul)))
                    soul.append(type_none)
                #print soul
                return soul, soul_2p_mask, soul_4p_mask

            r, c, n, v = filter_soul(__filter_type,
                                  prop_value_none,
                                  prop_value_none,
                                  prop_value_l6,
                                  __build_mask,
                                  crit_rate,
                                  False,
                                  score_suit_buf_max_damage,
                                  data_dict)
            #if len(r) > 0: print '+type', s, int(attack_hero * n / 1000000 / 100), ('%s' % (make_result(data_dict, r, c)['sum'])).decode('raw_unicode_escape')
            if n > damage:
                damage, res, com, p, cc = n, r, c, s, v
        if len(res) > 0:
            for x in res:
                done.add(x)
            comb_data = make_result(data_dict, res, com)
            print('%s(+%s):%d=%.2f*%.2f,+%.2f' % (
                  __[soul_type], __[p], int(attack_hero * damage / 1000000 / 100),
                  (attack_buf_base * 10.0 + __decode(cc, offset_attackbuf, bits_attackbuf)) / 1000.0 * attack_hero,
                  (crit_damage_base * 10.0 + __decode(cc, offset_critdamage, bits_critdamage)) / 1000.0,
                  base_speed + comb_data['sum'][speed] / 100.0))
            #print('%s(+%s):%d,+%d' % (__[soul_type], __[p], int(damage), base_speed + comb_data['sum'][speed]))
            return comb_data
        return None
    def cal_seductress_crit_over129_3350_11_160_117():
        global attack_hero
        global attack_buf_base
        global damage_min_crit_rate
        global crit_damage_base
        global damage_min_speed
        attack_hero = 3350
        attack_buf_base = 100
        damage_min_crit_rate = 100 - 11 - 30
        crit_damage_base = 160
        damage_min_speed = 129 - 117
        return cal_x_max_damage(type_seductress, soul_crit, 117, prop_value_l6_crit_damage, 0)
    def cal_seductress_crit_over140_3350_11_160_117():
        global attack_hero
        global attack_buf_base
        global damage_min_crit_rate
        global crit_damage_base
        global damage_min_speed
        attack_hero = 3350
        attack_buf_base = 100
        damage_min_crit_rate = 100 - 11 - 30
        crit_damage_base = 160
        damage_min_speed = 140 - 117
        return cal_x_max_damage(type_seductress, soul_crit, 117, prop_value_none, 0)
    def cal_seductress_attack_over140_3350_11_160_117():
        global attack_hero
        global attack_buf_base
        global damage_min_crit_rate
        global crit_damage_base
        global damage_min_speed
        attack_hero = 3350
        attack_buf_base = 100
        damage_min_crit_rate = 100 - 11 - 15
        crit_damage_base = 160 + 15
        damage_min_speed = 140 - 117
        return cal_x_max_damage(type_seductress, soul_attack, 117, prop_value_l6_crit_damage, 0)
    def cal_seductress_over0_3323_10_150_104():
        global attack_hero
        global attack_buf_base
        global damage_min_crit_rate
        global crit_damage_base
        global damage_min_speed
        attack_hero = 3323
        attack_buf_base = 100
        damage_min_crit_rate = 100 - 10 - 30
        crit_damage_base = 150
        damage_min_speed = 104 - 104
        return cal_x_max_damage(type_seductress, soul_crit, 104, prop_value_none, 0)
    def cal_seductress_attack_over0_3377_9_150_109():
        global attack_hero
        global attack_buf_base
        global damage_min_crit_rate
        global crit_damage_base
        global damage_min_speed
        attack_hero = 3377
        attack_buf_base = 100 + 15
        damage_min_crit_rate = 100 - 9 - 15
        crit_damage_base = 150
        damage_min_speed = 109 - 109
        return cal_x_max_damage(type_seductress, soul_attack, 109, prop_value_none, 0)
    def cal_sprite_over140_2332_5_150_108():
        global attack_hero
        global attack_buf_base
        global damage_min_crit_rate
        global crit_damage_base
        global damage_min_speed
        attack_hero = 2332
        attack_buf_base = 100
        damage_min_crit_rate = 100 - 5 - 15
        crit_damage_base = 150
        damage_min_speed = 141 - 108
        return cal_x_max_damage(type_sprite, soul_crit, 108, prop_value_none, 0)
    def cal_jizo_over140_4074_10_150_118():
        global attack_hero
        global attack_buf_base
        global damage_min_crit_rate
        global crit_damage_base
        global damage_min_speed
        attack_hero = 4074
        attack_buf_base = 100
        damage_min_crit_rate = 100 - 10 - 15
        crit_damage_base = 150
        damage_min_speed = 141 - 118
        return cal_x_max_damage(type_jizo, soul_crit, 118, prop_value_none, 0)
    def cal_shadow_indirect_over131_4074_10_150_118():
        global attack_hero
        global attack_buf_base
        global damage_min_crit_rate
        global crit_damage_base
        global damage_min_speed
        global damage_max_speed
        attack_hero = 4074
        attack_buf_base = 100
        damage_min_crit_rate = 100 - 10 - 30
        crit_damage_base = 150 + 211
        damage_min_speed = 130 - 118
        damage_max_speed = 132 - 118
        r = cal_x_max_damage(type_shadow, soul_crit, 118, prop_value_none, 0)
        damage_max_speed = 500
        return r
    def cal_shadow_over0_3350_12_160_110():
        global attack_hero
        global attack_buf_base
        global damage_min_crit_rate
        global crit_damage_base
        global damage_min_speed
        attack_hero = 3350
        attack_buf_base = 100
        damage_min_crit_rate = 100 - 12 - 30
        crit_damage_base = 160
        damage_min_speed = 110 - 110
        return cal_x_max_damage(type_shadow, soul_crit, 110, prop_value_none, 0)
    def cal_shadow_over0_3350_11_160_117():
        global attack_hero
        global attack_buf_base
        global damage_min_crit_rate
        global crit_damage_base
        global damage_min_speed
        attack_hero = 3350
        attack_buf_base = 100 + 15
        damage_min_crit_rate = 100 - 11 - 15
        crit_damage_base = 160
        damage_min_speed = 117 - 117
        return cal_x_max_damage(type_shadow, soul_attack, 117, prop_value_none, 0)
    def cal_shadow_crit_over131_3350_12_160_110():
        global attack_hero
        global attack_buf_base
        global damage_min_crit_rate
        global crit_damage_base
        global damage_min_speed
        attack_hero = 3350
        attack_buf_base = 100
        damage_min_crit_rate = 100 - 12 - 30
        crit_damage_base = 160
        damage_min_speed = 131 - 110
        return cal_x_max_damage(type_shadow, soul_crit, 110, prop_value_l6_crit_damage, 0)
    def cal_shadow_skull_over117_3350_32_160_110():
        global attack_hero
        global attack_buf_base
        global damage_min_crit_rate
        global crit_damage_base
        global damage_min_speed
        attack_hero = 3350
        attack_buf_base = 100
        damage_min_crit_rate = 100 - 20 - 12 - 15
        crit_damage_base = 160
        damage_min_speed = 117 - 110
        return cal_x_max_damage(type_shadow, [type_skull], 110, prop_value_none, 0)
    def cal_shadow_skull_over117_3350_32_160_110():
        global attack_hero
        global attack_buf_base
        global damage_min_crit_rate
        global crit_damage_base
        global damage_min_speed
        attack_hero = 3350
        attack_buf_base = 100
        damage_min_crit_rate = 100 - 20 - 12 - 15
        crit_damage_base = 160
        damage_min_speed = 122 - 110
        return cal_x_max_damage(type_shadow, [type_skull], 110, prop_value_none, 0)
    def cal_shadow_skull_over0_3350_32_160_110():
        global attack_hero
        global attack_buf_base
        global damage_min_crit_rate
        global crit_damage_base
        global damage_min_speed
        attack_hero = 3350
        attack_buf_base = 100
        damage_min_crit_rate = 100 - 20 - 12 - 15
        crit_damage_base = 160
        damage_min_speed = 110 - 110
        return cal_x_max_damage(type_shadow, [type_skull], 110, prop_value_none, 0)
    def cal_shadow_over0_3350_32_160_110():
        global attack_hero
        global attack_buf_base
        global damage_min_crit_rate
        global crit_damage_base
        global damage_min_speed
        attack_hero = 3350
        attack_buf_base = 100
        damage_min_crit_rate = 101 - 32 - 30
        crit_damage_base = 160
        damage_min_speed = 110 - 110
        return cal_x_max_damage(type_shadow, soul_crit, 110, prop_value_l6_crit_damage, 0)
        #return cal_x_max_damage(type_shadow, [type_skull], 110, prop_value_l6_crit_damage, 0)
    def cal_kyoukotsu_crit_over117_3323_15_150_112():
        global attack_hero
        global attack_buf_base
        global damage_min_crit_rate
        global crit_damage_base
        global damage_min_speed
        attack_hero = 3323
        attack_buf_base = 100 + 15
        damage_min_crit_rate = 100 - 15 - 15
        crit_damage_base = 150
        damage_min_speed = 117 - 112
        return cal_x_max_damage(type_kyoukotsu, soul_crit, 112, prop_value_none, 0)
    def cal_shadow_skull_over117_3323_15_150_112():
        global attack_hero
        global attack_buf_base
        global damage_min_crit_rate
        global crit_damage_base
        global damage_min_speed
        attack_hero = 3323
        attack_buf_base = 100
        damage_min_crit_rate = 100 - 15 - 15
        crit_damage_base = 150
        damage_min_speed = 117 - 112
        return cal_x_max_damage(type_shadow, [type_skull], 112, prop_value_none, 0)
    def cal_shadow_skull_over121_3323_35_150_112():
        global attack_hero
        global attack_buf_base
        global damage_min_crit_rate
        global crit_damage_base
        global damage_min_speed
        attack_hero = 3323
        attack_buf_base = 100
        damage_min_crit_rate = 100 - 20 - 15 - 15
        crit_damage_base = 150
        damage_min_speed = 121 - 112
        return cal_x_max_damage(type_shadow, [type_skull], 112, prop_value_none, 0)
    def cal_shadow_crit_over0_3323_35_150_112():
        global attack_hero
        global attack_buf_base
        global damage_min_crit_rate
        global crit_damage_base
        global damage_min_speed
        attack_hero = 3323
        attack_buf_base = 100
        damage_min_crit_rate = 100 - 35 - 30
        crit_damage_base = 150
        damage_min_speed = 112 - 112
        return cal_x_max_damage(type_shadow, soul_crit, 112, prop_value_none, 0)
    def cal_shadow_crit_over117_3323_35_150_112():
        global attack_hero
        global attack_buf_base
        global damage_min_crit_rate
        global crit_damage_base
        global damage_min_speed
        attack_hero = 3323
        attack_buf_base = 100
        damage_min_crit_rate = 100 - 20 - 15 - 30
        crit_damage_base = 150
        damage_min_speed = 117 - 112
        return cal_x_max_damage(type_shadow, soul_crit, 112, prop_value_none, 0)
    def cal_watcher_crit_over117_3323_15_150_112():
        global attack_hero
        global attack_buf_base
        global damage_min_crit_rate
        global crit_damage_base
        global damage_min_speed
        attack_hero = 3323
        attack_buf_base = 100 + 15
        damage_min_crit_rate = 100 - 15 - 15
        crit_damage_base = 150
        damage_min_speed = 117 - 112
        return cal_x_max_damage(type_watcher, soul_crit, 112, prop_value_none, 0)
    def cal_watcher_skull_over117_3323_15_150_112():
        global attack_hero
        global attack_buf_base
        global damage_min_crit_rate
        global crit_damage_base
        global damage_min_speed
        attack_hero = 3323
        attack_buf_base = 100 + 15
        damage_min_crit_rate = 100 - 15 - 0
        crit_damage_base = 150
        damage_min_speed = 117 - 112
        return cal_x_max_damage(type_watcher, [type_skull], 112, prop_value_none, 0)
    def cal_watcher_crit_over117_3323_35_150_112():
        global attack_hero
        global attack_buf_base
        global damage_min_crit_rate
        global crit_damage_base
        global damage_min_speed
        attack_hero = 3323
        attack_buf_base = 100 + 15
        damage_min_crit_rate = 100 - 20 - 15
        crit_damage_base = 150
        damage_min_speed = 117 - 112
        return cal_x_max_damage(type_watcher, [type_skull], 112, prop_value_none, 0)
    def cal_watcher_crit_over0_3350_12_160_110():
        global attack_hero
        global attack_buf_base
        global damage_min_crit_rate
        global crit_damage_base
        global damage_min_speed
        attack_hero = 3350
        attack_buf_base = 100 + 15
        damage_min_crit_rate = 100 - 15 - 15
        crit_damage_base = 160
        damage_min_speed = 110 - 110
        return cal_x_max_damage(type_watcher, soul_crit, 110, prop_value_none, 0)
    def cal_watcher_skull_over0_3350_12_160_110():
        global attack_hero
        global attack_buf_base
        global damage_min_crit_rate
        global crit_damage_base
        global damage_min_speed
        attack_hero = 3350
        attack_buf_base = 100 + 15
        damage_min_crit_rate = 100 - 15 - 0
        crit_damage_base = 160
        damage_min_speed = 110 - 110
        return cal_x_max_damage(type_watcher, [type_skull], 110, prop_value_none, 0)
    def cal_watcher_crit_over0_3323_35_150_112():
        global attack_hero
        global attack_buf_base
        global damage_min_crit_rate
        global crit_damage_base
        global damage_min_speed
        attack_hero = 3323
        attack_buf_base = 100 + 15
        damage_min_crit_rate = 100 - 35 - 15
        crit_damage_base = 150
        damage_min_speed = 112 - 112
        return cal_x_max_damage(type_watcher, soul_crit, 112, prop_value_none, 0)
    def cal_watcher_skull_over117_3323_35_150_112():
        global attack_hero
        global attack_buf_base
        global damage_min_crit_rate
        global crit_damage_base
        global damage_min_speed
        attack_hero = 3323
        attack_buf_base = 100 + 15
        damage_min_crit_rate = 100 - 35 - 0
        crit_damage_base = 150
        damage_min_speed = 112 - 112
        return cal_x_max_damage(type_watcher, [type_skull], 112, prop_value_none, 0)
    def cal_shadow_over0_3002_8_150_107():
        global attack_hero
        global attack_buf_base
        global damage_min_crit_rate
        global crit_damage_base
        global damage_min_speed
        attack_hero = 3002
        attack_buf_base = 100
        damage_min_crit_rate = 101 - 8 - 30
        crit_damage_base = 150
        damage_min_speed = 107 - 107
        return cal_x_max_damage(type_shadow, soul_crit, 107, prop_value_l6_crit_damage, 0)
    def cal_shadow_overstar_3350_12_160_110():
        global attack_hero
        global attack_buf_base
        global damage_min_crit_rate
        global crit_damage_base
        global damage_min_speed
        attack_hero = 3350
        attack_buf_base = 100
        damage_min_crit_rate = 100 - 12 - 30
        crit_damage_base = 160
        damage_min_speed = 128 - 110
        return cal_x_max_damage(type_shadow, soul_crit, 110, prop_value_l6_crit_damage, 0)
    def cal_shadow_crit_over120_3216_10_150_112():
        global attack_hero
        global attack_buf_base
        global damage_min_crit_rate
        global crit_damage_base
        global damage_min_speed
        attack_hero = 3216
        attack_buf_base = 100
        damage_min_crit_rate = 100 - 10 - 30
        crit_damage_base = 150
        damage_min_speed = 120 - 112
        return cal_x_max_damage(type_shadow, soul_crit, 112, prop_value_none, 0)
    def cal_shadow_semisen_over119_2385_25_150_118():
        global attack_hero
        global attack_buf_base
        global damage_min_crit_rate
        global crit_damage_base
        global damage_min_speed
        #global damage_max_speed
        attack_hero = 2385
        attack_buf_base = 100
        damage_min_crit_rate = 100 - 20 - 5 - 30
        crit_damage_base = 150
        damage_min_speed = 119 - 118
        #damage_max_speed = 119 - 118
        r = cal_x_max_damage(type_shadow, [type_semisen], 118, prop_value_none, 0)
        #damage_max_speed = 500
        return r
    def cal_shadow_crit_over122_3216_10_150_112():
        global attack_hero
        global attack_buf_base
        global damage_min_crit_rate
        global crit_damage_base
        global damage_min_speed
        attack_hero = 3216
        attack_buf_base = 100
        damage_min_crit_rate = 100 - 10 - 30
        crit_damage_base = 150
        damage_min_speed = 122 - 112
        return cal_x_max_damage(type_shadow, soul_crit, 112, prop_value_none, 0)
    def cal_shadow_skull_over122_3216_10_150_112():
        global attack_hero
        global attack_buf_base
        global damage_min_crit_rate
        global crit_damage_base
        global damage_min_speed
        attack_hero = 3216
        attack_buf_base = 100
        damage_min_crit_rate = 100 - 10 - 15
        crit_damage_base = 150
        damage_min_speed = 122 - 112
        return cal_x_max_damage(type_shadow, [type_skull], 112, prop_value_none, 0)
    def cal_shadow_skull_over130_3216_30_150_112():
        global attack_hero
        global attack_buf_base
        global damage_min_crit_rate
        global crit_damage_base
        global damage_min_speed
        attack_hero = 3216
        attack_buf_base = 100
        damage_min_crit_rate = 100 - 20 - 10 - 15
        crit_damage_base = 150
        damage_min_speed = 130 - 112
        return cal_x_max_damage(type_shadow, [type_skull], 112, prop_value_none, 0)
    def cal_shadow_crit_over128_4074_10_150_118():
        global attack_hero
        global attack_buf_base
        global damage_min_crit_rate
        global crit_damage_base
        global damage_min_speed
        attack_hero = 4074
        attack_buf_base = 100
        damage_min_crit_rate = 100 - 10 - 30
        crit_damage_base = 150
        damage_min_speed = 129 - 118
        return cal_x_max_damage(type_shadow, soul_crit, 118, prop_value_l6_crit_damage, 0)
    def cal_shadow_attack_over128_3216_10_150_112():
        global attack_hero
        global attack_buf_base
        global damage_min_crit_rate
        global crit_damage_base
        global damage_min_speed
        attack_hero = 3216
        attack_buf_base = 100 + 15
        damage_min_crit_rate = 100 - 10 - 15
        crit_damage_base = 150
        damage_min_speed = 129 - 112
        return cal_x_max_damage(type_shadow, soul_attack, 112, prop_value_none, 0)
    def cal_shadow_crit_over158_1741_8_150_118():
        global attack_hero
        global attack_buf_base
        global damage_min_crit_rate
        global crit_damage_base
        global damage_min_speed
        attack_hero = 1741
        attack_buf_base = 100
        damage_min_crit_rate = 100 - 8 - 15
        crit_damage_base = 150
        damage_min_speed = 158 - 118
        return cal_x_max_damage(type_shadow, [type_spider], 118, prop_value_none, 0)
    def cal_shadow_over158_2894_8_150_118():
        global attack_hero
        global attack_buf_base
        global damage_min_crit_rate
        global crit_damage_base
        global damage_min_speed
        attack_hero = 2894
        attack_buf_base = 100
        damage_min_crit_rate = 100 - 20 - 8 - 30
        crit_damage_base = 150
        damage_min_speed = 158 - 118
        return cal_x_max_damage(type_shadow, soul_crit, 118, prop_value_none, 157)
    def cal_fire_over158_2894_8_150_118():
        global attack_hero
        global attack_buf_base
        global damage_min_crit_rate
        global crit_damage_base
        global damage_min_speed
        attack_hero = 2894
        attack_buf_base = 100
        damage_min_crit_rate = 100 - 8 - 15
        crit_damage_base = 150
        damage_min_speed = 158 - 118
        return cal_x_max_damage(type_fire, soul_crit, 118, prop_value_none, 0)
    def cal_shadow_over163_2894_28_150_118():
        global attack_hero
        global attack_buf_base
        global damage_min_crit_rate
        global crit_damage_base
        global damage_min_speed
        attack_hero = 2894
        attack_buf_base = 100
        damage_min_crit_rate = 100 - 8 - 30
        crit_damage_base = 150
        damage_min_speed = 163 - 118
        return cal_x_max_damage(type_shadow, soul_crit, 118, prop_value_none, 0)
        #return cal_x_max_damage(type_shadow, [type_none], 118, prop_value_none, 27900)

    def cal_x_free_max_damage(soul_x_type, base_speed):
        global attack_buf_base
        attack_buf_base = 100
        if soul_x_type == type_scarlet:
            attack_buf_base = attack_buf_base + 15
        damage = 0
        res = []
        com = {}
        def _build_mask():
            return build_mask_x_free(soul_x_type)
        def _filter_type(mitama):
            if mitama.keys()[0] in done:
                return False
            enhance_type = mitama.values()[0][u'御魂类型']
            return enhance_type == soul_x_type or enhance_type in soul_free
        r, c, n = filter_soul(_filter_type,
                              prop_value_none,
                              prop_value_none,
                              prop_value_none,
                              _build_mask,
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
            print('%s(free):%d,+%d' % (__[soul_x_type], int(damage / 100), base_speed + comb_data['sum'][speed]))
            return comb_data
        return None
    def cal_scarlet_free_max_damage():
        global attack_hero
        global damage_min_crit_rate
        global crit_damage_base
        global damage_min_speed
        attack_hero = 3350
        damage_min_crit_rate = 100 - 11 - 0
        crit_damage_base = 160
        damage_min_speed = 0
        return cal_x_free_max_damage(type_scarlet, 0)
    def cal_seductress_free_over140_3350_12_160_117():
        global attack_hero
        global damage_min_crit_rate
        global crit_damage_base
        global damage_min_speed
        attack_hero = 3350
        damage_min_crit_rate = 100 - 11 - 15
        crit_damage_base = 160
        damage_min_speed = 141 - 117
        return cal_x_free_max_damage(type_seductress, 117)
    def cal_shadow_free_3350_12_160_110():
        global attack_hero
        global damage_min_crit_rate
        global crit_damage_base
        global damage_min_speed
        attack_hero = 3350
        damage_min_crit_rate = 100 - 12 - 15
        crit_damage_base = 160
        damage_min_speed = 129 - 110
        return cal_x_free_max_damage(type_shadow, 110)
    def cal_shadow_free_over128_3216_10_150_112():
        global attack_hero
        global damage_min_crit_rate
        global crit_damage_base
        global damage_min_speed
        attack_hero = 3216
        damage_min_crit_rate = 100 - 10 - 15
        crit_damage_base = 150
        damage_min_speed = 129 - 112
        return cal_x_free_max_damage(type_shadow, 112)
    def cal_clear():
        done.clear()
        print '--'
        return None

    dou1 = [
            cal_freetype_max_speed,
            #
            #cal_fortune_max_speed,
            cal_sprite_over140_2332_5_150_108,
            #cal_seductress_crit_over129_3350_11_160_117,
            cal_seductress_crit_over140_3350_11_160_117, #cal_seductress_free_over140_3350_12_160_117,
            cal_jizo_over140_4074_10_150_118,
            #
            cal_shadow_crit_over120_3216_10_150_112,
            cal_shadow_over0_3350_12_160_110,
            #cal_shadow_xstar_max_damage,
        ]
    test = [
            cal_seductress_crit_over129_3350_11_160_117,
            cal_seductress_crit_over140_3350_11_160_117, #cal_seductress_free_over140_3350_12_160_117,
            #
            cal_shadow_over0_3350_12_160_110,
        ]
    mine = [
            ##cal_shadow_free_over128_3216_10_150_112,
            cal_seductress_crit_over140_3350_11_160_117, #cal_seductress_attack_over140_3350_11_160_117,
            cal_shadow_crit_over120_3216_10_150_112, #cal_shadow_attack_over128_3216_10_150_112,
            cal_shadow_over0_3350_12_160_110,
            cal_shadow_over0_3002_8_150_107,
        ]
    supp = [
            cal_shadow_over158_2894_8_150_118,
        ]
    min2 = [
            #cal_seductress_crit_over129_3350_11_160_117,
            cal_shadow_over0_3350_32_160_110,
        ]
    sup2 = [
            cal_shadow_over163_2894_28_150_118,
        ]
    brief = [
            cal_fortune_max_speed,
            #
            cal_clear,
            cal_freetype_max_speed,
            cal_seductress_crit_over129_3350_11_160_117,
            #
            cal_clear,
            cal_shadow_indirect_over131_4074_10_150_118,
            #
            cal_clear,
            #cal_shadow_skull_over117_3350_32_160_110,
            cal_shadow_skull_over121_3323_35_150_112,
            #cal_clear,
            #cal_watcher_crit_over0_3323_35_150_112,
            #cal_shadow_skull_over121_3323_35_150_112,
            #cal_clear,
            #cal_shadow_crit_over0_3323_35_150_112,
        ]
    dou2 = [
        cal_freetype_max_speed,
        cal_fortune_max_speed,
        cal_fire_max_speed,
        cal_sprite_over140_2332_5_150_108,
        cal_seductress_crit_over129_3350_11_160_117,
        cal_shadow_indirect_over131_4074_10_150_118,
        #
        cal_shadow_over0_3350_12_160_110,
        cal_seductress_over0_3323_10_150_104,
    ]
    mine11 = [
        #03_33s light+star+lin+lin
        #cal_clear, #cal_shadow_skull_over121_3323_35_150_112, #lin #cal_shadow_over158_2894_8_150_118, #shi
        #cal_watcher_skull_over117_3323_35_150_112, #lin2

        #04_31s star+220lin+205lin
        cal_clear,
        #cal_shadow_skull_over117_3323_15_150_112, #lin #cal_clear, #cal_shadow_over158_2894_8_150_118, #shi
        #cal_watcher_crit_over117_3323_15_150_112, #lin2
        cal_watcher_skull_over117_3323_15_150_112,

        #06_32s light+lin
        cal_clear,
        cal_shadow_skull_over121_3323_35_150_112,

        #09_35s jiu
        cal_clear,
        cal_shadow_skull_over0_3350_32_160_110, #jiu
        cal_clear,
        cal_shadow_skull_over122_3216_10_150_112,

        #10_33s shi+ci+chou+qin+jiu
        #cal_clear, #cal_shadow_skull_over117_3350_32_160_110,
        #cal_shadow_skull_over122_3216_10_150_112, #cal_watcher_crit_over0_3350_12_160_110,
        #cal_clear,
        #cal_watcher_skull_over0_3350_12_160_110, #jiu

        #cal_clear,
        #cal_shadow_crit_over122_3216_10_150_112,
        #cal_clear,
        #cal_watcher_crit_over0_3350_12_160_110, #jiu
        #cal_fire_over158_2894_8_150_118, #shi
    ]
    fast = [
        cal_fortune_max_speed,
        cal_clear,
        cal_freetype_max_speed,
            #cal_shadow_indirect_over131_4074_10_150_118,
        cal_seductress_crit_over129_3350_11_160_117,
        cal_clear,
        cal_shadow_skull_over121_3323_35_150_112,
        cal_clear,
        cal_shadow_skull_over0_3350_32_160_110,
            #cal_seductress_crit_over140_3350_11_160_117, #cal_seductress_free_over140_3350_12_160_117,
    ]
    dou4 = [
        cal_fortune_max_speed,
    ]
    man = [
        cal_shadow_skull_over117_3350_32_160_110,   #jiu        SO
        cal_shadow_skull_over0_3350_32_160_110,     #jiu        SO
        cal_shadow_crit_over158_1741_8_150_118,     #shi        SO
    ]
    mine11A = [
        cal_clear,
        cal_shadow_skull_over122_3216_10_150_112,   #ci         SO3
        cal_shadow_over158_2894_8_150_118,          #shi        SO2
    ]
    mine11B = [
        cal_clear,
        cal_shadow_skull_over0_3350_32_160_110,     #jiu        SO5
    ]
    mine11a6 = [
        cal_clear,
        cal_shadow_over158_2894_8_150_118,          #shi        SO2
        cal_shadow_semisen_over119_2385_25_150_118, #qin        SO3
        cal_seductress_crit_over129_3350_11_160_117,
    ]
    mine11b6 = [
        cal_clear,
        cal_shadow_skull_over121_3323_35_150_112,   #lin        SO3
    ]
    dou3 = [
        cal_freetype_max_speed,                      #mian  DO1
        cal_fortune_max_speed,                       #lian  DO1
        cal_shadow_semisen_over119_2385_25_150_118,  #qin       SO5
        cal_seductress_crit_over129_3350_11_160_117, #qie   DO
        cal_shadow_over158_2894_8_150_118,           #shi       SO1
        cal_seductress_crit_over140_3350_11_160_117, #qie   DO
        cal_shadow_indirect_over131_4074_10_150_118, #she   DO
        cal_shadow_over0_3350_12_160_110,            #jiu           TU3
        cal_seductress_attack_over0_3377_9_150_109,  #hei               SE
        cal_shadow_over0_3350_11_160_117,            #qie               SE
        cal_seductress_over0_3323_10_150_104,        #huang DO5
    ]
    dou4 = [
        cal_fortune_max_speed,                       #lian  DO1
        cal_fortune_effect_over200_119,              #zhu   DO2
    ]
    test = [
        cal_fortune_max_speed,
    ]
    she = [
        cal_fortune_max_speed,
        cal_fortune_max_speed,
        cal_freetype_max_speed,
        cal_fortune_max_speed,
    ]
    order = brief
    order = dou2
    order = fast
    order = supp
    order = man
    order = mine11A
    order = mine11B
    order = mine11b6
    order = mine11a6
    order = dou3
    order = test
    order = she
    order = dou4
    for f in order:
        comb = f()
        if comb is not None:
            yield comb
        if 0:
            done.clear()
    return

