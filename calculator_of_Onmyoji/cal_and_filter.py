# coding: utf-8

import itertools
import os
import sys
import multiprocessing
import uuid
import copy
#from multiprocessing import Pool

from calculator_of_Onmyoji import data_format

attack      = data_format.MITAMA_PROPS[0]
attack_buf  = data_format.MITAMA_PROPS[1]
def_buf     = data_format.MITAMA_PROPS[3]
crit_rate   = data_format.MITAMA_PROPS[4]
crit_damage = data_format.MITAMA_PROPS[5]
hp          = data_format.MITAMA_PROPS[6]
hp_buf      = data_format.MITAMA_PROPS[7]
effect      = data_format.MITAMA_PROPS[8]
resist      = data_format.MITAMA_PROPS[9]
speed       = data_format.MITAMA_PROPS[10]
soul_sn     = data_format.MITAMA_COL_NAME_ZH[0]
suit        = data_format.MITAMA_COL_NAME_ZH[1]
pos         = data_format.MITAMA_COL_NAME_ZH[2]

speed_1p_overflow = 20
speed_1p_limit = 1
fast_min_speed = int(277 - (127 + 57 + 16.5 * 5))

selected = set()

effect_min_speed = 0
effect_max_speed = 200
damage_min_speed = 11
damage_max_speed = 500
damage_limit = 0
damage_indirect = 0
damage_min_crit_rate = 90
attack_buf_base_only = 100
hp_buf_base_only = 100
attack_buf_base_or_hp_buf_base = 100
crit_damage_base = 160
hero_attack_only = 3350
hero_hp_only = 3350
hero_attack_or_hero_hp = 3350
effect_base = 0
# |-effect(11)-|-attackbuf(14)-|-critrate(13)-|-critdamage(11)-|-speed(12)-|
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
# |-resist(11)-|-hpbuf(14)-----|-critrate(13)-|-critdamage(11)-|-speed(12)-|
encode_hp_resist = False
hp_buf_base = 0
resist_base = 0
bits_hpbuf = bits_attackbuf
bits_resist = bits_effect
offset_hpbuf = offset_attackbuf
offset_resist = offset_effect

def __decode(v, offset, bits):
    return (v >> offset) & ((1 << bits) - 1)

def score_suit_buf_max_speed(soul_2p_mask, buf_max, n, t):
    if __decode(n, offset_speed, bits_speed) <= buf_max:
        return buf_max, n, True
    return __decode(n, offset_speed, bits_speed), n, False
def score_buf_max_effect(soul_2p_mask, buf_max, n, t):
    #test speed
    s = __decode(n, offset_speed, bits_speed)
    if s < effect_min_speed * 100 or s > effect_max_speed * 100:
        return buf_max, 1, True
    #test buf with suit enhance
    if soul_2p_mask and (t & soul_2p_mask) == 0:
        return buf_max, 2, True
    #test crit rate
    if __decode(n, offset_critrate, bits_critrate) < damage_min_crit_rate * 10:
        return buf_max, 3, True
    #test effect with suit enhance
    e = __decode(n, offset_effect, bits_effect)
    if buf_max >= e:
        return buf_max, 4, True
    return e, n, False
def score_buf_max_resist(soul_2p_mask, buf_max, n, t):
    return score_buf_max_effect(soul_2p_mask, buf_max, n, t)
def score_freetype_max_effect(soul_2p_mask, buf_max, n, t):
    #test speed
    s = __decode(n, offset_speed, bits_speed)
    if s < effect_min_speed * 100 or s > effect_max_speed * 100:
        return buf_max, 1, True
    #test effect with suit enhance
    e = __decode(n, offset_effect, bits_effect)
    #test buf with suit enhance
    if t & (6 << (3 * 0)):
        e = e + 150
    if t & (6 << (3 * 1)):
        e = e + 150
    if buf_max >= e:
        return buf_max, 3, True
    return e, n, False

def score_max_damage(soul_2p_mask, buf_max, n, t):
    #test speed
    s = __decode(n, offset_speed, bits_speed)
    if s < int(damage_min_speed * 100) or s > int(damage_max_speed * 100):
        return buf_max, 1, True
    ##test crit rate with suit enhance
    if soul_2p_mask and (t & soul_2p_mask) == 0:
        return buf_max, 2, True
    #test crit rate
    if __decode(n, offset_critrate, bits_critrate) < damage_min_crit_rate * 10:
        return buf_max, 3, True
    ab = attack_buf_base_or_hp_buf_base * 10 + __decode(n, offset_attackbuf, bits_attackbuf)
    cd = crit_damage_base * 10 + __decode(n, offset_critdamage, bits_critdamage)
    d = ab * cd
    #print attack_buf_base_or_hp_buf_base + ab, crit_damage_base + cd, d
    #if (ab == 129) and (cd == 360): print 'score:', d, attack_buf_base_or_hp_buf_base, crit_damage_base
    if buf_max >= d:
        return buf_max, 4, True
    if 0 < damage_limit and damage_limit < int(hero_attack_or_hero_hp * d / 1000000 / 100):
        return buf_max, 5, True
    #print damage_limit, d
    return d + 1, n, False
def score_buf_max_hp_shield(soul_2p_mask, buf_max, n, t):
    return score_max_damage(soul_2p_mask, buf_max, n, t)

def score_max_crit_damage_only(soul_2p_mask, buf_max, n, t):
    #test speed
    s = __decode(n, offset_speed, bits_speed)
    if s < int(damage_min_speed * 100) or s > int(damage_max_speed * 100):
        return buf_max, 1, True
    ##test crit rate with suit enhance
    if soul_2p_mask and (t & soul_2p_mask) == 0:
        return buf_max, 2, True
    #test crit rate
    if __decode(n, offset_critrate, bits_critrate) < damage_min_crit_rate * 10:
        return buf_max, 3, True
    ab = 100 * 10
    cd = crit_damage_base * 10 + __decode(n, offset_critdamage, bits_critdamage)
    d = ab * cd
    if buf_max >= d:
        return buf_max, 4, True
    if 0 < damage_limit and damage_limit < int(hero_attack_or_hero_hp * d / 1000000 / 100):
        return buf_max, 5, True
    return d + 1, n, False

