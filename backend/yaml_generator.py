import yaml

def generate(config, filename):
    filename = filename + '.yaml'
    with open(filename, 'w') as file:
        yaml.dump(config, file)