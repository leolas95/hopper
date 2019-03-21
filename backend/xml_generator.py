import dicttoxml


def generate(config, filename):
    filename = filename + '.xml'
    with open(filename, 'w') as file:
        # Generate the XML representation and convert it to UTF-8
        xmlstr = dicttoxml.dicttoxml(config, attr_type=False).decode('utf-8')
        file.write(xmlstr)
