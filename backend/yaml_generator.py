import yaml

def generate(config, filename):
    with open(filename, 'w') as file:
        yaml.dump(config, file)