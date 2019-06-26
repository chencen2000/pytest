import xml.etree.ElementTree as ET
import glob
import json
import os
import pandas
import re


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


def parse_270_log():
    root = '117_Testing Set'
    output = 'output'
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


def parse_classify_log_count(text):
    ret = {}
    if text:
        for s in text.split('\n'):
            if s:
                pos = s.index('=')
                if 0 < pos < len(s):
                    k = s[0:pos].strip()
                    v = int(s[pos+1:])
                    ret[k] = v
    return ret


def parse_classify_log_surface(surface, text):
    ret = {}
    if surface and text:
        for s in text.split('\n'):
            if s:
                s = s.strip()
                pos = s.index('=')
                if s.startswith('Totoal number on') and pos > 0:
                    ret['All-{}-ALL'.format(surface)] = int(s[pos+1:])
                elif s.startswith('Totoal number of major on') and pos > 0:
                    ret['All-{}-Major'.format(surface)] = int(s[pos+1:])
                elif s.startswith('Zone') and pos > 0:
                    ret['All-{}-{}'.format(surface, s[0:pos].strip())] = int(s[pos + 1:])
    return ret


def parse_classify_log(filename):
    ret = {}
    with open(filename) as f:
        text = f.read()
    r = re.compile(r'Flaws:(.*)Count:(.*)AA Surface:(.*)A Surface:(.*)B Surface:(.*)C Surface:(.*)Grade = (.*)',
                   flags=re.S)
    m = r.match(text)
    if m:
        ret.update(parse_classify_log_count(m.group(2)))
        ret.update(parse_classify_log_surface('AA', m.group(3)))
        ret.update(parse_classify_log_surface('A', m.group(4)))
        ret.update(parse_classify_log_surface('B', m.group(5)))
        ret.update(parse_classify_log_surface('C', m.group(6)))
    return ret


def parse_270_log_v2(root='data270_xml', output='output'):
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
                log_fn = 'classify_{}.txt'.format(m.group(1))
                print("parse: {} and {}".format(fn, log_fn))
                defects = parse_defect_xml(os.path.join(r, fn))
                vd = find_by_imei_last(m.group(1), vdb)
                dict = {}
                dict.update(vd)
                dict['defects'] = defects
                if os.path.exists(os.path.join(r, log_fn)):
                    dict['counts'] = parse_classify_log(os.path.join(r, log_fn))
                with open(os.path.join(output, '{}.json'.format(vd['imei'])), 'w') as f:
                    json.dump(dict, f, indent=4)

'''
defects = parse_defect_xml(r'C:\Tools\avia\test.xml')
s = json.dumps(defects)
print(s)
'''


def func1():
    root = 'C:\\projects\\avia\\pytest\\data270_json'
    for fn in os.listdir(root):
        data = None
        fullname = os.path.join(root, fn)
        if os.path.isfile(fullname):
            db = []
            with open(fullname) as f:
                try:
                    data = json.load(f)
                except:
                    pass
            if data is None:
                f = open(fullname, 'w')
                f.write('[]')
                f.close()
            else:
                for i in data:
                    if i['class'] == 'defect' and i['type'] == 'Discoloration':
                        print(i)
                        '''
                    else:
                        db.append(i)
                f = open(fullname, 'w')
                # f.write('[]')
                json.dump(db, f, indent=4)
                f.close() '''


def func2():
    df = pandas.read_excel('test\\FD COSMETIC GRADING GAGE_G270_G117.xlsx', sheet_name='GAGE', dtype=str)
    db = []
    for i in df.index:
        r = {}
        imei = df['IMEI'][i]
        vzw = df['VZW Adjusted Grade'][i]
        model = df['Model'][i]
        color = df['Color'][i]
        if not pandas.isna(imei) and not pandas.isna(vzw):
            r['imei'] = imei
            r['model'] = model
            r['color'] = color
            r['vzw'] = vzw
            db.append(r)
    s = json.dumps(db, indent=4)
    print(s)


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
                defects = data['defects']
                for i in defects:
                    #print(i)
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
    f = open('all_defects.json', 'w')
    # f.write('[]')
    json.dump(db, f, indent=4)
    f.close()


def func_3():
    db = json.load(open('all_defects.json'))
    surfaces = ['B', 'A', 'AA']
    oetypes = ['Discoloration', 'Nick', 'PinDotGroup', 'OK', 'Fail', 'Scratch']
    surface = 'AA'
    oetype = 'Nick'
    for surface in surfaces:
        for oetype in oetypes:
            db2 = list(filter(lambda x: x['surface'] == surface and x['type'] == oetype, db))
            print('{}_{}: {}'.format(surface, oetype, len(db2)))
    # print(json.dumps(db2))


