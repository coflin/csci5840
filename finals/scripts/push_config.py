import argparse
from netmiko import ConnectHandler
from sshInfo import sshInfo
from loguru import logger

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Push a configuration file to a specific router.")
parser.add_argument("--router", required=True, help="Router name (e.g., r1, r2).")
parser.add_argument("--config_file", required=True, help="Path to the configuration file.")

args = parser.parse_args()

# Load SSH information
ssh_data = sshInfo()
if args.router not in ssh_data:
    logger.error(f"Router {args.router} not found in sshInfo data.")
    exit(1)

# Fetch device connection details
device_info = ssh_data[args.router]
device = {
    "device_type": device_info["Device_Type"],
    "host": device_info["IP"],
    "username": device_info["Username"],
    "password": device_info["Password"],
}

# Read the configuration file
try:
    with open(args.config_file, "r") as file:
        config_lines = file.read().splitlines()
except Exception as e:
    logger.error(f"Unable to read configuration file {args.config_file}: {e}")
    exit(1)

# Push the configuration to the router
try:
    logger.info(f"Connecting to {args.router} at {device['host']}...")
    connection = ConnectHandler(**device)
    logger.info(f"Connected to {args.router}")

    # Send the configuration
    connection.enable()
    output = connection.send_config_set(config_lines)
    logger.info(f"Configuration pushed successfully:\n{output}")

    # Save the configuration
    save_output = connection.save_config()
    logger.info(f"Configuration saved:\n{save_output}")

    connection.disconnect()
    logger.info(f"Disconnected from {args.router}")

except Exception as e:
    logger.error(f"Failed to push configuration to {args.router}: {e}")
    exit(1)
