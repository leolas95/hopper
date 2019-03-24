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

    def parse_variable_declaration(self, declaration):
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
            if type(zone).__name__ != 'ZoneDeclaration':
                if zone not in self.symtab:
                    print('ERROR: Undefined zone:', zone)
                    exit(1)

                # TODO: Uncomment when bug in grammar is fixed
                # if type(self.symtab[zone]).__name__ != 'ZoneDeclaration':
                #     print('ERROR: Incompatible types: expecting ZoneDeclaration, but found:', type(
                #         self.symtab[zone]).__name__)
                #     exit(1)

                value = self.symtab[zone]
            else:
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
        if type(declaration.target).__name__ != 'TargetDeclaration':
            if declaration.target not in self.symtab:
                print(f'ERROR: Undeclared identifier `{declaration.target}`')
                exit(1)
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

        if len(declaration.zones) > 0:
            self.targets[target.target_name]['zones'] = self.parse_zones(
                declaration.zones)

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
        if type(rhoperand).__name__ == 'str':
            # Check if it's declared
            if rhoperand not in self.counters and rhoperand not in self.symtab:
                print(f'ERROR: Undeclared identifier: {rhoperand}. ' +
                      'Right operand of boolean expression must be counter declared in ' +
                      'track object statement, or a variable that evaluate to a integer.')
                exit(1)

            # It's a variable. Get its value and checks that evaluates to an int
            if rhoperand in self.symtab:
                right_operand = self.symtab[rhoperand]
                if type(right_operand).__name__ != 'int':
                    print(f'ERROR: Variable `{rhoperand}` ' +
                          'in right side of boolean expression must evaluate to integer')
                    exit(1)
            # It's a counter, so just get its name
            else:
                index = self.counters.index(rhoperand)
                right_operand = self.counters[index]

        # It's just an int
        elif type(rhoperand).__name__ == 'int':
            right_operand = rhoperand

        self.targets_conditions.append({
            'condition': {
                'left_operand': left_operand,
                'operator': operator,
                'right_operand': right_operand
            },
            'action': declaration.action,
            'action_args': declaration.arguments
        })


    def parse_on_statement(self, declaration):
        self.activities_conditions.append({
            'activity': declaration.activity_name,
            'action': declaration.action,
            'action_args': declaration.arguments
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
        return {
            'targets': self.targets,
            'targets_conditions': self.targets_conditions,
            'activities_conditions': self.activities_conditions,
            'activities': self.activities
        }
