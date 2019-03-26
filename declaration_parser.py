class DeclarationParser:
    # Symbol table to store the name and value of identifiers
    symtab = {}
    activities = {}
    targets = {}
    targets_conditions = []
    activities_conditions = []
    counters = []

    def __init__(self):
        pass

    def typename(self, x):
        return type(x).__name__

    def is_identifier(self, x):
        return self.typename(x) == 'str'

    def parse_variable_declaration(self, declaration):
        print('storing', declaration.value)
        self.symtab[declaration.name] = declaration.value

    def parse_cameras(self, cameras):
        result = {}
        for camera in cameras:
            # If not a declaration literal, is an ID
            if type(camera).__name__ != 'CameraDeclaration':
                if camera not in self.symtab:
                    print('ERROR: Undefined camera:', camera)
                    exit(1)

                # Check that the type is a camera
                if type(self.symtab[camera]).__name__ != 'CameraDeclaration':
                    print('ERROR: Incompatible types: expecting CameraDeclaration, but found:', type(
                        self.symtab[camera]).__name__)
                    exit(1)

                cam = self.symtab[camera]
            else:
                cam = camera

            if type(cam.type).__name__ == 'IpCamera':
                if 'ip' not in result:
                    result['ip'] = []
                result['ip'].append(cam.type.ip.ip)

            elif type(cam.type).__name__ == 'NamedCamera':
                if 'name' not in result:
                    result['name'] = []
                result['name'].append(cam.type.name)

            elif type(cam.type).__name__ == 'NumberedCamera':
                if 'number' not in result:
                    result['number'] = []
                result['number'].append(cam.type.number)

        return result

    def parse_zones(self, zones):
        result = []
        for zone in zones:
            # If it's an identifier, look it up in the symbol table
            if self.is_identifier(zone):

                # Check that it's in symbol table
                if zone not in self.symtab:
                    print('ERROR: Undefined zone:', zone)
                    exit(1)

                value = self.symtab[zone]
                # Check that it has compatible type
                if self.typename(value) != 'ZoneVariableDeclaration':
                    print('ERROR: Incompatible types: expecting ZoneVariableDeclaration, but found:', self.typename(self.symtab[zone]))
                    exit(1)
                value = value.zone
            else:
                # It's a zone literal, so just gets its value
                value = zone.zone

            result.append(value)

        return result

    def parse_detect_activity(self, declaration):
        self.activities[declaration.activity_name] = {}

        if len(declaration.cameras) > 0:
            self.activities[declaration.activity_name]['cameras'] = self.parse_cameras(
                declaration.cameras)

        if len(declaration.zones) > 0:
            self.activities[declaration.activity_name]['zones'] = self.parse_zones(
                declaration.zones)

    def parse_track_object(self, declaration):
        # If it's an identifier, look it up in the symbol table
        if self.is_identifier(declaration.target):
            # Check that it's in symbol table
            if declaration.target not in self.symtab:
                print(f'ERROR: Undeclared identifier `{declaration.target}`')
                exit(1)
            
            target = self.symtab[declaration.target]

            # Check that it has compatible type
            if self.typename(target) != 'TargetVariableDeclaration':
                print('ERROR: Incompatible types: expecting TargetVariableDeclaration, but found:', self.typename(target))
                exit(1)
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

        if any(target_properties):
            self.targets[target.target_name]['properties'] = target_properties

        if len(declaration.zones) > 0:
            self.targets[target.target_name]['zones'] = self.parse_zones(
                declaration.zones)
        
        if len(declaration.cameras) > 0:
            self.targets[target.target_name]['cameras'] = self.parse_cameras(declaration.cameras)

    def parse_when_statement(self, declaration):
        # Find left and right operands, and operator
        # Check that the operands are declared variables, or counters
        lhoperand = declaration.bool_expr.lhoperand
        if lhoperand not in self.counters:
            print(f'ERROR: Undeclared counter: {lhoperand}. ' +
                  'Left operand of boolean expression must be counter declared in ' +
                  'track object statement')
            exit(1)

        left_operand = declaration.bool_expr.lhoperand

        operator = declaration.bool_expr.operator

        # If the right operand is an identifier, it could be either a (int) variable or a counter
        rhoperand = declaration.bool_expr.rhoperand
        if self.is_identifier(rhoperand):
            # Check if it's declared
            if rhoperand not in self.counters and rhoperand not in self.symtab:
                print(f'ERROR: Undeclared identifier: {rhoperand}. ' +
                      'Right operand of boolean expression must be counter declared in ' +
                      'track object statement, or a variable that evaluate to a integer.')
                exit(1)

            # It's a variable. Get its value and checks that evaluates to an int
            if rhoperand in self.symtab:
                right_operand = self.symtab[rhoperand]
                if self.typename(right_operand) != 'int':
                    print(f'ERROR: Variable `{rhoperand}` ' +
                          'in right side of boolean expression must evaluate to integer')
                    exit(1)
            # It's a counter, so just get its name
            else:
                index = self.counters.index(rhoperand)
                right_operand = self.counters[index]

        # It's just an int
        elif self.typename(rhoperand) == 'int':
            right_operand = rhoperand

        self.targets_conditions.append({
            'condition': {
                'left_operand': left_operand,
                'operator': operator,
                'right_operand': right_operand
            },
            'action': declaration.action,
            'action_arguments': declaration.arguments
        })

    def parse_on_statement(self, declaration):
        self.activities_conditions.append({
            'activity': declaration.activity_name,
            'action': declaration.action,
            'action_arguments': declaration.arguments
        })
    
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

        if declaration_type == 'OnStatement':
            self.parse_on_statement(declaration)

    def get_results(self):
        result = {}
        if any(self.targets):
            result['targets'] = self.targets

        if any(self.targets_conditions):
            result['targets_conditions'] = self.targets_conditions

        if any(self.activities_conditions):
            result['activities_conditions'] = self.activities_conditions

        if any(self.activities):
            result['activities'] = self.activities
        
        return result
