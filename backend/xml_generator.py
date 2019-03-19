import dicttoxml

def generate(config, filename):
    with open(filename, 'w') as f:
        xmlstr = dicttoxml.dicttoxml(config).decode('utf-8')
        f.write(xmlstr)