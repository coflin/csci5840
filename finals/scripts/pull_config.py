import os
from sshInfo import sshInfo
from netmiko import ConnectHandler
from loguru import logger

def pull_configs():
    # Load device information from sshInfo
    devices = sshInfo()

    # Ensure the golden-configs directory exists
    config_dir = "golden-configs"
    os.makedirs(config_dir, exist_ok=True)

    # Iterate through devices and pull configurations
    for device_name, device_info in devices.items():
        logger.info(f"Pulling configuration for {device_name}...")

        # Prepare device connection parameters
        device_params = {
            "device_type": device_info["Device_Type"],
            "host": device_info["IP"],
            "username": device_info["Username"],
            "password": device_info["Password"],
        }

        try:
            # Connect to the device
            connection = ConnectHandler(**device_params)
            logger.info(f"Connected to {device_name} ({device_info['IP']})")

            # Get the running configuration
            connection.enable()
            running_config = connection.send_command("show running-config")

            # Save the configuration to a file
            config_file = os.path.join(config_dir, f"{device_name}.cfg")
            with open(config_file, "w") as file:
                file.write(running_config)

            logger.info(f"Configuration saved for {device_name} in {config_file}")

            # Disconnect from the device
            connection.disconnect()
        except Exception as e:
            logger.error(f"Failed to pull configuration for {device_name}: {e}")

if __name__ == "__main__":
    pull_configs()

