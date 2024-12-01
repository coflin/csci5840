from netmiko import ConnectHandler
from sshInfo import sshInfo
from loguru import logger
import os
import difflib

def normalize_config(config):
    """
    Normalize configuration by stripping trailing spaces and standardizing newlines.
    """
    return [line.strip() for line in config.splitlines() if line.strip()]

def parse_contextual_commands(diff_lines):
    """
    Parse the diff lines to generate contextual negation commands.
    Ensures commands are applied under the appropriate configuration context.
    """
    contextual_commands = []
    current_context = None

    for line in diff_lines:
        if line.startswith("+") and not line.startswith("+++"):
            command = line[1:].strip()  # Remove '+' and strip whitespace
            if command and not command.startswith("!"):  # Ignore comments or empty lines
                if current_context:
                    contextual_commands.append((current_context, f"no {command}"))
                else:
                    contextual_commands.append((None, f"no {command}"))

        elif not line.startswith("-") and not line.startswith("@") and not line.startswith("+"):
            # Detect context (e.g., interface, router config modes)
            stripped_line = line.strip()
            if stripped_line.startswith("interface") or stripped_line.startswith("router"):
                current_context = stripped_line

    return contextual_commands

def compare_configs(net_connect, device_name, current_config, golden_config_path):
    """
    Compare the current configuration with the golden configuration.
    If differences are found, revert extra commands in the correct context
    and apply the golden configuration.
    """
    try:
        # Load golden configuration
        if not os.path.exists(golden_config_path):
            logger.warning(f"No golden configuration found for {device_name}. Skipping comparison.")
            return None

        with open(golden_config_path, "r") as golden_file:
            golden_config = golden_file.read()

        # Normalize configurations
        normalized_current = normalize_config(current_config)
        normalized_golden = normalize_config(golden_config)

        # Compare configurations
        diff = list(difflib.unified_diff(
            normalized_golden,
            normalized_current,
            fromfile="Golden Config",
            tofile="Current Config",
            lineterm=""
        ))

        # Collect differences
        differences = "\n".join(diff)
        if differences:
            logger.warning(f"Differences found for {device_name}:\n{differences}")
            diff_file = f"diffs/{device_name}_diff.txt"
            with open(diff_file, "w") as file:
                file.write(differences)

            # Parse diff to generate contextual negation commands
            contextual_commands = parse_contextual_commands(diff)

            if contextual_commands:
                net_connect.enable()

                # Process each contextual command
                for context, command in contextual_commands:
                    if context:
                        logger.info(f"Entering context: {context}")
                        # Combine context and command into a single config set
                        net_connect.send_config_set([context, command])
                    else:
                        # Handle global commands
                        logger.info(f"Applying global command: {command}")
                        net_connect.send_config_set([command])


            # Apply golden configuration to ensure compliance
            net_connect.send_config_from_file(golden_config_path)
            logger.info("Reverted the config back to golden config")

        else:
            logger.info(f"No differences found for {device_name}. Configuration is compliant.")

    except Exception as e:
        logger.error(f"Error comparing configs for {device_name}: {e}")

def main():
    # Load SSH data
    logger.info("Loading SSH device information...")
    ssh_data = sshInfo()

    # Validate SSH data
    if not ssh_data:
        logger.error("No data found in sshInfo.csv. Exiting.")
        exit(1)

    # Ensure output directories exist
    output_dir = "current_config"
    diff_dir = "diffs"
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(diff_dir, exist_ok=True)
    logger.info(f"Output directories verified: {output_dir}, {diff_dir}")

    # Iterate over devices and retrieve configurations
    for key, value in ssh_data.items():
        device_type = value["Device_Type"]
        ip = value["IP"]
        username = value["Username"]
        password = value["Password"]

        device = {
            "device_type": device_type,
            "host": ip,
            "username": username,
            "password": password,
        }

        try:
            logger.info(f"Connecting to {key} ({ip})...")
            with ConnectHandler(**device) as net_connect:
                net_connect.enable()
                logger.info(f"Retrieving running configuration from {key}...")
                current_config = net_connect.send_command("show running-config")
                
                # Save current configuration
                config_file = os.path.join(output_dir, f"{key}.cfg")
                with open(config_file, "w") as file:
                    file.write(current_config)
                logger.info(f"Configuration for {key} saved to {config_file}")

                # Compare with golden configuration
                golden_config_path = f"/home/student/git/csci5840/golden-configs/{key}.cfg"
                compare_configs(net_connect, key, current_config, golden_config_path)

        except Exception as e:
            logger.error(f"Failed to process {key} ({ip}): {e}")

if __name__ == "__main__":
    # Start the troubleshooting process
    try:
        logger.info("Starting troubleshooting script...")
        main()
        logger.info("Troubleshooting script completed successfully.")
    except Exception as e:
        logger.critical(f"Critical error in troubleshooting script: {e}")
