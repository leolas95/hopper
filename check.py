def check_activities(output, manifest):
    for activity in output['activities']:
        if activity not in manifest['activities']:
            print(f"ERROR: Activity `{activity}` not valid according to manifest file. " +
                  f"Valid activities are: {list(manifest['activities'])}")
            exit(1)

        if 'zones' in output['activities'][activity]:
            for zone in output['activities'][activity]['zones']:
                if zone not in manifest['zones']:
                    print(f"ERROR: Zone value`{zone}` for `{activity}` not valid according to manifest file. " +
                          f"Valid values are: {manifest['zones']}")
                    exit(1)

        if 'cameras' in output['activities'][activity]:
            for camera_type, values in output['activities'][activity]['cameras'].items():
                for value in values:
                    if camera_type == 'number' and value not in manifest['cameras_numbers']:
                        print(f"ERROR: Camera value `{value}` for `{activity}` not valid according to manifest file. " +
                              f"Valid values are: {manifest['cameras_numbers']}")
                        exit(1)

                    if camera_type == 'ip' and value not in manifest['cameras_ips']:
                        print(f"ERROR: Camera value `{value}` for `{activity}` not valid according to manifest file. " +
                              f"Valid values are: {manifest['cameras_ips']}")
                        exit(1)

                    if camera_type == 'name' and value not in manifest['cameras_names']:
                        print(f"ERROR: Camera value `{value}` for `{activity}` not valid according to manifest file. " +
                              f"Valid values are: {manifest['cameras_names']}")
                        exit(1)


def check_targets(output, manifest):
    for target in output['targets']:
        if target not in manifest['targets'].keys():
            print(f"ERROR: Target `{target}` not valid according to manifest file. " +
                  f"Valid targets are: {list(manifest['targets'].keys())}")
            exit(1)

        # Check that properties and their values are valid
        if 'properties' in output['targets'][target]:
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

        # Check cameras
        if 'cameras' in output['targets'][target]:
            for camera_type, values in output['targets'][target]['cameras'].items():
                for value in values:
                    if camera_type == 'number' and value not in manifest['cameras_numbers']:
                        print(f"ERROR: Camera value `{value}` for `{target}` not valid according to manifest file. " +
                              f"Valid values are: {manifest['cameras_numbers']}")
                        exit(1)

                    if camera_type == 'ip' and value not in manifest['cameras_ips']:
                        print(f"ERROR: Camera value `{value}` for `{target}` not valid according to manifest file. " +
                              f"Valid values are: {manifest['cameras_ips']}")
                        exit(1)

                    if camera_type == 'name' and value not in manifest['cameras_names']:
                        print(f"ERROR: Camera value `{value}` for `{target}` not valid according to manifest file. " +
                              f"Valid values are: {manifest['cameras_names']}")
                        exit(1)


def check_conditions(output, manifest, keyname):
    for condition in output[keyname]:
        action = condition['action']
        if action not in manifest['actions']:
            print(f"ERROR: Action `{action}` not valid according to manifest file. " +
                  f"Valid actions are: {manifest['actions']}")
            exit(1)

        expected_number_of_arguments = manifest['actions_arguments'][action]['arguments_number']
        if len(condition['action_arguments']) != expected_number_of_arguments:
            print(f"ERROR: Number of arguments for action `{action}` not valid according to manifest file. " +
                  f"Expected {expected_number_of_arguments}, but got {len(condition['action_arguments'])}")
            exit(1)


def check_activities_conditions(output, manifest):
    check_conditions(output, manifest, 'activities_conditions')


def check_targets_conditions(output, manifest):
    check_conditions(output, manifest, 'targets_conditions')

# Checks that the input program conforms to the manifest file
def check(output, manifest_file):
    # Load and read manifest file
    import json
    with open(manifest_file, 'r') as file:
        manifest = json.load(file)

    # Check activities
    if 'activities' in output:
        check_activities(output, manifest)

    # Check targets
    if 'targets' in output:
        check_targets(output, manifest)

    # Check activities conditions
    if 'activities_conditions' in output:
        check_activities_conditions(output, manifest)

    # Check targets conditions
    if 'targets_conditions' in output:
        check_activities_conditions(output, manifest)
