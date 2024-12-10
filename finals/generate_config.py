import yaml
from jinja2 import Environment, FileSystemLoader
import argparse
import os

# Parse the command-line argument for the YAML file path
parser = argparse.ArgumentParser(description='Generate router configuration from YAML file.')
parser.add_argument('--config', required=True, help='Path to the YAML file.')

args = parser.parse_args()

# Extract device name from the filename
filename = os.path.splitext(args.config)[0]
device_name = filename.split('_')[0]

# Load YAML data
with open(args.config) as file:
    yaml_data = yaml.safe_load(file)

# Set up the Jinja2 environment
env = Environment(loader=FileSystemLoader('/home/student/git/csci5840/finals/templates'))

# List of all configurations to process
config_sections = []

# Render interfaces if present
if yaml_data["device"]["interfaces"]:
    try:
        interfaces_template = env.get_template("interfaces.j2")
        config_sections.append(interfaces_template.render(yaml_data))
    except Exception as e:
        print("Error: interfaces.j2 template not found.")
        exit(1)

# Render OSPF configuration if present
if "ospf" in yaml_data["device"]["routing_protocols"]:
    try:
        ospf_template = env.get_template("ospf.j2")
        config_sections.append(ospf_template.render(yaml_data))
    except Exception as e:
        print("Error: ospf.j2 template not found.")
        exit(1)

# Render BGP configuration if present
if "bgp" in yaml_data["device"]["routing_protocols"]:
    try:
        bgp_template = env.get_template("bgp.j2")
        config_sections.append(bgp_template.render(yaml_data))
    except Exception as e:
        print("Error: bgp.j2 template not found.")
        exit(1)

# Render RIP configuration if present
if "rip" in yaml_data["device"]["routing_protocols"]:
    try:
        rip_template = env.get_template("rip.j2")
        config_sections.append(rip_template.render(yaml_data))
    except Exception as e:
        print("Error: rip.j2 template not found.")
        exit(1)

# Render static routes if present
if yaml_data["device"]["routes"]["static"] or yaml_data["device"]["routes"]["ipv6_static"]:
    try:
        static_routes_template = env.get_template("static_routes.j2")
        config_sections.append(static_routes_template.render(yaml_data))
    except Exception as e:
        print("Error: static_routes.j2 template not found.")
        exit(1)

# Combine all rendered sections into a single output
config_output = "\n\n".join(config_sections)

# Save the configuration to a .cfg file in the current directory
output_file_path = f"/home/student/git/csci5840/finals/generated-configs/{device_name}.cfg"
with open(output_file_path, 'w') as cfg_file:
    cfg_file.write(config_output)

print(f"Configuration saved to {output_file_path}")

