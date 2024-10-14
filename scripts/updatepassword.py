import csv
from loguru import logger
from netmiko import ConnectHandler
import secrets
from sshInfo import sshInfo
import time

def generatePassword():
    """Generate a random password."""
    return secrets.token_urlsafe(4)

def updatePassword(net_connect, ip, password):
    """Send the command to update the password on the router."""
    try:
        net_connect.enable()
        net_connect.send_config_set([f"username admin secret 0 {password}"])
        logger.success(f"Updated password on {ip}")
        return True

    except Exception as e:
        logger.error(f"Unable to configure password: {e}")
        return False

def updatePasswordFile(file_path, ip, new_password):
    """Update the password for the given IP in the CSV file."""
    updated_rows = []

    # Read the existing CSV content
    with open(file_path, "r") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames  # Store the headers

        # Iterate through each row and update the matching IP entry
        for row in reader:
            if row["IP"] == ip:
                row["Password"] = new_password  # Update the password
                logger.success(f"Password updated for {ip} in {file_path}.")
            updated_rows.append(row)

    # Write the updated content back to the CSV
    with open(file_path, "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()  # Write the header first
        writer.writerows(updated_rows)  # Write all rows

def connectRouter(eos, hostname):
    """Connect to a router and return the connection object."""
    try:
        net_connect = ConnectHandler(**eos)
        logger.info(f"Successfully connected to {eos['ip']} as {eos['username']}")
        return net_connect
    except Exception as e:
        logger.error(f"Unable to connect to {eos['ip']} as {eos['username']}. Check config and try again: {e}")

def main():
    while True:
        credentials = sshInfo()  # Load router credentials from CSV

        for hostname, info in credentials.items():
            eos = {
                "device_type": info["Device_Type"],
                "ip": info["IP"],
                "username": info["Username"],
                "password": info["Password"]
            }

            # Connect to the router
            net_connect = connectRouter(eos, info["IP"])

            # Generate a new password
            new_password = generatePassword()

            # Update the router password if connected successfully
            if net_connect and updatePassword(net_connect, info["IP"], new_password):
                updatePasswordFile('/home/student/git/csci5840/scripts/sshInfo.csv', info["IP"], new_password)
        
        logger.info("\nWaiting 1 minute before the next update...\n")
        time.sleep(60)  # Wait for 10 seconds before the next iteration

if __name__ == "__main__":
    main()
