#! /usr/bin/python3
from art import text2art
import re
import csv
from netmiko import ConnectHandler
from rich.console import Console
from rich.table import Table
from InquirerPy import prompt
from termcolor import colored

console = Console()

def sshInfo():
    try:
        csv_file = "sshInfo.csv"
        data = {}

        with open(csv_file, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                router_name = row["Routers"]
                router_data = {
                    "Device_Type": row["Device_Type"],
                    "IP": row["IP"],
                    "Username": row["Username"],
                    "Password": row["Password"]
                }
                data[router_name] = router_data

        return data

    except Exception as e:
        console.log(f"[bold red]Unable to open sshInfo.csv file: {e}[/bold red]")
        return None

def extract_cpu_usage(cpu_output):
    """
    Extracts 'sy' from the CPU usage output. Format expected:
    %Cpu(s):  3.2 us,  5.6 sy,  0.0 ni, 91.3 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st
    """
    match = re.search(r'(\d+\.\d+) sy', cpu_output)
    return f"{match.group(1)}%" if match else "[bold red]Unable to extract CPU usage[/bold red]"

def extract_ospf_neighbors(ospf_output):
    """
    Extracts Neighbor ID, State, and Interface from the OSPF output. Expected format:
    Neighbor ID     Instance VRF      Pri State                  Dead Time   Address         Interface
    200.0.0.1       1        default  1   FULL/BDR               00:00:33    100.0.0.3       Vlan50
    """
    neighbors = []
    for line in ospf_output.splitlines():
        match = re.search(r'(\d+\.\d+\.\d+\.\d+)\s+\S+\s+\S+\s+\S+\s+(\S+)\s+.+\s+(\S+)$', line)
        if match:
            neighbor_id = match.group(1)
            state = match.group(2)
            interface = match.group(3)
            neighbors.append(f"Neighbor: {neighbor_id}, State: {state}, Interface: {interface}")
    return "\n".join(neighbors) if neighbors else "[bold red]No OSPF neighbors found[/bold red]"

def execute_ssh_command(ip, username, password, command):
    device = {
        'device_type': 'arista_eos',
        'ip': ip,
        'username': username,
        'password': password,
    }

    try:
        net_connect = ConnectHandler(**device)
        net_connect.enable()  # Enter enable mode
        output = net_connect.send_command(command)
        return output
    except Exception as e:
        return f"[bold red]Failed to connect to {ip}: {e}[/bold red]"

def get_health_info(device):
    ip = ssh_data[device]['IP']
    username = ssh_data[device]['Username']
    password = ssh_data[device]['Password']

    # Health check commands
    commands = {
        "CPU Usage": "show processes top once | grep Cpu",
        "OSPF Neighborships": "show ip ospf neighbor",
        "BGP Neighborships": "show ip bgp summary",
        "Route Table": "show ip route",
        "IP Connectivity": "ping 192.168.100.1"
    }

    console.rule(f"[bold cyan]Health Check for {device} ({ip})[/bold cyan]")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Check")
    table.add_column("Result")

    # CPU Usage
    cpu_output = execute_ssh_command(ip, username, password, commands["CPU Usage"])
    cpu_usage = extract_cpu_usage(cpu_output)
    table.add_row(f"\n[bold yellow]CPU Usage[/bold yellow]", cpu_usage)

    # OSPF Neighborships
    ospf_output = execute_ssh_command(ip, username, password, commands["OSPF Neighborships"])
    ospf_neighbors = extract_ospf_neighbors(ospf_output)
    table.add_row(f"--------------------------------\n\n[bold yellow]OSPF Neighborships[/bold yellow]", f"----------------------------------------------------------------\n\n{ospf_neighbors}")

    # BGP Neighborships (Simply output as is, or you could extract fields similarly)
    bgp_output = execute_ssh_command(ip, username, password, commands["BGP Neighborships"])
    table.add_row(f"--------------------------------\n\n[bold yellow]BGP Neighborships[/bold yellow]", f"----------------------------------------------------------------\n\n{bgp_output.strip()}")

    # Route Table (Filtered)
    route_output = execute_ssh_command(ip, username, password, commands["Route Table"])
    if "Gateway of last resort" in route_output:
        start_index = route_output.find("Gateway of last resort")
        filtered_route_output = route_output[start_index:]
        table.add_row(f"--------------------------------\n\n[bold yellow]Route Table[/bold yellow]", f"----------------------------------------------------------------\n\n{filtered_route_output.strip()}")
    else:
        table.add_row(f"--------------------------------\n[bold yellow]Route Table[/bold yellow]", "----------------------------------------------------------------\n[bold red]No route table available[/bold red]")

    # IP Connectivity
    ping_output = execute_ssh_command(ip, username, password, commands["IP Connectivity"])
    table.add_row(f"--------------------------------\n\n[bold yellow]IP Connectivity[/bold yellow]", f"----------------------------------------------------------------\n\n{ping_output.strip()}")

    console.print(table)  # Print the table once at the end

# Display fancy title at the start
def display_title():
    title = text2art("NetHealth", font="doom")
    print(title)
    print(colored("Author: Sneha Irukuvajjula\n\n", "cyan"))

if __name__ == "__main__":
    display_title()
    ssh_data = sshInfo()
    if ssh_data:
        # Loop to continuously ask for input until the user quits
        while True:
            devices = list(ssh_data.keys()) + ["Quit"]  # Add 'Quit' as an option
            questions = [
                {
                    "type": "list",
                    "name": "device_choice",
                    "message": "Choose the device you want to check or quit:",
                    "choices": devices
                }
            ]
            answers = prompt(questions)
            selected_device = answers['device_choice']

            if selected_device == "Quit":
                console.print("\n[bold yellow]Exiting the health check tool.[/bold yellow]\n")
                break
            else:
                get_health_info(selected_device)

