from netmiko import ConnectHandler
import time
import os

# IP addresses of the routers
ips = ["192.168.100.2", "192.168.100.3", "192.168.100.4", "192.168.100.5", 
       "192.168.100.6", "192.168.100.7", "192.168.100.8", "192.168.100.9"]

# SSH credentials
username = 'admin'
password = 'admin'

# Directory to save config files
save_dir = '/home/student/git/csci5840/cfgs'

# Make sure the directory exists
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# Function to get the running config and save it
def backup_running_config(ip):
    # Device connection details
    device = {
        'device_type': 'arista_eos',  # Adjust this based on your router type
        'ip': ip,
        'username': username,
        'password': password,
        'secret': password,  # Enable password (if needed)
    }

    # Connect to the device
    net_connect = ConnectHandler(**device)
    
    # Enter enable mode if required
    net_connect.enable()
    
    # Get the hostname
    hostname = net_connect.send_command('show running-config | include hostname').split()[1]
    
    # Get the running configuration
    running_config = net_connect.send_command('show running-config')
    
    # Save the running config to a file
    file_path = os.path.join(save_dir, f"{hostname}.cfg")
    with open(file_path, 'w') as config_file:
        config_file.write(running_config)
    
    print(f"Saved running config for {hostname} ({ip}) to {file_path}")

# Main loop to repeatedly backup configs every 5 seconds
while True:
    for ip in ips:
        try:
            backup_running_config(ip)
        except Exception as e:
            print(f"Failed to backup config for {ip}: {e}")
    
    # Wait for 5 seconds before the next iteration
    time.sleep(5)

