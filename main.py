from backend import json_generator, yaml_generator, xml_generator
from textx import metamodel_from_file
import argparse

metamodel = metamodel_from_file('model.tx')
model = metamodel.model_from_file('test.dsl')

# Symbol table to store the name and value of identifiers
symtab = {}
activities = []
targets = {}
conditions = []
counters = []

ap = argparse.ArgumentParser()
ap.add_argument("-o", "--output", type=str, default="config",
                help="Name of the output generated config file, without the extension")
ap.add_argument("-f", "--format", type=str, default="json",
                help="Format of the generated file. Valid values are: json, yaml, xml")
arguments = vars(ap.parse_args())

def handle_declaration_type(declaration, declarationType):
    # When variable declaration is found, store it in the symtab
    if declarationType == 'VariableDeclaration':
        symtab[declaration.name] = declaration.value

    if declarationType == 'DetectActivity':
        for camera in declaration.camera:
            # If identifier is found, retrieve its entry from the symtab
            if type(camera).__name__ != 'CameraDeclaration':

                if camera not in symtab:
                    print('ERROR: UNDEFINED VARIABLE:', camera)
                    exit(1)

                if type(symtab[camera]).__name__ != 'CameraDeclaration':
                    print('ERROR: INCOMPATIBLE TYPE: expecting CameraDeclaration, but found:', type(
                        symtab[camera]).__name__)
                    exit(1)
        activities.append(declaration.activity_name)

    if declarationType == 'TrackObject':
        if type(declaration.target).__name__ != 'TargetDeclaration':
            # If not a declaration literal, is an ID
            target = symtab[declaration.target]
        else:
            # Target declaration literal
            target = declaration.target

        # Get properties of object to track
        target_properties = {}
        for prop in target.properties.properties:
            target_properties[prop.property_name] = prop.property_value

        targets[target.target_name] = {}
        if declaration.min > 0:
            targets[target.target_name]['min'] = declaration.min

        if declaration.max > 0:
            targets[target.target_name]['max'] = declaration.max

        if len(declaration.counter) > 0:
            targets[target.target_name]['counter'] = declaration.counter
            counters.append(declaration.counter)

        if target_properties is not None:
            targets[target.target_name]['properties'] = target_properties
        

    if declarationType == 'WhenStatement':
        # Find left and right operands, and operator
        # Check that the operands are declared variables, or counters
        if type(declaration.bool_expr.lhoperand).__name__ == 'str':
            if declaration.bool_expr.lhoperand not in counters and declaration.bool_expr.lhoperand not in symtab:
                print('ERROR: UNDECLARED IDENTIFIER:',
                      declaration.bool_expr.lhoperand)
                exit(1)

        lhoperand = declaration.bool_expr.lhoperand
        operator = declaration.bool_expr.operator

        if type(declaration.bool_expr.rhoperand).__name__ == 'str':
            if declaration.bool_expr.rhoperand not in counters and declaration.bool_expr.rhoperand not in symtab:
                print('ERROR: UNDECLARED IDENTIFIER:',
                      declaration.bool_expr.rhoperand)
                exit(1)
        rhoperand = declaration.bool_expr.rhoperand

        conditions.append({
            'condition': {
                'left_operand': lhoperand,
                'operator': operator,
                'right_operand': rhoperand
            },
            'action': declaration.action
        })


for decl in model.declarations:
    handle_declaration_type(decl, type(decl).__name__)

# print('Symbol table:', symtab, '\n')
# print('Activities:', activities, '\n')
# print('Targets:', targets, '\n')
# print('Conditions:', conditions)

output = {
    'targets': targets,
    'conditions': conditions
}

if arguments['format'] == 'json':
    json_generator.generate(output, arguments['output'])
elif arguments['format'] == 'yaml':
    yaml_generator.generate(output, arguments['output'])
else:
    xml_generator.generate(output, arguments['output'])
