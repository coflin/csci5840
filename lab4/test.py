import yaml
from jinja2 import Environment, FileSystemLoader

# Load the YAML file
def load_yaml(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

# Render the selected template based on YAML content
def render_template(template_name, context):
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template(template_name)
    return template.render(context)

# Main logic to decide which template to call
def generate_config(yaml_file):
    # Load the YAML data
    device_data = load_yaml(yaml_file)
    print(device_data)
    full_config = ""

    # Render VLAN configuration
    full_config += render_template('vlan.j2', {'device': device_data})
    print(render_template('vlan.j2', {'device': device_data}))

    # Render DHCP if DHCP is enabled
    if any(vlan.get('dhcp_enabled') for vlan in device_data.get('vlans', [])):
        full_config += "\n" + render_template('dhcp.j2', {'device': device_data})

    # Render SNMP configuration
    full_config += "\n" + render_template('snmp.j2', {'device': device_data})

    # Render Interfaces configuration
    full_config += "\n" + render_template('interfaces.j2', {'device': device_data})

    # Render VLAN interfaces configuration
    full_config += "\n" + render_template('vlan_interfaces.j2', {'device': device_data})

    # Render OSPF if available
    if 'ospf' in device_data.get('routing_protocols', {}):
        full_config += "\n" + render_template('ospf.j2', {'device': device_data})

    # Render OSPFv3 if available
    if any(vlan.get('ospfv3') for vlan in device_data.get('vlans', [])):
        full_config += "\n" + render_template('ospfv3.j2', {'device': device_data})

    # Render RIP if available
    if 'rip' in device_data.get('routing_protocols', {}):
        full_config += "\n" + render_template('rip.j2', {'device': device_data})

    # Render static routes
    if device_data.get('routes', {}).get('static') or device_data.get('routes', {}).get('ipv6_static'):
        full_config += "\n" + render_template('static_routes.j2', {'device': device_data})

    # Render virtual router and general routing
    full_config += "\n" + render_template('virtual_router.j2', {'device': device_data})

    # Return the full configuration
    return full_config

# Example usage
if __name__ == "__main__":
    yaml_file_path = 'configs/r1.yaml'  # Path to your YAML file
    full_config = generate_config(yaml_file_path)
    print(full_config)

