import json
import os
import pandas
from sklearn.feature_extraction import DictVectorizer
import numpy as np
from sklearn import neighbors
from sklearn.cluster import KMeans


def save_all_defects(folder):
    for fn in os.listdir(folder):
        db = None
        with open(os.path.join(folder, fn)) as f:
            db = json.load(f)
        if db:
            pass


def seperate_defects_by_model_color(filename):
    df = None
    with open(filename) as f:
        db = json.load(f)
        if db:
            df = pandas.DataFrame.from_dict(db['defects'])
    if df:
        models = df.model.unique
        colors = df.color.unique
        for m in models:
            for c in colors:
                pass


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
    return  all_data


def put_together_1():
    root = 'data270_json'
    d1 = []
    d2 = []
    for fn in os.listdir(root):
        data = None
        fullname = os.path.join(root, fn)
        if os.path.isfile(fullname):
            with open(fullname) as f:
                try:
                    data = json.load(f)
                except:
                    pass
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
    db = {
        'defects': d1,
        'measurement': d2
    }
    # f = open('all_defects_1.json', 'w')
    # json.dump(db, f, indent=4)
    # f.close()
    return db


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


def create_training_data(nc_d, nc_m):
    ret = {}
    ret['vzw'] = 'D'
    for i in range(0, nc_d):
        ret['D_{:03d}'.format(i)] = 0
    for i in range(0, nc_m):
        ret['M_{:03d}'.format(i)] = 0
    return ret


def test():
    root = 'data270_json'
    db = put_together(root)
    dv_defects = DictVectorizer()
    vec_defects = dv_defects.fit_transform(db['defects'])
    km_defects = KMeans(n_clusters=nc_d)
    km_defects.fit(vec_defects)
    dv_m = DictVectorizer()
    vec_m = dv_m.fit_transform(db['measurement'])
    km_m = KMeans(n_clusters=nc_m)
    km_m.fit(vec_m)
    ready = []
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
            if len(fe['defects']) > 0:
                vec = dv_defects.transform(fe['defects'])
                p = km_defects.predict(vec)
                data['vd'] = p.tolist()
            if len(fe['measurement']) > 0:
                vec = dv_m.transform(fe['measurement'])
                p = km_m.predict(vec)
                data['vm'] = p.tolist()
            ready.append(data)
    # with open('test.json', 'w') as f:
    #     json.dump(ready, f, indent=4)
    return ready


def test_1():
    root = 'data270_json'
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
            all_data['defects'].append(fe['defects'])
            all_data['measurement'].append(fe['measurement'])
    with open('test.json', 'w') as f:
        json.dump(all_data, f, indent=4)


nc_d = 128
nc_m = 20
db = test()
ready = []
for r in db:
    nr = create_training_data(nc_d, nc_m)
    nr['vzw'] = r['vzw']
    # nr['model'] = r['model']
    # nr['color'] = r['color']
    if 'vd' in r:
        for i in r['vd']:
            k = 'D_{:03d}'.format(i)
            nr[k] += 1
    if 'vm' in r:
        for i in r['vm']:
            k = 'M_{:03d}'.format(i)
            nr[k] += 1
    ready.append(nr)
with open('test.json', 'w') as f:
    json.dump(ready, f, indent=4)
df = pandas.DataFrame.from_dict(ready)
df['label'] = df['vzw'].astype('category').cat.codes
df.pop('vzw')
df.to_csv('test.csv', index=False)