def find_by_imei_last(imei, vdb):
    ret = None
    for v in vdb:
        if v['imei'].endswith('{:0>4}'.format(imei)):
            ret = v
            break
    return ret


def find_by_imei(imei, vdb):
    ret = None
    for v in vdb:
        if v['imei'] == imei:
            ret = v
            break
    return ret


def score_270():
    root = 'C:\\projects\\avia\\pytest\\data270_json'
    vdb = json.load(open('verizon_data.json'))
    r = re.compile(r'^defect_(\d*).json$')
    scores = {}
    weights = {
        'AA': 10.0,
        'A': 5.0,
        'B': 1.0,
    }
    for fn in os.listdir(root):
        data = None
        m = r.match(fn)
        if m:
            fullname = os.path.join(root, fn)
            if os.path.isfile(fullname):
                score = 0.0
                with open(fullname) as f:
                    try:
                        data = json.load(f)
                    except:
                        pass
                if data is not None:
                    for i in data:
                        w = weights[i['surface']]
                        if i['class'] == 'measurement' and i['type'] == 'Discoloration':
                            score += 1000.0*i['value']
                        else:
                            score += i['area_pixel']*i['contrast']*w
                print('{} score: {}'.format(fn, score))
                scores[m.group(1)] = score
    rdb = []
    for s in scores:
        r = find_by_imei(s, vdb)
        if r:
            r['score'] = scores[s]
            rdb.append(r)
    with open('result.json', 'w') as f:
        json.dump(rdb, f, indent=4)


def check_score():
    grade = ['A+', "A", 'B', 'C', 'D+', 'D']
    with open('result.json') as f:
        db = json.load(f)
    for g in grade:
        f = list(filter(lambda x: x['vzw'] == g, db))
        i = list(map(lambda d: d['score'], f))
        print('{} score: max={}, min={}'.format(g, max(i), min(i)))


def prepare_data_1(filename):
    data = {
        'AA_Scratch_Count': 0,
        'AA_Scratch_Value': 0,
        'AA_Nick_Count': 0,
        'AA_Nick_Value': 0,
        'AA_PinDotGroup_Count': 0,
        'AA_PinDotGroup_Value': 0,
        'A_Scratch_Count': 0,
        'A_Scratch_Value': 0,
        'A_Nick_Count': 0,
        'A_Nick_Value': 0,
        'A_PinDotGroup_Count': 0,
        'A_PinDotGroup_Value': 0,
        'B_Scratch_Count': 0,
        'B_Scratch_Value': 0,
        'B_Nick_Count': 0,
        'B_Nick_Value': 0,
        'B_PinDotGroup_Count': 0,
        'B_PinDotGroup_Value': 0,
        'Discoloration_Mic': 0,
        'Discoloration_Logo': 0,
        'Discoloration_Rear_Cam': 0,
        'Discoloration_Switch': 0
    }
    th = {
        'AA': 5,
        'A': 10,
        'B': 20
    }
    db = None
    with open(filename) as f:
        db = json.load(f)
    if db:
        data['vzw'] = db['vzw']
        data['imei'] = db['imei']
        defects = db['defects']
        for r in defects:
            if r['type'] == 'Discoloration':
                k = '{}_{}'.format(r["type"], r['region'])
                if k in data:
                    data[k] += r['value']
            else:
                k1 = '{}_{}_Count'.format(r["surface"], r['type'])
                k2 = '{}_{}_Value'.format(r["surface"], r['type'])
                if k1 in data and k2 in data:
                    if r['contrast'] >= th[r['surface']]:  # if contrast < 10 ignore.
                        data[k1] += 1
                        data[k2] += r['length'] * r['area_pixel'] * r['contrast'] / r['width']
    return data


def prepare_data():
    root = 'data270_json'
    ex = [
        '353009097159887.json'
    ]
    db = []
    for r, d, f in os.walk(root):
        for fn in f:
            if not fn in ex:
                data = prepare_data_1(os.path.join(r, fn))
                db.append(data)
    with open('ready.json', 'w') as f:
        json.dump(db, f, indent=4)


