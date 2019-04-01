import argparse
import importlib.util

from textx import metamodel_from_file

from parsers.model_parser import ModelParser

ap = argparse.ArgumentParser()
ap.add_argument("filename", type=str,
                help="Name or path of the input NAME OF LANGUAGE file")

ap.add_argument("-o", "--output", type=str, default="config",
                help="Name of the output generated config file, without the extension")

ap.add_argument("-b", "--backend", type=str, required=True,
                help="Name of the backend to use to generate the config file")

ap.add_argument("-f", "--format", type=str, required=True,
                help="Format of the generated file (like json, yaml, xml, etc.)")

ap.add_argument("-c", "--check", type=str, nargs='?', const='manifest.json',
                help="Name of the manifest file against to check the program")

arguments = vars(ap.parse_args())


def backend_exists(backend):
    return importlib.util.find_spec(backend)


def generator_exists(generator):
    return importlib.util.find_spec(generator)


def main():
    backend_name = f"backend.{arguments['backend']}"
    if not backend_exists(backend_name):
        print(f"ERROR: Specified backend `{arguments['backend']}` does not exists")
        exit(1)

    generator_name = f"{backend_name}.generators.{arguments['format']}_generator"
    if not generator_exists(generator_name):
        print(f"ERROR: Specified generator `{generator_name}` does not exists")
        exit(1)

    generator_module = importlib.import_module(generator_name)

    # Checks that the generator has the generate function
    if not hasattr(generator_module, 'generate'):
        print(
            f'Module {generator_name} does not have required `generate` function')
        exit(1)

    # Generator is OK, we can continue processing the program

    metamodel = metamodel_from_file('model.tx')

    from textx.exceptions import TextXSyntaxError

    try:
        model = metamodel.model_from_file(arguments['filename'])
    except TextXSyntaxError as err:
        print(f'ERROR: line {err.line}, column {err.col}: {err.message}')
        exit(1)

    mp = ModelParser(model)
    output = mp.parse_model()

    # Remove the extension from the output filename if the user added it despite the help message
    try:
        extension_index = arguments['output'].rindex('.')
        arguments['output'] = arguments['output'][0:extension_index]
    except ValueError:
        pass

    if arguments['check']:
        from check import check
        check(output, arguments['check'])
        print('Everything OK')
    else:
        generator_module.generate(output, arguments['output'])


if __name__ == '__main__':
    main()
