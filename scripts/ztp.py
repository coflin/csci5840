import time
import os
import threading
from netmiko import ConnectHandler
from loguru import logger

# Device connection details for R6 and R7
devices = {
    "R6": {
        "device_type": "arista_eos",
        "host": "192.51.0.2",  # IP for R6
        "username": "admin",
        "password": "admin",
        "config_file": "r6_config.cfg"  # Configuration file for R6
    },
    "R7": {
        "device_type": "arista_eos",
        "host": "192.51.0.6",  # IP for R7
        "username": "admin",
        "password": "admin",
        "config_file": "r7_config.cfg"  # Configuration file for R7
    }
}

def ping_until_reachable(device_name, device_info):
    """Ping the device's IP address until it is reachable, then push configuration."""
    ip_address = device_info["host"]
    config_file = device_info["config_file"]

    # Load configuration from the file
    with open(config_file) as config_file_obj:
        config_commands = config_file_obj.read().splitlines()

    while True:
        response = os.system(f"ping -c 1 {ip_address}")
        if response == 0:
            logger.info(f"{ip_address} ({device_name}) is reachable.")
            push_config(device_info, config_commands)
            break
        else:
            logger.info(f"{ip_address} ({device_name}) is not reachable. Retrying in 3 seconds...")
        time.sleep(3)

def push_config(device_info, config_commands):
    """Connect to the device and push configuration commands."""
    # Remove the `config_file` key before passing to ConnectHandler
    device_connection_info = {k: v for k, v in device_info.items() if k != "config_file"}
    connection = ConnectHandler(**device_connection_info)
    connection.enable()
    try:
        # Apply configuration from the file
        connection.send_config_set(config_commands)
        connection.save_config()  # Save the configuration to startup-config
        logger.success(f"Configuration applied successfully to {device_info['host']}.")
    except Exception as e:
        logger.error(f"Error on {device_info['host']}: {e}")
    finally:
        connection.disconnect()
        logger.info(f"Disconnected from {device_info['host']}.")

# Run the ping and configuration in parallel for each device
threads = []
for device_name, device_info in devices.items():
    thread = threading.Thread(target=ping_until_reachable, args=(device_name, device_info))
    thread.start()
    threads.append(thread)

# Wait for all threads to complete
for thread in threads:
    thread.join()

logger.success("Configuration process completed for all devices.")

