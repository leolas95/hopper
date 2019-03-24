def check_activities(output, manifest):
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


def check_targets(output, manifest):
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


def check_conditions(output, manifest):
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


# Check that the input program conforms to the manifest file
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

    # Check actions
    # The actions are inside the conditions, so loop over them
    if 'conditions' in output:
        check_conditions(output, manifest)
