from enum import Enum
class Statements(Enum):
    DETECT_ACTIVITY = 'DetectActivityStatement'
    TRACK_OBJECT = 'TrackObjectStatement'
    ON_STATEMENT = 'OnStatement'
    VARIABLE_DEFINITION = 'VariableDefinition'
    WHEN_STATEMENT = 'WhenStatement'
    CAMERA_DECLARATION = 'CameraDeclaration'
    IP_CAMERA = 'IpCamera'
    NAMED_CAMERA = 'NamedCamera'
    NUMBERED_CAMERA = 'NumberedCamera'
    ZONE_VARIABLE_DECLARATION = 'ZoneVariableDeclaration'
    TARGET_VARIABLE_DECLARATION = 'TargetVariableDeclaration'

def typename(x):
    return type(x).__name__


def is_identifier(x):
    return typename(x) == 'str'

class DeclarationParser:

    def __init__(self, model):
        self.symtab = {}
        self.activities = {}
        self.targets = {}
        self.targets_conditions = []
        self.activities_conditions = []
        self.counters = []

        # We only need the model so we can use the _tx_parser.pos_to_linecol
        # method for error handling
        self.model = model
        self.filename = self.model._tx_filename

    def line_col(self, declaration):
        return self.model._tx_parser.pos_to_linecol(declaration._tx_position)

    def error_undefined_identifier(self, declaration, identifier, friendly_name, explanation=None):
        line, col = self.line_col(declaration)
        print(f'Error: {self.filename}: line {line}, column {col}: Undefined ' +
              f'{friendly_name} identifier `{identifier}`.')

        if explanation:
            print(explanation)
        exit(1)

    def error_incompatible_types(self, declaration, expected, actual):
        line, col = self.line_col(declaration)
        print(
            f'ERROR: {self.filename}: line {line}, column {col}: Incompatible types.' +
            f'Expecting {expected}, but found {actual}')
        exit(1)

    def parse_variable_declaration(self, declaration):
        self.symtab[declaration.name] = declaration.value

    def parse_cameras(self, declaration, cameras):
        result = {}
        for camera in cameras:
            # If not a declaration literal, is an ID
            if is_identifier(camera):
                if camera not in self.symtab:
                    self.error_undefined_identifier(
                        declaration, camera, 'camera')

                cam = self.symtab[camera]
                # Check that the type is a camera
                if typename(cam) != Statements.CAMERA_DECLARATION.value:
                    self.error_incompatible_types(declaration,
                                                  expected=Statements.CAMERA_DECLARATION.value,
                                                  actual=typename(cam))
            else:
                cam = camera

            cam_typename = typename(cam.type)
            if cam_typename == Statements.IP_CAMERA.value:
                if 'ip' not in result:
                    result['ip'] = []
                result['ip'].append(cam.type.ip.ip)

            elif cam_typename == Statements.NAMED_CAMERA.value:
                if 'name' not in result:
                    result['name'] = []
                result['name'].append(cam.type.name)

            elif cam_typename == Statements.NUMBERED_CAMERA.value:
                if 'number' not in result:
                    result['number'] = []
                result['number'].append(cam.type.number)

        return result

    def parse_zones(self, declaration, zones):
        result = []
        for zone in zones:
            # If it's an identifier, look it up in the symbol table
            if is_identifier(zone):
                # Check that it's in symbol table
                if zone not in self.symtab:
                    self.error_undefined_identifier(declaration, zone, 'zone')

                value = self.symtab[zone]
                # Check that it has compatible type
                if typename(value) != Statements.ZONE_VARIABLE_DECLARATION.value:
                    self.error_incompatible_types(declaration,
                                                  expected=Statements.ZONE_VARIABLE_DECLARATION.value,
                                                  actual=typename(value))

                value = value.zone
            else:
                # It's a zone literal, so just gets its value
                value = zone.zone

            result.append(value)

        return result

    def parse_detect_activity(self, declaration):
        self.activities[declaration.activity_name] = {}

        if declaration.cameras:
            self.activities[declaration.activity_name]['cameras'] = self.parse_cameras(
                declaration, declaration.cameras)

        if declaration.zones:
            self.activities[declaration.activity_name]['zones'] = self.parse_zones(
                declaration, declaration.zones)

    def parse_track_object(self, declaration):
        # If it's an identifier, look it up in the symbol table
        if is_identifier(declaration.target):
            # Check that it's in symbol table
            if declaration.target not in self.symtab:
                self.error_undefined_identifier(
                    declaration, declaration.target, 'target')

            target = self.symtab[declaration.target]

            # Check that it has compatible type
            if typename(target) != Statements.TARGET_VARIABLE_DECLARATION.value:
                self.error_incompatible_types(declaration,
                                              expected=Statements.TARGET_VARIABLE_DECLARATION.value,
                                              actual=typename(target))

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

        if declaration.counter:
            self.targets[target.target_name]['counter'] = declaration.counter
            self.counters.append(declaration.counter)

        if any(target_properties):
            self.targets[target.target_name]['properties'] = target_properties

        if declaration.zones:
            self.targets[target.target_name]['zones'] = self.parse_zones(
                declaration, declaration.zones)

        if declaration.cameras:
            self.targets[target.target_name]['cameras'] = self.parse_cameras(
                declaration, declaration.cameras)

    def parse_when_statement(self, declaration):
        # Find left and right operands, and operator
        # Check that the operands are declared variables, or counters
        lhoperand = declaration.bool_expr.lhoperand
        if lhoperand not in self.counters:
            self.error_undefined_identifier(declaration,
                                            lhoperand,
                                            'counter',
                                            'Left operand of boolean expression' +
                                            'must be counter declared in ' +
                                            'track object statement')

        left_operand = declaration.bool_expr.lhoperand

        operator = declaration.bool_expr.operator

        # If the right operand is an identifier, it could be either a (int) variable or a counter
        rhoperand = declaration.bool_expr.rhoperand
        if is_identifier(rhoperand):
            # Check if it's declared
            if rhoperand not in self.counters and rhoperand not in self.symtab:
                self.error_undefined_identifier(declaration,
                                                rhoperand,
                                                'boolean right operand',
                                                'Right operand of boolean' +
                                                'expression must be counter declared in ' +
                                                'track object statement, or a' +
                                                'variable that evaluates to an integer.')

            # It's a variable. Get its value and checks that evaluates to an int
            if rhoperand in self.symtab:
                right_operand = self.symtab[rhoperand]
                if typename(right_operand) != 'int':
                    filename = self.filename
                    line, col = self.line_col(declaration)
                    print(f'ERROR: {filename}: line {line}, col {col}: Variable `{rhoperand}` ' +
                          'in right side of boolean expression must evaluate to an integer')
                    exit(1)
            # It's a counter, so just get its name
            else:
                index = self.counters.index(rhoperand)
                right_operand = self.counters[index]

        # It's just an int
        elif typename(rhoperand) == 'int':
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
        if declaration_type == Statements.VARIABLE_DEFINITION.value:
            self.parse_variable_declaration(declaration)

        if declaration_type == Statements.DETECT_ACTIVITY.value:
            self.parse_detect_activity(declaration)

        if declaration_type == Statements.TRACK_OBJECT.value:
            self.parse_track_object(declaration)

        if declaration_type == Statements.WHEN_STATEMENT.value:
            self.parse_when_statement(declaration)

        if declaration_type == Statements.ON_STATEMENT.value:
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