def score_buf_max_attack_only(soul_2p_mask, buf_max, n, t):
    #test speed
    s = __decode(n, offset_speed, bits_speed)
    if s < int(damage_min_speed * 100) or s > int(damage_max_speed * 100):
        return buf_max, 1, True
    ##test crit rate with suit enhance
    if soul_2p_mask and (t & soul_2p_mask) == 0:
        return buf_max, 2, True
    #test crit rate
    if __decode(n, offset_critrate, bits_critrate) < damage_min_crit_rate * 10:
        return buf_max, 3, True
    ab = attack_buf_base_or_hp_buf_base * 10 + __decode(n, offset_attackbuf, bits_attackbuf)
    cd = 100 * 10
    d = ab * cd
    if buf_max >= d:
        return buf_max, 4, True
    if 0 < damage_limit and damage_limit < int(hero_attack_or_hero_hp * d / 1000000 / 100):
        return buf_max, 5, True
    return d + 1, n, False
def score_buf_max_hp_only(soul_2p_mask, buf_max, n, t):
    return score_buf_max_attack_only(soul_2p_mask, buf_max, n, t)

def score_suit_buf_none(soul_2p_mask, buf_max, n, t):
    return n, n, False

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
    #print('search:%d' % (len(d1) * len(d2) * len(d3) * len(d4) * len(d5) * len(d6)))
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
    #print('result: %s' % result)
    #print(('%s %s' % (d, comb_sum)).decode('raw_unicode_escape'))
    return result, comb_sum, suit_buf_max, comb_code

