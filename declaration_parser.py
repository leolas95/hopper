class DeclarationParser:
    # Symbol table to store the name and value of identifiers
    symtab = {}
    activities = []
    targets = {}
    conditions = []
    counters = []

    def __init__(self):
        pass

    # TODO: Split into functions for each declaration type
    def parse_declaration(self, declaration, declarationType):
        # When variable declaration is found, store it in the symtab
        if declarationType == 'VariableDeclaration':
            self.symtab[declaration.name] = declaration.value

        if declarationType == 'DetectActivity':
            for camera in declaration.camera:
                # If identifier is found, retrieve its entry from the symtab
                if type(camera).__name__ != 'CameraDeclaration':

                    if camera not in self.symtab:
                        print('ERROR: UNDEFINED VARIABLE:', camera)
                        exit(1)

                    if type(self.symtab[camera]).__name__ != 'CameraDeclaration':
                        print('ERROR: INCOMPATIBLE TYPE: expecting CameraDeclaration, but found:', type(
                            self.symtab[camera]).__name__)
                        exit(1)
            self.activities.append(declaration.activity_name)

        if declarationType == 'TrackObject':
            if type(declaration.target).__name__ != 'TargetDeclaration':
                # If not a declaration literal, is an ID
                target = self.symtab[declaration.target]
            else:
                # Target declaration literal
                target = declaration.target

            # Get properties of object to track
            target_properties = {}
            if target.properties is not None:
                for prop in target.properties.properties:
                    target_properties[prop.property_name] = prop.property_value

            self.targets[target.target_name] = {}
            if declaration.min > 0:
                self.targets[target.target_name]['min'] = declaration.min

            if declaration.max > 0:
                self.targets[target.target_name]['max'] = declaration.max

            if len(declaration.counter) > 0:
                self.targets[target.target_name]['counter'] = declaration.counter
                self.counters.append(declaration.counter)

            if target_properties is not None:
                self.targets[target.target_name]['properties'] = target_properties

        if declarationType == 'WhenStatement':
            # Find left and right operands, and operator
            # Check that the operands are declared variables, or counters
            if type(declaration.bool_expr.lhoperand).__name__ == 'str':
                if declaration.bool_expr.lhoperand not in self.counters and declaration.bool_expr.lhoperand not in self.symtab:
                    print('ERROR: UNDECLARED IDENTIFIER:',
                          declaration.bool_expr.lhoperand)
                    exit(1)

            lhoperand = declaration.bool_expr.lhoperand
            operator = declaration.bool_expr.operator

            if type(declaration.bool_expr.rhoperand).__name__ == 'str':
                if declaration.bool_expr.rhoperand not in self.counters and declaration.bool_expr.rhoperand not in self.symtab:
                    print('ERROR: UNDECLARED IDENTIFIER:',
                          declaration.bool_expr.rhoperand)
                    exit(1)
            rhoperand = declaration.bool_expr.rhoperand

            self.conditions.append({
                'condition': {
                    'left_operand': lhoperand,
                    'operator': operator,
                    'right_operand': rhoperand
                },
                'action': declaration.action,
                'action_args': declaration.arguments
            })

    def get_results(self):
        return {
            'targets': self.targets,
            'conditions': self.conditions
        }
        