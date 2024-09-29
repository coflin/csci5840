import yaml
from jinja2 import Environment, FileSystemLoader

# Load YAML files
with open('configs/r5.yaml') as file:
    r3_data = yaml.safe_load(file)

# Set up Jinja2 environment
env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('edge.j2')

# Render templates
r3_config = template.render(r3_data)

# Output the configurations
print(r3_config)