def convert_data_to_csv(filename):
    db = None
    with open(filename) as f:
        db = json.load(f)
    if db:
        pd = pandas.DataFrame.from_dict(db)
        pd['label'] = pd['vzw'].astype('category').cat.codes
        pd.to_csv('test.csv', index=False)
        pd.pop('imei')
        pd.pop('vzw')
        pd.to_csv('ready.csv', index=False)


def load_270_json(folder):
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


def rule_base_test(src, target='test.csv'):
    folder = 'output'
    # grades = ['A+', 'A', 'B', 'C', 'D+']
    for fn in os.listdir(folder):
        os.remove(os.path.join(folder, fn))
    parse_270_log_v2(src, folder)
    data = []
    for fn in os.listdir(folder):
        db = None
        with open(os.path.join(folder, fn)) as f:
            db = json.load(f)
        if db:
            r = {
                'All-A-ALL': 0,
                'All-A-Major': 0,
                'All-AA-ALL': 0,
                'All-AA-Major': 0,
                'All-AA-Zone1': 0,
                'All-AA-Zone2': 0,
                'All-AA-Zone3': 0,
                'All-AA-Zone4': 0,
                'All-AA-Zone5': 0,
                'All-B-ALL': 0,
                'All-B-Major': 0,
                'All-C-ALL': 0,
                'All-C-Major': 0,
                'Discoloration-B-Area1': 0,
                'Discoloration-B-Logo': 0,
                'Discoloration-B-Mic': 0,
                'Discoloration-B-Rear_Cam': 0,
                'Discoloration-B-Switch': 0,
                'Nick-A-Minor': 0,
                'Nick-A-Other1': 0,
                'Nick-A-Other2': 0,
                'Nick-A-S': 0,
                'Nick-AA-Minor': 0,
                'Nick-AA-Other1': 0,
                'Nick-AA-Other2': 0,
                'Nick-B-Major': 0,
                'Nick-B-MajorC': 0,
                'Nick-B-Minor': 0,
                'Nick-B-MinorC': 0,
                'Nick-B-Other1': 0,
                'Nick-B-Other2': 0,
                'Nick-B-OtherC': 0,
                'Nick-B-S': 0,
                'PinDotGroup-A-10x10': 0,
                'PinDotGroup-B-10x10': 0,
                'PinDotGroup-B-10x40': 0,
                'PinDotGroup-B-Other': 0,
                'Scratch-A-Minor': 0,
                'Scratch-A-Other1': 0,
                'Scratch-A-Other2': 0,
                'Scratch-A-Other3': 0,
                'Scratch-A-S1': 0,
                'Scratch-A-S2': 0,
                'Scratch-AA-Major': 0,
                'Scratch-AA-Minor': 0,
                'Scratch-AA-Other1': 0,
                'Scratch-AA-Other2': 0,
                'Scratch-AA-S': 0,
                'Scratch-B-Major': 0,
                'Scratch-B-Minor': 0,
                'Scratch-B-Other1': 0,
                'Scratch-B-Other2': 0,
                'Scratch-B-Other3': 0,
                'Scratch-B-S1': 0,
                'Scratch-B-S2': 0,
                'vzw': 0
            }
            # r['vzw'] = grades.index(db['vzw'])
            r['vzw'] = db['vzw']
            r['model'] = db['model']
            r['color'] = db['color']
            for i in db['counts']:
                if i in r:
                    r[i] = db['counts'][i]
            data.append(r)
    with open('test.json', 'w') as f:
        json.dump(data, f, indent=4)
    df = pandas.DataFrame.from_dict(data)
    x = df.drop(['color','model','vzw'], axis=1)
    # x['color'] = df['color'].astype('category').cat.codes
    # x['model'] = df['model'].astype('category').cat.codes
    x['vzw'] = df['vzw'].astype('category').cat.codes
    x.to_csv(target, index=False)


# check_score()
# d = parse_defect_xml('data270_xml\\123\\defect_123.xml')
# with open('test\\test.json', 'w') as f:
#     json.dump(d, f, indent=4)
# parse_270_log()
# data = prepare_data_1('data270_json/355344086238212.json')
# print(json.dumps(data, indent=4))
# parse_defect_xml('data270_xml/iPhone6 Gold/123/defect_123.xml')
# prepare_data()
# convert_data_to_csv('ready.json')
# put_together()
# parse_classify_log('data270_xml/iPhone6 Gold/123/classify_123.txt')
# rule_base_test('117_Testing Set')
rule_base_test('117_Testing Set')
# rule_base_test('data270_xml', 'ready.csv')
