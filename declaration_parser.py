class DeclarationParser:
    # Symbol table to store the name and value of identifiers
    symtab = {}
    activities = []
    targets = {}
    conditions = []
    counters = []

    def __init__(self):
        pass

    def parse_variable_declaration(self, declaration):
        self.symtab[declaration.name] = declaration.value

    def parse_detect_activity(self, declaration):
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

    def parse_track_object(self, declaration):
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

    def parse_when_statement(self, declaration):
        # Find left and right operands, and operator
        # Check that the operands are declared variables, or counters
        if declaration.bool_expr.lhoperand not in self.counters:
            print(f'ERROR: Undeclared identifier: {declaration.bool_expr.lhoperand}. ' +
                  'Left operand of boolean expression must be counter declared in ' +
                  'track object statement')
            exit(1)

        lhoperand = declaration.bool_expr.lhoperand
        operator = declaration.bool_expr.operator

        # If the right operand is an identifier, it could be either a (int) variable or a counter
        if type(declaration.bool_expr.rhoperand).__name__ == 'str':
            # Check if it's declared
            if declaration.bool_expr.rhoperand not in self.counters and declaration.bool_expr.rhoperand not in self.symtab:
                print(f'ERROR: Undeclared identifier: {declaration.bool_expr.rhoperand}. ' +
                      'Right operand of boolean expression must be counter declared in ' +
                      'track object statement, or a variable that evaluate to a integer.')
                exit(1)

            # It's a variable. Get its value and checks that evaluates to an int
            if declaration.bool_expr.rhoperand in self.symtab:
                rhoperand = self.symtab[declaration.bool_expr.rhoperand]
                if type(rhoperand).__name__ != 'int':
                    print(f'ERROR: Variable `{declaration.bool_expr.rhoperand}` ' +
                          'in right side of boolean expression must evaluate to integer')
                    exit(1)
            # It's a counter, so just get its name
            else:
                index = self.counters.index(declaration.bool_expr.rhoperand)
                rhoperand = self.counters[index]

        # It's just an int
        elif type(declaration.bool_expr.rhoperand).__name__ == 'int':
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

    # TODO: Split into functions for each declaration type
    def parse_declaration(self, declaration, declaration_type):
        # When variable declaration is found, store it in the symtab
        if declaration_type == 'VariableDeclaration':
            self.parse_variable_declaration(declaration)

        if declaration_type == 'DetectActivity':
            self.parse_detect_activity(declaration)

        if declaration_type == 'TrackObject':
            self.parse_track_object(declaration)

        if declaration_type == 'WhenStatement':
            self.parse_when_statement(declaration)

    def get_results(self):
        return {
            'targets': self.targets,
            'conditions': self.conditions
        }
