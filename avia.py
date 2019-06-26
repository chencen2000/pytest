import xml.etree.ElementTree as ET
import glob
import json
import os
from typing import Dict, Union
import pandas
import re
from sklearn.feature_extraction import DictVectorizer
from sklearn import cluster


def num(s):
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            return s


def etree_to_dict(t):
    d = {}
    for c in list(t):
        if c.text and not c.text.isspace():
            d[c.tag] = num(c.text)
        else:
            if len(c) > 0:
                a = []
                for ch in c.getchildren():
                    a.append(ch.text)
                d[c.tag] = a
    d.update(t.attrib)
    return d


def parse_defect_xml(filename):
    defects = []
    myxml = ET.parse(filename)
    surfaces = myxml.findall('.//surface')
    for surface in surfaces:
        defect_items = surface.findall('./sensor/defect/item')
        for item in defect_items:
            d = etree_to_dict(item)
            d['surface'] = surface.attrib['name']
            # ignore class='defect' and type='discoloration'
            if d['class'] == 'defect' and d['type'] == 'Discoloration' \
                    or d['type'] == 'OK' or d['type'] == 'OK' or d['class'] == 'fail':
                pass
            else:
                defects.append(d)
    return defects


def parse_avia_log(root='data270_xml', output='output'):
    # root = '117_Testing Set'
    # output = 'output'
    rg = re.compile(r'^defect_(\d*).xml$')
    vdb = None
    with open('verizon_data.json') as f:
        vdb = json.load(f)
    for r, d, f in os.walk(root):
        for fn in f:
            m = rg.match(fn)
            if m:
                print("parse: {}".format(fn))
                defects = parse_defect_xml(os.path.join(r, fn))
                vd = find_by_imei_last(m.group(1), vdb)
                dict = {}
                dict.update(vd)
                dict['defects'] = defects
                with open(os.path.join(output, '{}.json'.format(vd['imei'])), 'w') as f:
                    json.dump(dict, f, indent=4)


def find_by_imei_last(imei, vdb):
    ret = None
    for v in vdb:
        if v['imei'].endswith('{:0>4}'.format(imei)):
            ret = v
            break
    return ret


def load_device_json(folder='data270_json'):
    ret = []
    for fn in os.listdir(folder):
        data = None
        fullname = os.path.join(folder, fn)
        if os.path.isfile(fullname):
            with open(fullname) as f:
                try:
                    data = json.load(f)
                except:
                    pass
        if data:
            ret.append(data)
    return ret


def get_features(data):
    d1 = []
    d2 = []
    if data is not None:
        model = data['model']
        color = data['color']
        defects = data['defects']
        for i in defects:
            # print(i)
            if i['class'] == 'defect':
                n = {}
                n['model'] = model
                n['color'] = color
                n.update(i)
                n.pop('class', None)
                n.pop('defect_item', None)
                n.pop('location', None)
                d1.append(n)
            elif i['class'] == 'measurement':
                n = {}
                n['model'] = model
                n['color'] = color
                n.update(i)
                n.pop('class', None)
                n.pop('type', None)
                n.pop('surface', None)
                d2.append(n)
    return {
        'defects': d1,
        'measurement': d2
    }


def get_feature_score(data):
    features = {}
    if data:
        for d in data['defects']:
            if d['class'] == 'defect':
                k = '{}_{}'.format(d['surface'], d['type'])
                v = d['length'] * d['area_mm'] * d['contrast'] / d['width']
                if k not in features:
                    features[k] = 0
                features[k] += v
                pass
            elif d['class'] == 'measurement':
                features[d['region']] = d['value']
                pass
            else:
                pass
        data['features'] = features
    return data


def put_together(root):
    all_data = {
        'defects': [],
        'measurement': []
    }
    for fn in os.listdir(root):
        data = None
        fullname = os.path.join(root, fn)
        if os.path.isfile(fullname):
            with open(fullname) as f:
                try:
                    data = json.load(f)
                except:
                    pass
        if data:
            fe = get_features(data)
            all_data['defects'].extend(fe['defects'])
            all_data['measurement'].extend(fe['measurement'])
    return all_data


def csv_record(nc_d):
    ret = {
        'vzw': 'D',
        'Discoloration_Mic': 0,
        'Discoloration_Logo': 0,
        'Discoloration_Rear_Cam': 0,
        'Discoloration_Switch': 0
    }
    for i in range(0, nc_d):
        ret['D_{:03d}'.format(i+1)] = 0
    return ret


def csv_recode_score():
    return {
        'vzw': 'D',
        'AA_Scratch': 0,
        'AA_Nick': 0,
        'A_Scratch': 0,
        'A_Nick': 0,
        'A_PinDotGroup': 0,
        'B_Scratch': 0,
        'B_Nick': 0,
        'B_PinDotGroup': 0,
        'Logo': 0,
        'Switch': 0,
        'Rear_Cam': 0,
        'Mic': 0,
    }


