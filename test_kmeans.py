import os
import json
from sklearn.feature_extraction import DictVectorizer
from sklearn.cluster import KMeans
from sklearn.cluster import MiniBatchKMeans
import numpy as np
import pandas


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
    vec = DictVectorizer()
    vec_defects = vec.fit_transform(all_defects['defects'])
    km_defects = KMeans(n_clusters=100)
    km_defects.fit_transform(vec_defects)
    return vec, km_defects


def prepare_dictionary_2(folder):
    # 1. load 270 json, put defects and measurement together
    all_defects = put_together(folder)
    vec = DictVectorizer()
    vec_defects = vec.fit_transform(all_defects['defects'])
    km_defects = MiniBatchKMeans(n_clusters=100)
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


def to_csv():
    db = None
    ready = []
    with open('ready.json') as f:
        db = json.load(f)
    if db:
        for r in db:
            nr = {}
            nr['vzw'] = r['vzw']
            nr['Discoloration_Mic'] = r['Discoloration_Mic']
            nr['Discoloration_Logo'] = r['Discoloration_Logo']
            nr['Discoloration_Rear_Cam'] = r['Discoloration_Rear_Cam']
            nr['Discoloration_Switch'] = r['Discoloration_Switch']
            for i in range(1, 100):
                if i-1 < len(r['defects']):
                    nr['d{:02d}'.format(i)] = r['defects'][i-1]
                else:
                    nr['d{:02d}'.format(i)] = -1
            ready.append(nr)
        df = pandas.DataFrame.from_dict(ready)
        df['label'] = df['vzw'].astype('category').cat.codes
        df.pop('vzw')
        df.to_csv('ready.csv', index=False)


source_folder = 'data270_json'
vec, kmeans = prepare_dictionary_2(source_folder)
prepare_training_data_by_folder(source_folder, vec, kmeans)
to_csv()
