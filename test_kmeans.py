import os
import json
from sklearn.feature_extraction import DictVectorizer
from sklearn.cluster import KMeans
from sklearn.cluster import MiniBatchKMeans
import numpy as np
import pandas


def put_defects_togetther(root):
    dm = []
    daa = []
    da = []
    dsb = []
    regions = ['Logo', 'Switch', 'Rear_Cam', 'Mic']
    types = ['Nick', 'Scratch', 'PinDotGroup']
    for fn in os.listdir(root):
        fullname = os.path.join(root, fn)
        db = None
        if os.path.isfile(fullname):
            with open(fullname) as f:
                db = json.load(f)
        if db:
            model = db['model']
            color = db['color']
            for d in db['defects']:
                if d['class'] == 'measurement':
                    r = {
                        'region': regions.index(d['region']),
                        'value': d['value']
                    }
                    dm.append(r)
                elif d['class'] == 'defect':
                    r = {
                        'type': types.index(d['type']),
                        'length': d['length'],
                        'width': d['width'],
                        'area_mm': d['area_mm'],
                        'area_pixel': d['area_pixel'],
                        'contrast': d['contrast']
                    }
                    if d['surface'] == 'AA':
                        daa.append(r)
                    elif d['surface'] == 'A':
                        da.append(r)
                    elif d['surface'] == 'B':
                        dsb.append(r)
    db = {
        'measurement': dm,
        'surface_AA': daa,
        'surface_A': da,
        'surface_B': dsb
    }
    return db


def put_together(root):
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
                defects = data['defects']
                for i in defects:
                    if i['class'] == 'defect':
                        i.pop('class', None)
                        i.pop('defect_item', None)
                        i.pop('location', None)
                        i['model'] = data['model']
                        i['color'] = data['color']
                        d1.append(i)
                    elif i['class'] == 'measurement':
                        i.pop('class', None)
                        i.pop('type', None)
                        i.pop('surface', None)
                        d2.append(i)
    db = {
        'defects': d1,
        'measurement': d2
    }
    # f = open('all_defects.json', 'w')
    # f.write('[]')
    # json.dump(db, f, indent=4)
    # f.close()
    return db


def prepare_dictionary(folder):
    # 1. load 270 json, put defects and measurement together
    all_defects = put_together(folder)
    with open('all_defects.json', 'w') as f:
        json.dump(all_defects, f, indent=4)
    vec = DictVectorizer()
    vec_defects = vec.fit_transform(all_defects['defects'])
    km_defects = KMeans(n_clusters=n_cluster)
    km_defects.fit_transform(vec_defects)
    return vec, km_defects


def prepare_dictionary_2(folder):
    # 1. load 270 json, put defects and measurement together
    all_defects = put_together(folder)
    vec = DictVectorizer()
    vec_defects = vec.fit_transform(all_defects['defects'])
    km_defects = MiniBatchKMeans(n_clusters=n_cluster)
    km_defects.fit(vec_defects)
    return vec, km_defects


def prediction_defect(defects, vec, kmeans):
    ready = []
    for defect in defects:
        if defect['class'] == 'defect':
            defect.pop('defect_item', None)
            defect.pop('location', None)
            defect.pop('class', None)
            ready.append(defect)
    if len(ready) > 0:
        v = vec.transform(ready)
        p = kmeans.predict(v)
        ready = np.sort(p, axis=None).tolist()
    return ready


def prepare_training_data_by_filename(filename, vec, kmeans):
    ret = {}
    db = None
    with open(filename) as f:
        db = json.load(f)
    if db:
        ret['vzw'] = db['vzw']
        ret['imei'] = db['imei']
        ret['Discoloration_Mic'] = 0
        ret['Discoloration_Logo'] = 0
        ret['Discoloration_Rear_Cam'] = 0
        ret['Discoloration_Switch'] = 0
        for r in db['defects']:
            if r['class'] == 'measurement':
                if '{}_{}'.format(r['type'], r['region']) in ret:
                    ret['{}_{}'.format(r['type'], r['region'])] = r['value']
        ret['defects'] = prediction_defect(db['defects'], vec, kmeans)
        # print(json.dumps(ret))
        return ret


def prepare_training_data_by_folder(src, vec, kmeans):
    db = []
    for fn in os.listdir(src):
        r = prepare_training_data_by_filename(os.path.join(src, fn), vec, kmeans)
        db.append(r)
    with open('ready.json', 'w') as f:
        json.dump(db, f, indent=4)


def csv_new_record(count):
    cols = {}
    cols['vzw'] = 0
    cols['Discoloration_Mic'] = 0
    cols['Discoloration_Logo'] = 0
    cols['Discoloration_Rear_Cam'] = 0
    cols['Discoloration_Switch'] = 0
    for i in range(1, count+1):
        cols['AA_{:03d}'.format(i)] = 0
    for i in range(1, count+1):
        cols['A_{:03d}'.format(i)] = 0
    for i in range(1, count+1):
        cols['B_{:03d}'.format(i)] = 0
    return cols


