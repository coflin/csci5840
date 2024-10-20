import yaml
from jinja2 import Environment, FileSystemLoader
import argparse

# Set up argparse for command-line arguments with --config and --type flags
parser = argparse.ArgumentParser(description='Generate router configuration from YAML file.')
parser.add_argument('--config', required=True, help='Path to the YAML file.')
parser.add_argument('--type', required=True, choices=['access', 'core', 'edge'], help='Type of the router (access, core, edge).')

# Parse the arguments
args = parser.parse_args()

# Load YAML file based on the user input
with open(args.config) as file:
    yaml_data = yaml.safe_load(file)

# Set up Jinja2 environment and select template based on router type
env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template(f'{args.type}.j2')  # Dynamically select template (access.j2, core.j2, edge.j2)

# Render the template with the provided YAML data
config_output = template.render(yaml_data)

# Output the configuration
print(config_output)