result_num = 0
def make_result(data_dict, res, com):
    global result_num
    result_num = result_num + 1
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
        #if k == '5b47041108942d6ee02ea362': print 'map2list', v[attack], (int(v[attack_buf]) + int(v[attack]*100/hero_attack_or_hero_hp))
        if encode_hp_resist:
            val <<= bits_resist
            val += int(v[resist] * 10)
            val <<= bits_hpbuf
            val += (int(v[hp_buf] * 10) + int(v[hp]*100/hero_attack_or_hero_hp * 10))
        else:
            val <<= bits_effect
            val += int(v[effect] * 10)
            val <<= bits_attackbuf
            val += (int(v[attack_buf] * 10) + int(v[attack]*100/hero_attack_or_hero_hp * 10))
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
    return {soul_sn:     nz,
            attack_buf:  __decode(nx, offset_attackbuf, bits_attackbuf),
            crit_rate:   __decode(nx, offset_critrate, bits_critrate),
            crit_damage: __decode(nx, offset_critdamage, bits_critdamage),
            effect:      __decode(nx, offset_effect, bits_effect),
            resist:      __decode(nx, offset_resist, bits_resist),
            speed:       __decode(nx, offset_speed, bits_speed),
            suit:        mitama_type}

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
    none = set()
    def append_data_dict(type_x, fake_speed):
        for i in xrange(6):
            v = data_dict[i+1][0].values()[0]
            kf = ('%s' % uuid.uuid1()).decode('utf-8')
            none.add(kf)
            vf = {}
            for k in v.keys():
                vf[k] = 0
            vf[suit] = type_x
            vf[pos] = i + 1
            if i == 0:
                vf[data_format.MITAMA_COL_NAME_ZH[3]] = 486
            vf[data_format.MITAMA_COL_NAME_ZH[13]] = fake_speed
            if i in [1]:
                vf[data_format.MITAMA_COL_NAME_ZH[13]] = 0 # too hard for p2
            data_dict[i + 1].append({kf : vf})
    type_none = 0
    append_data_dict(type_none, 0)

    type_pearl = data_format.MITAMA_TYPES[0]
    type_dice = data_format.MITAMA_TYPES[1]
    type_sprite = data_format.MITAMA_TYPES[2]
    type_seductress = data_format.MITAMA_TYPES[4]
    type_senecio = data_format.MITAMA_TYPES[5]
    type_spider = data_format.MITAMA_TYPES[6]
    type_skull = data_format.MITAMA_TYPES[8]
    type_catfish = data_format.MITAMA_TYPES[9]
    type_shinkirou = data_format.MITAMA_TYPES[10]
    type_snow = data_format.MITAMA_TYPES[11]
    type_jizo = data_format.MITAMA_TYPES[12]
    type_nightwing = data_format.MITAMA_TYPES[13]
    type_semisen = data_format.MITAMA_TYPES[15]
    type_mimic = data_format.MITAMA_TYPES[16]
    type_fortune = data_format.MITAMA_TYPES[18]
    type_taker = data_format.MITAMA_TYPES[20]
    type_dawnfairy = data_format.MITAMA_TYPES[21]
    type_priestess = data_format.MITAMA_TYPES[23]
    type_scarlet = data_format.MITAMA_TYPES[24]
    type_fire = data_format.MITAMA_TYPES[25]
    type_house = data_format.MITAMA_TYPES[26]
    type_edge = data_format.MITAMA_TYPES[27]
    type_watcher = data_format.MITAMA_TYPES[28]
    type_nymph = data_format.MITAMA_TYPES[29]
    type_spirit = data_format.MITAMA_TYPES[30]
    type_claws = data_format.MITAMA_TYPES[31]
    type_phenix = data_format.MITAMA_TYPES[33]
    type_shadow = data_format.MITAMA_TYPES[34]
    type_tomb = data_format.MITAMA_TYPES[35]
    type_kyoukotsu = data_format.MITAMA_TYPES[36]
    type_kasodani = data_format.MITAMA_TYPES[37]
    type_geisha = data_format.MITAMA_TYPES[38]
    __ = {
        speed: 'speed',

        type_none: 'none',
        type_pearl: 'pearl',
        type_dice: 'dice',
        type_sprite: 'sprite',
        type_seductress: 'seductress',
        type_senecio: 'senecio',
        type_spider: 'spider',
        type_skull: 'skull',
        type_catfish: 'catfish',
        type_shinkirou: 'shinkirou',
        type_snow: 'snow',
        type_jizo: 'jizo',
        type_nightwing: 'nightwing',
        type_semisen: 'semisen',
        type_mimic: 'mimic',
        type_fortune: 'fortune',
        type_taker: 'taker',
        type_dawnfairy: 'dawnfairy',
        type_priestess: 'priestess',
        type_scarlet: 'scarlet',
        type_fire: 'fire',
        type_house: 'house',
        type_edge: 'edge',
        type_watcher: 'watcher',
        type_nymph: 'nymph',
        type_spirit: 'spirit',
        type_claws: 'claws',
        type_phenix: 'phenix',
        type_shadow: 'shadow',
        type_tomb: 'tomb',
        type_kyoukotsu: 'kyoukotsu',
        type_kasodani: 'kasodani',
        type_geisha: 'geisha',
    }
    append_data_dict(type_fortune, speed_1p_overflow)

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
    soul_resist = []
    for (k, v) in data_format.MITAMA_ENHANCE.items():
        enhance_type = v[u"加成类型"]
        if enhance_type == resist:
            soul_resist.append(k)
            continue
    soul_hp = []
    for (k, v) in data_format.MITAMA_ENHANCE.items():
        enhance_type = v[u"加成类型"]
        if enhance_type == hp_buf:
            soul_hp.append(k)
            continue
    soul_def = []
    for (k, v) in data_format.MITAMA_ENHANCE.items():
        enhance_type = v[u"加成类型"]
        if enhance_type == def_buf:
            soul_def.append(k)
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
        enhance_type = mitama.values()[0][suit]
        enhance_speed = mitama.values()[0][speed]
        if enhance_type == type_fortune and enhance_speed == speed_1p_overflow:
            return False
        return enhance_speed >= speed_1p_limit
    def prop_value_fast_speed(mitama):
        if mitama.keys()[0] in done:
            return False
        enhance_type = mitama.values()[0][suit]
        enhance_speed = mitama.values()[0][speed]
        if enhance_type == type_fortune and enhance_speed == speed_1p_overflow:
            return False
        if enhance_speed >= fast_min_speed:
            return True
        return False
    def prop_value_effect(mitama):
        if mitama.keys()[0] in done:
            return False
        mitama_info = mitama.values()[0]
        if (mitama_info[effect] and mitama_info[effect] > 0):
            return True
        return False
    def prop_value_resist(mitama):
        if mitama.keys()[0] in done:
            return False
        mitama_info = mitama.values()[0]
        if (mitama_info[resist] and mitama_info[resist] > 0):
            return True
        return False
    def prop_value_damage(mitama):
        if mitama.keys()[0] in done:
            return False
        mitama_info = mitama.values()[0]
        return False
    def prop_l2_speed(mitama):
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
    def prop_value_hp(mitama):
        if mitama.keys()[0] in done:
            return False
        mitama_info = mitama.values()[0]
        if (mitama_info[hp_buf] and mitama_info[hp_buf] >= 55):
            return True
        return False
    def prop_attack(mitama):
        if mitama.keys()[0] in done:
            return False
        mitama_info = mitama.values()[0]
        if (mitama_info[attack_buf] and mitama_info[attack_buf] >= 55):
            return True
        return False
    def prop_crit_damage(mitama):
        if mitama.keys()[0] in done:
            return False
        mitama_info = mitama.values()[0]
        if (mitama_info[crit_damage] and mitama_info[crit_damage] >= 89):
            return True
        return False
    def prop_crit_rate(mitama):
        if mitama.keys()[0] in done:
            return False
        mitama_info = mitama.values()[0]
        if (mitama_info[crit_rate] and mitama_info[crit_rate] >= 55):
            return True
        return False
    def prop_value_l6_none(mitama):
        if mitama.keys()[0] in done:
            return False
        mitama_info = mitama.values()[0]
        return mitama_info[suit] == 0
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
    def cal_fortune_or_none():
        def __filter_type(mitama):
            if mitama.keys()[0] in done:
                return False
            enhance_type = mitama.values()[0][suit]
            enhance_speed = mitama.values()[0][speed]
            if enhance_type == type_none:
                return True
            if enhance_type == type_fortune:
                if enhance_speed == speed_1p_overflow:
                    return False
                return enhance_speed > 10
            return False
        res, com, n, _ = filter_soul(__filter_type,
                          prop_value_none,
                          prop_value_none,
                          prop_value_none,
                          build_mask_none,
                          speed,
                          True,
                          score_suit_buf_max_speed,
                          data_dict)
        if len(res) > 0:
            for x in res:
                if x not in none:
                    done.add(x)
            comb_data = make_result(data_dict, res, com)
            comb_speed = [comb_data['info'][i].values()[0][speed] for i in xrange(6)]
            comb_type = ['#' if (type_fortune == comb_data['info'][i].values()[0][suit]) else '' for i in xrange(6)]
            comb_speed[1] = comb_speed[1] - 57
            print ('%02d[_____]fortune()maxspeed' % result_num), comb_data['sum'][speed] / 100.0, \
                    '(1)%0.2f%s' % (comb_speed[0], comb_type[0]), \
                    '57+(2)%0.2f%s' % (comb_speed[1], comb_type[1]), \
                    '(3)%0.2f%s' % (comb_speed[2], comb_type[2]), \
                    '(4)%0.2f%s' % (comb_speed[3], comb_type[3]), \
                    '(5)%0.2f%s' % (comb_speed[4], comb_type[4]), \
                    '(6)%0.2f%s' % (comb_speed[5], comb_type[5])
            #base_speed = 117
            #print('%02d[%s]%s()maxspeed:%.2f,+%.2f' % (result_num, '____', __[type_fortune], n / 100.0, base_speed + comb_data['sum'][speed] / 100.0))
            return comb_data
        return None
    freepos = []
    for f1p in range(6):
        for f2p in range(6):
            if f2p > f1p:
                freepos.append([f1p+1, f2p+1])
    if 0: print freepos

    def cal_x_max_speed(soul_x_type, base_speed, note):
        def _build_mask():
            soul = []
            soul_2p_mask = int(0)
            soul_4p_mask = int(0)
            for (k, v) in data_format.MITAMA_ENHANCE.items():
                if k == soul_x_type:
                    soul_4p_mask |= (4 << (3 * len(soul)))
                    soul.append(k)
                    break
            return soul, soul_2p_mask, soul_4p_mask

        speedbuf = 0
        res = []
        com = {}
        for fp in freepos:
            def __filter_type(mitama):
                if mitama.keys()[0] in done:
                    return False
                if not prop_value_speed(mitama):
                    return False
                location = mitama.values()[0][pos]
                if location in fp:
                    return True
                enhance_type = mitama.values()[0][suit]
                return enhance_type == soul_x_type
            r, c, n, _ = filter_soul(__filter_type,
                          prop_l2_speed,
                          prop_value_speed,
                          prop_value_speed,
                          _build_mask,
                          speed,
                          True,
                          score_suit_buf_max_speed,
                          data_dict)
            if n > speedbuf:
                res, com, speedbuf = r, c, n
        if len(res) > 0:
            for x in res:
                if x not in none:
                    done.add(x)
            comb_data = make_result(data_dict, res, com)
            comb_speed = [comb_data['info'][i].values()[0][speed] for i in xrange(6)]
            comb_type = ['#' if (type_fortune == comb_data['info'][i].values()[0][suit]) else '' for i in xrange(6)]
            ps = 0
            for i in xrange(6):
                ps += comb_speed[i]
            comb_speed[1] = comb_speed[1] - 57
            print ('%02d[%s]%s()maxspeed:%.2f/%.2f,+%.2f' % (result_num, note, __[soul_x_type], base_speed + ps, base_speed + comb_data['sum'][speed] / 100.0, ps)), \
                    '\n[1]     %0.2f %s' % (comb_speed[0], comb_type[0]), \
                    '\n[2] 57+ %0.2f %s' % (comb_speed[1], comb_type[1]), \
                    '\n[3]     %0.2f %s' % (comb_speed[2], comb_type[2]), \
                    '\n[4]     %0.2f %s' % (comb_speed[3], comb_type[3]), \
                    '\n[5]     %0.2f %s' % (comb_speed[4], comb_type[4]), \
                    '\n[6]     %0.2f %s' % (comb_speed[5], comb_type[5])
            #print('%02d[%s]%s()maxspeed:%.2f,+%.2f' % (result_num, note, __[soul_x_type], n / 100.0, base_speed + comb_data['sum'][speed] / 100.0))
            return comb_data
        return None
    def cal_fortune_max_speed():
        return cal_x_max_speed(type_fortune, 117, '_you1(270)')
    def cal_fire_max_speed():
        return cal_x_max_speed(type_fire)
    def cal_fortune_speed_107():
        return cal_x_max_speed(type_fortune, 107, '_you2')
    # free type max speed
    def cal_freetype_max_speed():
        global effect_min_speed
        global effect_max_speed
        res, com, n, _ = filter_soul(prop_value_speed,
                          prop_l2_speed,
                          prop_value_speed,
                          prop_value_speed,
                          build_mask_none,
                          speed,
                          True,
                          score_suit_buf_max_speed,
                          data_dict)
        if len(res) > 0:
            for x in res:
                if x not in none:
                    done.add(x)
            comb_data = make_result(data_dict, res, com)
            comb_speed = [comb_data['info'][i].values()[0][speed] for i in xrange(6)]
            comb_type = ['#' if (type_fortune == comb_data['info'][i].values()[0][suit]) else '' for i in xrange(6)]
            ps = 0
            for i in xrange(6):
                ps += comb_speed[i]
            comb_speed[1] = comb_speed[1] - 57
            print ('%02d[_mian(276)]freetype()maxspeed:%.2f/%.2f,+%.2f' % (result_num, 119 + ps, 119 + n / 100.0, ps)), \
                    '\n[1]     %0.2f %s' % (comb_speed[0], comb_type[0]), \
                    '\n[2] 57+ %0.2f %s' % (comb_speed[1], comb_type[1]), \
                    '\n[3]     %0.2f %s' % (comb_speed[2], comb_type[2]), \
                    '\n[4]     %0.2f %s' % (comb_speed[3], comb_type[3]), \
                    '\n[5]     %0.2f %s' % (comb_speed[4], comb_type[4]), \
                    '\n[6]     %0.2f %s' % (comb_speed[5], comb_type[5])
            #print('%04d[_mian]freetype()maxspeed:%.2f,+%.2f' % (result_num, n / 100.0, 119 + n / 100.0))
            return comb_data
        # quick terminate
        if n < 148 * 100:
            print('speed test fail')
            return None

    def cal_freetype_speed_effect(soul_peer, base_speed, note):
        score = 0
        res = []
        com = {}
        cc = 0
        desc = ''
        if 1:
            def __build_mask():
                soul = []
                soul_2p_mask = int(0)
                soul_4p_mask = int(0)
                for (k, v) in data_format.MITAMA_ENHANCE.items():
                    if k in soul_peer:
                        soul_2p_mask |= (6 << (3 * len(soul))) # for freetype only
                        soul.append(k)
                return soul, soul_2p_mask, soul_4p_mask

            r, c, n, _ = filter_soul(prop_value_fast_speed,
                              prop_l2_speed,
                              prop_value_l4_effect,
                              prop_value_none,
                              __build_mask,
                              effect,
                              False,
                              score_freetype_max_effect,
                              data_dict)
            if n > score:
                score, res, com = n, r, c
        if len(res) > 0:
            for x in res:
                if x not in none:
                    done.add(x)
            comb_data = make_result(data_dict, res, com)
            print('%02d[%s]freetype()maxeffect:%.1f,+%.2f' % (result_num, note, score / 10.0, base_speed + comb_data['sum'][speed] / 100.0))
            return comb_data
        return None
    def cal_freetype_effect_over276_127():
        global effect_min_speed
        global effect_max_speed
        effect_min_speed = 281 - 127
        effect_max_speed = 500
        r = cal_freetype_speed_effect(soul_effect, 127, '_yan ')
        return r

    def calxmaxdamage(soul_type, soul_peer, base_speed, prop_func, buf_limit, note, score_buf, sort_key, find_one):
        global effect_min_speed
        global effect_max_speed
        global damage_limit
        score = 0
        damage_limit = buf_limit
        res = []
        com = {}
        cc = 0
        desc = ''
        p = type_none
        prop_l2 = prop_value_none if len(prop_func) <= 2 else prop_func[2]
        prop_l4 = prop_value_none if len(prop_func) <= 1 else prop_func[1]
        prop_l6 = prop_func[0]
        for s in soul_peer:
            def __filter_type(mitama):
                if mitama.keys()[0] in done:
                    return False
                enhance_type = mitama.values()[0][suit]
                if enhance_type == type_fortune:
                    if mitama.values()[0][speed] == speed_1p_overflow:
                        return False
                return enhance_type == soul_type or enhance_type == s
            def __build_mask():
                soul = []
                soul_2p_mask = int(0)
                soul_4p_mask = int(0)
                for (k, v) in data_format.MITAMA_ENHANCE.items():
                    if k == soul_type:
                        soul_4p_mask |= (4 << (3 * len(soul)))
                    if k == s:
                        soul_2p_mask |= (2 << (3 * len(soul)))
                    if k == soul_type or k == s:
                        soul.append(k)
                if s == type_none:
                    soul_2p_mask |= (2 << (3 * len(soul)))
                    soul.append(type_none)
                return soul, soul_2p_mask, soul_4p_mask

            r, c, n, v = filter_soul(__filter_type,
                                  prop_l2,
                                  prop_l4,
                                  prop_l6,
                                  __build_mask,
                                  sort_key,
                                  find_one,
                                  score_buf,
                                  data_dict)
            if 0 and len(r) > 0: print '+type', s, int(hero_attack_or_hero_hp * n / 1000000 / 100), ('%s' % (make_result(data_dict, r, c)['sum'])).decode('raw_unicode_escape')
            if n > score:
                score, res, com, p, cc = n, r, c, s, v
        if len(res) == 0:
            print('  [%s]' % note)
        else:
            for x in res:
                if x not in none:
                    done.add(x)
            comb_data = make_result(data_dict, res, com)
            info = comb_data['info']
            comb_type = ['#' if (soul_type == comb_data['info'][i].values()[0][suit]) else '' for i in xrange(6)]

            if 1 and score_buf in [score_max_damage, score_buf_max_attack_only, score_max_crit_damage_only, score_buf_max_hp_shield]:
                ab = 0
                cd = 0
                ph = hero_hp_only
                ps = 0
                pc = 0
                for i in xrange(6):
                    v = info[i].values()[0]
                    ab += v[attack_buf] * 10
                    ab += v[attack] * 100 * 10 / hero_attack_only
                    cd += v[crit_damage] * 10
                    ph += v[hp_buf] * hero_hp_only / 100.0
                    ph += v[hp]
                    ps += v[speed]
                    pc += v[crit_rate]
                pa = (attack_buf_base_or_hp_buf_base * 10.0 + ab) / 1000.0 * hero_attack_only
                pd = (crit_damage_base * 10.0 + cd) / 1000.0
                print('%02d[%s]%s(+%s):%d=%.2f*%.2f,%.2fC,%.2fH,%.2fS' % (result_num, note, __[soul_type], __[p], int(pa * pd), pa, pd,
                    pc + 100 - damage_min_crit_rate, int(ph), base_speed + ps))
                for i in xrange(6):
                    v = info[i].values()[0]
                    print('[%d]%3dS%3dA%3dR%3dD %s' % (i+1, int(v[speed]+0.5), int(v[attack_buf]+0.5), int(v[crit_rate]+0.5), int(v[crit_damage]+0.5), comb_type[i]))
            if 1 and score_buf == score_buf_max_effect:
                print('%02d[%s]%s(+%s)maxeffect:%.1f,+%.2f' % (result_num, note, __[soul_type], __[p], score / 10.0 + effect_base, base_speed + comb_data['sum'][speed] / 100.0))
                for i in xrange(6):
                    v = info[i].values()[0]
                    print('[%d]%3dS%3dH%3dR%3dE %s' % (i+1, int(v[speed]+0.5), int(v[hp_buf]+0.5), int(v[crit_rate]+0.5), int(v[effect]+0.5), comb_type[i]))
            if 1 and score_buf == score_buf_max_resist:
                print('%02d[%s]%s(+%s)maxresist:%.1f,+%.2f' % (result_num, note, __[soul_type], __[p], score / 10.0 + effect_base, base_speed + comb_data['sum'][speed] / 100.0))
                for i in xrange(6):
                    v = info[i].values()[0]
                    print('[%d]%3dS%3dH%3dR%3dT %s' % (i+1, int(v[speed]+0.5), int(v[hp_buf]+0.5), int(v[crit_rate]+0.5), int(v[resist]+0.5), comb_type[i]))
            if 1 and score_buf == score_buf_max_hp_only:
                print('%02d[%s]%s(+%s)maxhp:%d+%.1f,+%.2f' % (result_num, note, __[soul_type], __[p], hero_attack_or_hero_hp, (score / 1000000.0 - 1) * hero_attack_or_hero_hp, base_speed + comb_data['sum'][speed] / 100.0))
                for i in xrange(6):
                    v = info[i].values()[0]
                    print('[%d]%3dS%3dH%3dR%3dT %s' % (i+1, int(v[speed]+0.5), int(v[hp_buf]+0.5), int(v[crit_rate]+0.5), int(v[resist]+0.5), comb_type[i]))
            return comb_data
        return None
    def cal_x_free_max_damage(soul_type, base_speed, prop_value_l6, buf_limit, note):
        global damage_limit
        damage = 0
        damage_limit = buf_limit
        res = []
        com = {}
        cc = 0
        desc = ''
        #for s in soul_peer:
        if 1:
            def __filter_type(mitama):
                if mitama.keys()[0] in done:
                    return False
                mitama_info = mitama.values()[0]
                location = mitama_info[pos]
                if location in [1, 2, 3, 5]:
                    enhance_type = mitama_info[suit]
                    return enhance_type == soul_type
                if location in [6]:
                    return (mitama_info[crit_rate] and mitama_info[crit_rate] >= 55)
                if location in [4]:
                    return (mitama_info[crit_rate] or mitama_info[crit_damage])
                return False
            def __build_mask():
                soul = []
                soul_2p_mask = int(0)
                soul_4p_mask = int(0)
                for (k, v) in data_format.MITAMA_ENHANCE.items():
                    if k == soul_type:
                        soul_4p_mask |= (4 << (3 * len(soul)))
                        soul.append(k)
                return soul, soul_2p_mask, soul_4p_mask

            r, c, n, v = filter_soul(__filter_type,
                                  prop_value_none,
                                  prop_value_none,
                                  prop_value_l6,
                                  __build_mask,
                                  crit_rate,
                                  False,
                                  score_max_damage,
                                  data_dict)
            if n > damage:
                damage, res, com, cc = n, r, c, v
        if len(res) > 0:
            for x in res:
                if x not in none:
                    done.add(x)
            comb_data = make_result(data_dict, res, com)
            print('%02d[%s]%s(+%s):%d=%.2f*%.2f,+%.2f' % (result_num, note,
                  __[soul_type], 'free', int(hero_attack_or_hero_hp * damage / 1000000 / 100),
                  (attack_buf_base_or_hp_buf_base * 10.0 + __decode(cc, offset_attackbuf, bits_attackbuf)) / 1000.0 * hero_attack_or_hero_hp,
                  (crit_damage_base * 10.0 + __decode(cc, offset_critdamage, bits_critdamage)) / 1000.0,
                  base_speed + comb_data['sum'][speed] / 100.0))
            return comb_data
        return None

    def cal_mask_top1(soul_type, loc, attr, note):
        def __filter_type(mitama):
            if mitama.keys()[0] in done:
                return False
            enhance_type = mitama.values()[0][suit]
            location = mitama.values()[0][pos]
            if location == loc:
                return enhance_type == soul_type
            return enhance_type == type_none
        def __build_mask():
            return [soul_type, type_none], 0, 0

        res, com, _, v = filter_soul(__filter_type,
                              prop_value_none,
                              prop_value_none,
                              prop_value_none,
                              __build_mask,
                              attr,
                              True,
                              score_suit_buf_none,
                              data_dict)
        if len(res) > 0:
            for x in res:
                if x not in none:
                    done.add(x)
            comb_data = make_result(data_dict, res, com)
            print('%02d[%s]%s():l%d@%s' % (result_num, note, __[soul_type], loc, __[attr]))
            return comb_data
        return None
    def cal_scarlet_mask_l6_speed():
        return cal_mask_top1(type_scarlet, 6, speed, ' xxxx')
    def cal_clear():
        done.clear()
        print '--'
        return None
    def cal_exit():
        sys.stdout.flush()
        os._exit(0)
        return None

    cbg = [
        cal_fortune_or_none,
        cal_clear,
        cal_freetype_max_speed,
        #cal_clear,
        cal_exit,
    ]
    order = cbg
    order.append(cal_clear)
    order = cbg
    def x_(asoul, bsoul):
        csoul = list(asoul)
        csoul.remove(bsoul)
        return csoul
    order = [
        cal_fortune_max_speed,                          #lian  DO1
        cal_freetype_max_speed,                         #mian  DO1
        [type_kyoukotsu,                [type_skull], 158, 156, 15+100, 3511, 12532, 115,  0+12, 160, '_jin (180)', score_max_crit_damage_only],
        #[type_kyoukotsu,               [type_geisha], 157, 156, 15+100, 3055, 11735, 115,  0+10, 150, '_yuan(180)'],
        [type_kyoukotsu,                   soul_crit,   0,   0, 15+100, 3136, 11165, 113, 15+10, 150, '_tun1(216)'],
        [type_kyoukotsu,                   soul_crit,   0,   0, 15+100, 3136, 11165, 113, 15+10, 150, '_tun2(216)'],
        cal_clear,
        cal_exit,
        [type_kyoukotsu,                [type_skull], 157, 156, 15+100, 3002, 10937, 115,  0+10, 150, '_xi  (199)'],
        cal_exit,
        [type_kyoukotsu,               [type_geisha],   0, 158, 15+100, 3511,     0, 115,  0+12, 160, '_jin (184)', score_max_crit_damage_only],
        cal_exit,
        [type_shadow,                   [type_skull],   0,   0,    100, 3511,     0, 120, 15+10, 150, '_cha1(   )', score_max_damage, [prop_crit_damage]],
        [type_kyoukotsu,  x_(soul_attack,type_taker),   1, 235, 30+100, 2841,     0, 111, 95+ 5, 150, '_jing(   )', score_buf_max_attack_only],
        [type_fire,                      soul_attack,   0, 235, 15+100, 2841,     0, 111, 95+ 5, 150, '_jing(   )', score_buf_max_attack_only],
        [type_taker,                     soul_attack,   0, 234, 30+100, 2841,     0, 111, 95+ 5, 150, '_jing(   )', score_buf_max_attack_only],
        [type_seductress,              [type_geisha],   0,   0,    115, 3136, 10026, 110, 15+10, 165, '_gou1(   )'],
        [type_seductress,              [type_geisha],   0,   0,    115, 3136, 10026, 110, 15+10, 165, '_gou2(   )'],
        [type_jizo,                        soul_crit,   0, 128,    100, 3457,  9229, 117, 45+10, 150, '_li  (243)', score_max_damage, [prop_crit_damage, prop_value_hp]],
        [type_shadow,                      soul_crit,   0, 194,    100, 3189, 11963, 109, 30+10, 150, '_gui1(   )', score_max_damage, [prop_crit_rate, prop_attack]],
        [type_fortune,                     soul_crit,   0, 194,    100, 3189, 11963, 109, 15+10, 150, '_gui2(   )', score_max_damage, [prop_crit_rate, prop_attack]],
        [type_watcher,                     soul_crit,   0, 128, 15+100, 3002,     0, 107, 15+ 8, 150, '_hua (   )'],   
        [type_seductress,                  soul_crit,   0, 134,    100, 3511,     0, 120, 30+10, 150, '_cha2(   )', score_max_damage, [prop_crit_damage]],
        [type_fortune,                     soul_crit, 134, 131,    311, 4074, 12418, 118, 15+10, 150, '_she1(   )', score_max_damage, [prop_crit_rate, prop_attack, prop_attack]],
        [type_sprite,                      soul_crit, 134, 131,    311, 4074, 12418, 118, 15+10, 150, '_she2(   )', score_max_damage, [prop_crit_rate, prop_value_hp]],
        [type_fire,                        soul_crit, 128, 111,    100, 2332, 13785, 108, 15+10, 150, '_hui1(   )'],
        [type_pearl,                       soul_crit,   0,   0,    100, 2385, 13785,  99, 15+ 3, 150, '_ying(   )', score_buf_max_hp_shield],
        cal_exit,
        [type_kyoukotsu,                   soul_crit, 158, 156, 15+100, 3511, 12532, 115, 15+12, 160, '_jin (198)', score_max_crit_damage_only],
        cal_clear,
        [type_kyoukotsu,                   soul_crit,   0, 158, 15+100, 3350, 12532, 110, 15+12, 160, '_yu  (179)'],
        cal_clear,
        [type_kyoukotsu,                [type_skull],   0, 158, 15+100, 3350, 12532, 110,  0+12, 160, '_yu  (161)'],


        [type_shadow,                      soul_crit,   0, 134,    311, 4074, 12418, 118, 30+10, 150, '_she1(   )', score_max_damage, [prop_crit_damage]],
        [type_fortune,                     soul_crit, 131, 130,    100, 2573, 12646, 120, 35+10, 150, '_shi1(   )', score_max_damage, [prop_crit_rate, prop_attack, prop_attack]],
        [type_fortune,                     soul_crit, 130, 129,    100, 1548,  9019, 120, 35+10, 150, '_shi2(   )', score_max_damage, [prop_crit_rate, prop_attack, prop_attack]],
        [type_fire,                        soul_crit, 129, 128,    100, 1386,  8206, 110, 35+10, 150, '_shi3(   )', score_max_damage, [prop_crit_rate, prop_attack, prop_attack]],
        cal_exit,
        [type_shadow,                   [type_skull],   0,   0,    100, 3377,     0, 111, 15+12, 150, '_chi (238)'],   

        cal_clear,
        [type_kyoukotsu,                [type_skull], 158, 156, 15+100, 3511,     0, 115,  0+12, 160, '_jin (180)', score_max_crit_damage_only],
        cal_clear,
        cal_exit,

        [type_kyoukotsu,                   soul_crit,   0, 128, 15+100, 3511,     0, 115, 15+12, 160, '_jin (226)'],
        [type_seductress,              [type_geisha],   0, 128, 15+100, 3511,     0, 115,  0+12, 160, '_jin (195)'],
        cal_exit,

        cal_exit,
        [type_kyoukotsu,               [type_geisha], 155, 134, 15+100, 3511,     0, 115,  0+12, 160, '_jin (180)', score_max_crit_damage_only],
        cal_exit,
        cal_freetype_max_speed,                         #mian  DO1
        cal_clear,
        #dou2
        [type_fire,                        soul_crit, 134, 128,    311, 4074, 12418, 118, 15+10, 150, '_she3(   )', score_max_damage, [prop_crit_rate, prop_value_hp]],
        cal_exit,



        [type_kyoukotsu,                [type_skull], 158, 156, 15+100, 3511,     0, 115,  0+12, 160, '_jin (208)'],
        #dong
        [type_seductress,   [type_geisha],   0,   0,    100, 3136, 10482, 109, 15+10, 185, '_fu  (   )'],
        cal_exit,
        [type_fortune,     [type_semisen],   0, 194,    100, 2948,     0, 109, 15+ 8, 180, '_jiu1(   )', score_max_damage, [prop_crit_rate, prop_attack]],
        [type_fortune,      [type_phenix],   0, 142,    100, 2332,     0, 108, 15+ 5, 150, '_ye1 (   )', score_max_damage, [prop_crit_rate, prop_attack]],
        #etc
        cal_exit,
        #dou3
        [type_seductress,       soul_crit,   0, 134,    100, 3270,     0, 110, 10+30, 150, '_tian(203)'],
        cal_exit,
        #feng
        [type_kyoukotsu,        soul_crit,   0, 134, 15+100, 2948,     0, 109, 55+ 8, 180, '_jiu3(   )'],
        cal_exit,


        [type_fortune,        [type_fire],   0, 183,    100, 13330, 116, 95+ 5, 150, '_bin (   )', score_buf_max_effect],
        cal_exit,
        [type_snow,           [type_fire],   0, 183,    100, 11849, 105, 95+ 5, 150, '_qin (   )', score_buf_max_effect],
        [type_shadow,           soul_crit,   0, 140,    100,  2948, 109, 30+ 8, 180, '_jiu2(   )'],
        [type_nymph,              soul_hp,   0, 225,    100, 14241, 111, 95+ 5, 150, '_bai (   )', score_buf_max_hp_only],
        [type_fortune,        soul_effect,   0, 240,    100,  6744, 118, 95+ 5, 150, '_mu  (   )', score_buf_max_effect],
        [type_shadow,           soul_crit,   0, 140,    100,  3323, 100, 30+10, 150, '_yue (   )'],
        [type_priestess,      soul_effect,   0, 210,    100,  2305, 112, 95+ 5, 150, '_niao(   )', score_buf_max_effect],
        [type_fire,             soul_crit,   0, 140,    100,  3457, 117, 45+10, 150, '_li2 (243)'],
        [type_sprite,         soul_resist,   0, 195,    100,  2251, 111,  0+ 3, 150, '_xun (   )', score_buf_max_resist, prop_value_none, resist],
        [type_shadow,           soul_crit,   0, 140,    100,  3404, 110, 30+20, 150, '_lan (   )'],
        [type_jizo,           soul_attack,   0, 140,    100, 11393, 121,  0+10, 150, '_lian(   )', score_buf_max_hp_shield],
        cal_exit,


        [type_fire,           soul_effect,   0, 194,    100,  2412, 119, 95+ 5, 150, '_zhu (   )', score_buf_max_effect, prop_value_none, effect, True],

        [type_shadow,           soul_crit, 128,   0,    100,  3323, 112, 30+15, 150, '_lin (215)'],
        [type_shadow,           soul_crit,   0, 140,    311,  4074, 118, 30+10, 150, '_she1(   )'],
        cal_exit,
        [type_seductress,       soul_crit,   0, 130,    100,  3350, 117, 30+11, 160, '_qie (   )'],   
        [type_fire,           soul_effect,   0, 194,    100, 2412, 119, 95+ 5, 150, '_zhu (   )', score_buf_max_effect, prop_value_none, effect, True],
        [type_jizo,             soul_crit, 128,   0,    100, 3457, 117, 45+10, 150, '_li  (243)'],

        [type_fortune,     [type_semisen],   0, 194,    100, 2948, 109, 15+ 8, 180, '_jiu (   )', score_max_damage, prop_crit_rate],
        [type_fortune,          soul_crit, 130, 128,    311, 4074, 118, 15+10, 150, '_she3(   )', score_max_damage, prop_crit_rate],
        cal_exit,
        [type_shadow,           soul_crit,   0, 128,    311, 4074, 118, 30+10, 150, '_she1(   )'],
        [type_fortune,          soul_crit,   0, 128,    311, 4074, 118, 15+10, 150, '_she2(   )', score_max_damage, prop_crit_rate],
        [type_fire,             soul_crit, 128,   0,    100, 3457, 117, 30+10, 150, '_li  (   )'],

        [type_fortune,          soul_crit, 120,   0,    311, 4074, 118, 15+10, 150, '_she2(   )'],
        cal_exit,
        cal_exit,
        [type_kyoukotsu, [type_shinkirou], 117,   0, 15+100, 3457, 117,    15, 150, '_li  (   )'],
        cal_exit,
        [type_shadow,           soul_crit, 0,   0,    100, 2948, 109, 30+ 8, 180, '_jiu (230)'],
        cal_exit,
        [type_kyoukotsu,        soul_crit, 0, 170, 15+100, 3136, 113, 15+10, 150, '_tun1(167)'],
        [type_kyoukotsu,        soul_crit, 0, 170, 15+100, 3136, 113, 15+10, 150, '_tun2(167)'],
        [type_jizo,             soul_crit, 0, 194, 15+100, 3350, 117, 15+11, 160, '_qie (   )'],   
        [type_dawnfairy, [type_shinkirou], 0, 162,    100, 2412, 105,     5, 150, '_qin ( 92)'],
    ]
    def xcal(xtype, xsoul, xmaxspeed, xminspeed, xattackbuf, xattack, xhp, xspeedbase, xcrit, xcritdamage, xnote, xscore, xprop, xsort, xone):
        global hero_attack_only
        global hero_hp_only
        global hero_attack_or_hero_hp
        global attack_buf_base_only
        global hp_buf_base_only
        global attack_buf_base_or_hp_buf_base
        global damage_min_crit_rate
        global crit_damage_base
        global damage_max_speed
        global damage_min_speed
        global effect_min_speed
        global effect_max_speed
        global effect_base
        global encode_hp_resist
        hero_attack_only = xattack
        hero_hp_only = xhp
        hero_attack_or_hero_hp = xattack
        attack_buf_base_only = xattackbuf
        hp_buf_base_only = 100
        attack_buf_base_or_hp_buf_base = xattackbuf
        if xscore in [score_buf_max_hp_only, score_buf_max_hp_shield]:
            encode_hp_resist = True
            hero_attack_or_hero_hp = xhp
            attack_buf_base_or_hp_buf_base = 100
            if xtype in soul_hp:
                attack_buf_base_or_hp_buf_base += 15
                hp_buf_base_only += 15
            for isoul in xsoul:
                if isoul in soul_hp:
                    attack_buf_base_or_hp_buf_base += 15
                    hp_buf_base_only += 15
                    break
        damage_min_crit_rate = 100 - xcrit
        crit_damage_base = xcritdamage
        damage_max_speed = (xmaxspeed - xspeedbase) if xmaxspeed >= xspeedbase else 500
        damage_min_speed = (xminspeed - xspeedbase) if xminspeed >= xspeedbase else 0
        effect_max_speed = damage_max_speed
        effect_min_speed = damage_min_speed
        if xscore == score_buf_max_effect:
            if xtype in soul_effect:
                effect_base = 0 + 15
            for isoul in xsoul:
                if isoul in soul_effect:
                    effect_base = effect_base + 15
                    break
        if xscore == score_buf_max_resist:
            encode_hp_resist = True
            if xtype in soul_resist:
                effect_base = 0 + 15
            for isoul in xsoul:
                if isoul in soul_resist:
                    effect_base = effect_base + 15
                    break
        r = calxmaxdamage(xtype, xsoul, xspeedbase, xprop, 0, xnote, xscore, xsort, xone)
        damage_max_speed = 500
        effect_base = 0
        encode_hp_resist = False
        return r
    for a in order:
        try:
            if isinstance(a, list):
                fscore = score_max_damage if len(a) <= 11 else a[11]
                fprop = [prop_value_none] if len(a) <= 12 else a[12]
                ssort = crit_rate if len(a) <= 13 else a[13]
                bone = False if len(a) <= 14 else a[14]
                comb = xcal(a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7], a[8], a[9], a[10], fscore, fprop, ssort, bone)
            else:
                comb = a()
            if comb is not None:
                yield comb
            if 0:
                done.clear()
        except Exception as e:
            print 'except', str(e).decode('raw_unicode_escape')
            sys.stdout.flush()
            os._exit(0)
    return

