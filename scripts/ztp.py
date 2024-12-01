import time
import os
import threading
from netmiko import ConnectHandler
from loguru import logger

# Device connection details
devices = {
    "R6": {
        "device_type": "arista_eos",
        "host": "192.51.0.2",
        "username": "admin",
        "password": "admin",
        "config_file": "/home/student/git/csci5840/ztp/r6_config.cfg"
    },
    "R7": {
        "device_type": "arista_eos",
        "host": "192.51.0.6",
        "username": "admin",
        "password": "admin",
        "config_file": "/home/student/git/csci5840/ztp/r7_config.cfg"
    },
    "R8": {
        "device_type": "arista_eos",
        "host": "172.20.20.20",  
        "username": "admin",
        "password": "admin",
        "config_file": "/home/student/git/csci5840/ztp/r8_config.cfg"
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
            if device_name == "R8":
                setup_r8(device_info)
            push_config(device_info, config_commands)
            break
        else:
            logger.info(f"{ip_address} ({device_name}) is not reachable. Retrying in 3 seconds...")
        time.sleep(3)

def setup_r8(device_info):
    """Assign IP to eth1 on R8 and check connectivity to 192.51.0.9."""
    connection = ConnectHandler(**{k: v for k, v in device_info.items() if k != "config_file"})
    connection.enable()
    try:
        # Assign IP to eth1
        connection.send_config_set([
            "interface Ethernet1",
            "no switchport",
            "ip address 192.51.0.10/30",
            "no shutdown"
        ])
    except Exception as e:
        logger.error(f"Error on {device_info['host']}: {e}")
    finally:
        connection.disconnect()

def push_config(device_info, config_commands):
    """Connect to the device and push configuration commands."""
    device_connection_info = {k: v for k, v in device_info.items() if k != "config_file"}
    connection = ConnectHandler(**device_connection_info)
    connection.enable()
    try:
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
