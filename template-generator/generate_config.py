import yaml
from jinja2 import Environment, FileSystemLoader
import argparse

parser = argparse.ArgumentParser(description='Generate router configuration from YAML file.')
parser.add_argument('--config', required=True, help='Path to the YAML file.')
parser.add_argument('--type', required=True, choices=['access', 'core', 'edge'], help='Type of the router (access, core, edge).')

args = parser.parse_args()

with open(args.config) as file:
    yaml_data = yaml.safe_load(file)

env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template(f'{args.type}.j2')

config_output = template.render(yaml_data)

print(config_output)