def to_csv():
    db = None
    ready = []
    with open('ready.json') as f:
        db = json.load(f)
    if db:
        for r in db:
            nr = csv_new_record()
            nr['vzw'] = r['vzw']
            nr['Discoloration_Mic'] = r['Discoloration_Mic']
            nr['Discoloration_Logo'] = r['Discoloration_Logo']
            nr['Discoloration_Rear_Cam'] = r['Discoloration_Rear_Cam']
            nr['Discoloration_Switch'] = r['Discoloration_Switch']
            for i in r['defects']:
                k = 'd{:03d}'.format(i)
                if k in nr:
                    nr[k] = nr[k]+1
            ready.append(nr)
        df = pandas.DataFrame.from_dict(ready)
        df['label'] = df['vzw'].astype('category').cat.codes
        df.pop('vzw')
        df.to_csv('ready.csv', index=False)


def prepare_trainging_data_1():
    n_cluster = 180
    source_folder = 'data270_json'
    vec, kmeans = prepare_dictionary(source_folder)
    prepare_training_data_by_folder(source_folder, vec, kmeans)
    to_csv()


def compute_features_from_file(filename):
    s_aa = []
    s_a = []
    s_b = []
    s_m = []
    info = {}
    regions = ['Logo', 'Switch', 'Rear_Cam', 'Mic']
    types = ['Nick', 'Scratch', 'PinDotGroup']
    db = None
    with open(filename) as f:
        db = json.load(f)
    if db:
        info['vzw'] = db['vzw']
        info['imei'] = db['imei']
        info['model'] = db['model']
        info['color'] = db['color']
        for r in db['defects']:
            if r['class'] == 'measurement':
                s_m.append({
                    'region': 'Discoloration_{}'.format(r['region']),
                    'value': r['value']
                })
            elif r['class'] == 'defect':
                n = {
                    'type': types.index(r['type']),
                    'length': r['length'],
                    'width': r['width'],
                    'area_mm': r['area_mm'],
                    'area_pixel': r['area_pixel'],
                    'contrast': r['contrast']
                }
                if r['surface'] == 'AA':
                    s_aa.append(n)
                elif r['surface'] == 'A':
                    s_a.append(n)
                elif r['surface'] == 'B':
                    s_b.append(n)
    db = {
        'info': info,
        'measurement': s_m,
        'surface_AA': s_aa,
        'surface_A': s_a,
        'surface_B': s_b
    }
    return db


src = 'data270_json'
'''
db = put_defects_togetther('data270_json')
with open('test.json', 'w') as f:
    json.dump(db, f, indent=4)
km_aa = KMeans(n_clusters=10)
x = pandas.DataFrame.from_dict(db["surface_AA"])
km_aa.fit(x)
km_a = KMeans(n_clusters=10)
x = pandas.DataFrame.from_dict(db["surface_A"])
km_a.fit(x)
km_b = KMeans(n_clusters=10)
x = pandas.DataFrame.from_dict(db["surface_B"])
km_b.fit(x)
for fn in os.listdir('data270_json'):
    db = None
    with open(os.path.join('data270_json', fn)) as f:
        db = json.load(f)
'''
def test():
    nc = 25
    feature_measurement = []
    feature_surface_AA = []
    feature_surface_A = []
    feature_surface_B = []
    for fn in os.listdir(src):
        fs = compute_features_from_file(os.path.join(src, fn))
        feature_measurement.extend(fs['measurement'])
        feature_surface_AA.extend(fs['surface_AA'])
        feature_surface_A.extend(fs['surface_A'])
        feature_surface_B.extend(fs['surface_B'])
    with open('test.json', 'w') as f:
        json.dump(feature_measurement, f, indent=4)
    km_aa = KMeans(n_clusters=nc)
    x = pandas.DataFrame.from_dict(feature_surface_AA)
    km_aa.fit(x)
    km_a = KMeans(n_clusters=nc)
    x = pandas.DataFrame.from_dict(feature_surface_A)
    km_a.fit(x)
    km_b = KMeans(n_clusters=nc)
    x = pandas.DataFrame.from_dict(feature_surface_B)
    km_b.fit(x)
    ready = []
    for fn in os.listdir(src):
        r = csv_new_record(nc)
        fs = compute_features_from_file(os.path.join(src, fn))
        r['vzw'] = fs['info']['vzw']
        for i in fs['measurement']:
            r[i['region']] = i['value']
        if len(fs['surface_AA']) > 0:
            x = pandas.DataFrame.from_dict(fs['surface_AA'])
            p = km_aa.predict(x)
            for i in p:
                k = 'AA_{:03d}'.format(i)
                if k in r:
                    r[k] += 1
        if len(fs['surface_A']) > 0:
            x = pandas.DataFrame.from_dict(fs['surface_A'])
            p = km_a.predict(x)
            for i in p:
                k = 'A_{:03d}'.format(i)
                if k in r:
                    r[k] += 1
        if len(fs['surface_B']) > 0:
            x = pandas.DataFrame.from_dict(fs['surface_B'])
            p = km_b.predict(x)
            for i in p:
                k = 'B_{:03d}'.format(i)
                if k in r:
                    r[k] += 1
        ready.append(r)
    with open('ready.json', 'w') as f:
        json.dump(ready, f, indent=4)
    df = pandas.DataFrame.from_dict(ready)
    df['label'] = df['vzw'].astype('category').cat.codes
    df.pop('vzw')
    df.to_csv('ready.csv', index=False)


def load_270_json(folder='data270_json'):
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


def count_model_color(data):
    if data is not None:
        models = data['model'].unique()
        colors = data['color'].unique()
        for m in models:
            for c in colors:
                cnt = len(data[(data['model'] == m) & (data['color'] == c)])
                if cnt > 0:
                    print('{} {} are {}'.format(m, c, cnt))


# db = load_270_json()
# count_model_color(db)