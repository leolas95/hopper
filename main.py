from textx import metamodel_from_file
from pprint import pprint

metamodel = metamodel_from_file('model.tx')
model = metamodel.model_from_file('test.dsl')

# Symbol table to store the name and value of identifiers
symtab = {}
activities = []
targets = {}
conditions = []
counters = []

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

        targets[target.target_name] = {
            'min': declaration.min,
            'max': declaration.max,
            'counter': declaration.counter,
            'properties': target_properties
        }
        counters.append(declaration.counter)

    if declarationType == 'WhenStatement':
        # Find left and right operands, and operator
        # Check that the operands are declared variables, or counters
        if type(declaration.bool_expr.lhoperand).__name__ == 'str':
            if declaration.bool_expr.lhoperand not in counters and declaration.bool_expr.lhoperand not in symtab:
                print('ERROR: UNDECLARED IDENTIFIER:', declaration.bool_expr.lhoperand)
                exit(1)

        lhoperand = declaration.bool_expr.lhoperand
        operator = declaration.bool_expr.operator

        if type(declaration.bool_expr.rhoperand).__name__ == 'str':
            if declaration.bool_expr.rhoperand not in counters and declaration.bool_expr.rhoperand not in symtab:
                print('ERROR: UNDECLARED IDENTIFIER:', declaration.bool_expr.rhoperand)
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

pprint(output)