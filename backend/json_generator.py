import json


def generate(config, filename):
    filename = filename + '.json'
    with open(filename, 'w') as file:
        json.dump(config, file, indent=4)
