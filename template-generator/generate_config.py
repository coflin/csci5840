import yaml
from jinja2 import Environment, FileSystemLoader
import argparse

parser = argparse.ArgumentParser(description='Generate router configuration from YAML file.')
parser.add_argument('--config', required=True, help='Path to the YAML file.')

args = parser.parse_args()

device_type = args.config.split('_')[1].split('.')[0]

with open(f"generated-configs/{args.config}") as file:
    yaml_data = yaml.safe_load(file)


env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template(f'{device_type}.j2')

config_output = template.render(yaml_data)

#print(config_output)

