import xml.etree.ElementTree as ET
import json

def defect_xml_to_json(filename = 'BZ_defect.xml'):
    xml = ET.parse(filename)
    data = {}
    defects = []
    for c in list(xml.getroot()):
        if c.tag != 'station':
            data[c.tag] = c.text
        else:
            pass
    # for each defect
    for sta in xml.getroot().findall('station'):
        for alg in list(sta):
            for suf in list(alg):
                defect_data = {'station': sta.get('name'), 'alg': alg.get('name'), 'surface': suf.get('name')}
                x = suf.find('ROIregion')
                temp = x.text.split(',')
                defect_data['ROIregion.x'] = temp[0]
                defect_data['ROIregion.y'] = temp[1]
                defect_data['ROIregion.width'] = temp[2]
                defect_data['ROIregion.height'] = temp[3]
                x = suf.find('defect/item')
                for c in list(x):
                    if c.tag != 'location':
                        defect_data[c.tag] = c.text
                    else:
                        loc = 0
                        for pt in list(c):
                            temp = pt.text.split(',')
                            defect_data['location_{}.x'.format(loc)] = temp[0]
                            defect_data['location_{}.y'.format(loc)] = temp[1]
                            loc += 1
                defects.append(defect_data)
    data['defects'] = defects
    return json.dumps(data, indent=4)


json_str = defect_xml_to_json()
print(json_str)
# save to file
with open('test.json', 'w') as f:
    f.write(json_str)