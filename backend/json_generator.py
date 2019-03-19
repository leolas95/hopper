import json

def generate(config, filename):
    with open(filename, 'w') as file:
        json.dump(config, file, indent=4)