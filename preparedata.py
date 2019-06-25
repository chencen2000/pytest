import json
import os
import pandas
from sklearn.feature_extraction import DictVectorizer
import numpy as np
from sklearn import neighbors



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


def put_together():
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


db = put_together()
dv_defects = DictVectorizer()
vec_defects = dv_defects .fit_transform(db['defects']).toarray()

