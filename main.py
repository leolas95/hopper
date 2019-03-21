import argparse

from textx import metamodel_from_file

from model_parser import ModelParser
from backend import json_generator, xml_generator, yaml_generator

ap = argparse.ArgumentParser()
ap.add_argument("filename", type=str,
                help="Name or path of the input NAME OF LANGUAGE file")

ap.add_argument("-o", "--output", type=str, default="config",
                help="Name of the output generated config file, without the extension")

ap.add_argument("-f", "--format", type=str, default="json", choices=['json', 'yaml', 'yml', 'xml'],
                help="Format of the generated file. Valid values are: json, yaml, xml")
arguments = vars(ap.parse_args())


FORMAT_FUNCTIONS = {
    'json': json_generator.generate,
    'yaml': yaml_generator.generate,
    'yml': yaml_generator.generate,
    'xml': xml_generator.generate
}


def main():
    metamodel = metamodel_from_file('model.tx')
    model = metamodel.model_from_file(arguments['filename'])

    mp = ModelParser(model)
    output = mp.parse_model()

    generate = FORMAT_FUNCTIONS[arguments['format']]

    # Remove the extension from the output filename, if the user added it despite the help message
    try:
        extension_index = arguments['output'].rindex('.')
        arguments['output'] = arguments['output'][0:extension_index]
    except ValueError:
        pass

    generate(output, arguments['output'])


if __name__ == '__main__':
    main()
