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

ap.add_argument("-c", "--check", type=str,
                help="Name of the manifest file against to check the program")
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

    # Remove the extension from the output filename if the user added it despite the help message
    try:
        extension_index = arguments['output'].rindex('.')
        arguments['output'] = arguments['output'][0:extension_index]
    except ValueError:
        pass

    if arguments['check']:
        # Check that the input program conforms to the manifest file

        # Load and read manifest file
        import json
        with open('manifest.json', 'r') as file:
            manifest = json.load(file)

        # Check activities
        if 'activities' in output:
            for activity in output['activities']:
                if activity not in manifest['activities']:
                    print(f"ERROR: Activity `{activity}` not valid according to manifest file. " +
                          f"Valid activities are: {list(manifest['activities'])}")
                    exit(1)

                for zone in output['activities'][activity]['zones']:
                    if zone not in manifest['zones']:
                        print(f"ERROR: Zone value`{zone}` for `{activity}` not valid according to manifest file. " +
                              f"Valid values are: {manifest['zones']}")
                        exit(1)

                for camera in output['activities'][activity]['cameras']:
                    if camera not in manifest['cameras']:
                        print(f"ERROR: Camera value`{camera}` for `{activity}` not valid according to manifest file. " +
                              f"Valid values are: {manifest['cameras']}")
                        exit(1)

        # Check targets
        if 'targets' in output:
            for target in output['targets']:
                if target not in manifest['targets'].keys():
                    print(f"ERROR: Target `{target}` not valid according to manifest file. " +
                          f"Valid targets are: {list(manifest['targets'].keys())}")
                    exit(1)

                # Check that properties and their values are valid
                for target_prop in output['targets'][target]['properties']:
                    if target_prop not in manifest['targets'][target]['properties']:
                        print(f"ERROR: Property `{target_prop}` not valid according to manifest file. " +
                              f"Valid properties for `{target}` are: {list(manifest['targets'][target]['properties'])}")
                        exit(1)

                for target_prop, value in output['targets'][target]['properties'].items():
                    if value not in manifest['targets'][target]['accepted_values'][target_prop]:
                        print(f"ERROR: Property value `{value}` for `{target}` `{target_prop}` not valid according to manifest file. " +
                              f"Valid values are: {list(manifest['targets'][target]['accepted_values'][target_prop])}")
                        exit(1)
                
                # Check zones
                if 'zones' in output['targets'][target]:
                    for zone in output['targets'][target]['zones']:
                        if zone not in manifest['zones']:
                            print(f"ERROR: Zone value`{zone}` for `{target}` not valid according to manifest file. " +
                                f"Valid values are: {manifest['zones']}")
                            exit(1)

        # Check actions
        # The actions are inside the conditions, so loop over them
        if 'conditions' in output:
            for condition in output['conditions']:
                action = condition['action']
                if action not in manifest['actions']:
                    print(f"ERROR: Action `{action}` not valid according to manifest file. " +
                          f"Valid actions are: {manifest['actions']}")
                    exit(1)

                expected_number_of_arguments = manifest['actions_arguments'][action]['arguments_number']
                if len(condition['action_args']) != expected_number_of_arguments:
                    print(f"ERROR: Number of arguments for action `{action}` not valid according to manifest file. " +
                          f"Expected {expected_number_of_arguments}, but got {len(condition['action_args'])}")
                    exit(1)
    else:
        generate(output, arguments['output'])


if __name__ == '__main__':
    main()