def seperate_defects_by_surface(defects):
    ret = {}
    df = pandas.DataFrame.from_dict(defects)
    surfaces = df.surface.unique()
    for s in surfaces:
        x = df[df.surface == s]
        # d = {s: x.to_dict(orient='records')}
        ret[s] = x.to_dict(orient='records')
    return ret


def prepare_data_1(folder, nc_d=25):
    db = put_together(folder)
    surfaces = seperate_defects_by_surface(db['defects'])
    for s in surfaces:
        dv = DictVectorizer()
        vec = dv.fit_transform(surfaces[s])
        km = cluster.KMeans(n_clusters=nc_d)
        km.fit(vec)
        surfaces[s] = (dv, km)
    # dv_defects = DictVectorizer()
    # vec_defects = dv_defects.fit_transform(db['defects'])
    # km_defects = cluster.KMeans(n_clusters=nc_d)
    # km_defects.fit(vec_defects)
    ready = []
    for fn in os.listdir(folder):
        data = None
        fullname = os.path.join(folder, fn)
        if os.path.isfile(fullname):
            with open(fullname) as f:
                try:
                    data = json.load(f)
                except:
                    pass
        if data:
            fe = get_features(data)
            r = {}
            r['vzw'] = data['vzw']
            r['measurement'] = fe['measurement']
            if len(fe['defects']) > 0:
                ss = seperate_defects_by_surface(fe['defects'])
                for s in ss:
                    dv, km = surfaces[s]
                    vec = dv.transform(ss[s])
                    p = km.transform(ss[s])
                    r[s] = p.tolist()
            ready.append(r)
    # save data into json
    # with open('test.json', 'w') as f:
    #     json.dump(ready, f, indent=4)
    ready_csv = []
    for r in ready:
        csv = csv_record(nc_d)
        csv['vzw'] = r['vzw']
        for i in r['defects']:
            k = 'D_{:03d}'.format(i+1)
            if k in csv:
                csv[k] += 1
        for i in r['measurement']:
            k = 'Discoloration_{}'.format(i['region'])
            if k in csv:
                csv[k] = i['value']
        ready_csv.append(csv)
    # with open('test.json', 'w') as f:
    #     json.dump(ready_csv, f, indent=4)
    return ready_csv


def prepare_data(folder, nc_d=25):
    db = put_together(folder)
    dv_defects = DictVectorizer()
    vec_defects = dv_defects.fit_transform(db['defects'])
    km_defects = cluster.KMeans(n_clusters=nc_d)
    km_defects.fit(vec_defects)
    ready = []
    for fn in os.listdir(folder):
        data = None
        fullname = os.path.join(folder, fn)
        if os.path.isfile(fullname):
            with open(fullname) as f:
                try:
                    data = json.load(f)
                except:
                    pass
        if data:
            fe = get_features(data)
            if len(fe['defects']) > 0:
                vec = dv_defects.transform(fe['defects'])
                p = km_defects.predict(vec)
                data['vd'] = p.tolist()
                r = {}
                r['vzw'] = data['vzw']
                r['defects'] = p.tolist()
                r['measurement'] = fe['measurement']
            ready.append(r)
    # save data into json
    # with open('test.json', 'w') as f:
    #     json.dump(ready, f, indent=4)
    ready_csv = []
    for r in ready:
        csv = csv_record(nc_d)
        csv['vzw'] = r['vzw']
        for i in r['defects']:
            k = 'D_{:03d}'.format(i+1)
            if k in csv:
                csv[k] += 1
        for i in r['measurement']:
            k = 'Discoloration_{}'.format(i['region'])
            if k in csv:
                csv[k] = i['value']
        ready_csv.append(csv)
    # with open('test.json', 'w') as f:
    #     json.dump(ready_csv, f, indent=4)
    return ready_csv


def prepare_data_score(folder):
    db = []
    for fn in os.listdir(folder):
        data = None
        fullname = os.path.join(folder, fn)
        if os.path.isfile(fullname):
            with open(fullname) as f:
                try:
                    data = json.load(f)
                except:
                    pass
        if data:
            fe = get_feature_score(data)
            r = csv_recode_score()
            r['vzw'] = fe['vzw']
            r['model'] = fe['model']
            r['color'] = fe['color']
            for f in fe['features']:
                if f in r:
                    r[f] = fe['features'][f]
            db.append(r)
    with open('test.json', 'w') as f:
        json.dump(db, f, indent=4)
    df = pandas.DataFrame.from_dict(db)
    df['model'] = df['model'].astype('category').cat.codes
    df['color'] = df['color'].astype('category').cat.codes
    df['label'] = df['vzw'].astype('category').cat.codes
    df.drop('vzw', axis=1).to_csv('test.csv', index=False)


# parse_avia_log('data270_xml/iPhone6s Gray')
# db = prepare_data('iPhone6s Gray')
prepare_data_score('data270_json')
