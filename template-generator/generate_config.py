import yaml
from jinja2 import Environment, FileSystemLoader
import argparse
import os

# Parse the command-line argument for the YAML file path
parser = argparse.ArgumentParser(description='Generate router configuration from YAML file.')
parser.add_argument('--config', required=True, help='Path to the YAML file.')

args = parser.parse_args()

# Extract device name and type from the filename
filename = os.path.splitext(args.config)[0]
device_name, device_type = filename.split('_', 1)

# Load YAML data
with open(f"{args.config}") as file:
    yaml_data = yaml.safe_load(file)

# Set up the Jinja2 environment and load the template based on device type
env = Environment(loader=FileSystemLoader('/home/student/git/csci5840/template-generator/templates'))
template = env.get_template(f'{device_type}.j2')

# Render the template with the YAML data
config_output = template.render(yaml_data)

# Save the configuration to a .cfg file in the generated-configs directory
output_file_path = f"{device_name}.cfg"
with open(output_file_path, 'w') as cfg_file:
    cfg_file.write(config_output)
    
print(f"Configuration saved to {output_file_path}")
