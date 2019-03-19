from textx import metamodel_from_file

metamodel = metamodel_from_file('model.tx')
model = metamodel.model_from_file('test.dsl')

# Symbol table to store the name and value of identifiers
symtab = {}
activities = []
targets = []


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
            target = symtab[declaration.target]
        else:
            target = declaration.target

        # Get properties of object to track
        target_properties = {}
        for prop in target.properties.properties:
            target_properties[prop.property_name] = prop.property_value

        targets.append({target.target_name: {'properties': target_properties}})

    if declarationType == 'WhenStatement':
        # Verifica que si los operandos son identificadores, esten declarados y sean de tipos compatibles
        # If operands are identifiers, check that they are defined
        if type(declaration.bool_expr.lhoperand).__name__ == 'str':
            # Verifica que este declarado
            if declaration.bool_expr.lhoperand not in symtab:
                print('ERROR: UNDEFINED VARIABLE:',
                      declaration.bool_expr.lhoperand)
                exit(1)

            # TODO: Check that they are of compatible types
            if type(symtab[declaration.bool_expr.lhoperand]).__name__ != 'int':
                print('TODO: Check compatible types')

        if type(declaration.bool_expr.rhoperand).__name__ == 'str':
            if declaration.bool_expr.rhoperand not in symtab:
                print('ERROR: UNDEFINED VARIABLE:',
                      declaration.bool_expr.rhoperand)
                exit(1)


for declaration in model.declarations:
    handle_declaration_type(declaration, type(declaration).__name__)

print('Symbol table:', symtab, '\n')
print('Activities:', activities, '\n')
print('Targets:', targets, '\n')
