import xml.etree.ElementTree as ET
from ncclient import manager
from ncclient.operations.rpc import RPCError
import sqlite3
import time

# Database file path
DB_FILE = '/var/log/netman/logs.db'

def initialize_database():
    """Initialize the SQLite database and create the table if it doesn't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS interface_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address TEXT,
            interface_name TEXT,
            mtu TEXT,
            incoming_packets TEXT,
            outgoing_packets TEXT,
            speed TEXT,
            interface_status TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(ip_address, interface_name)
        )
    ''')
    conn.commit()
    conn.close()


def insert_interface_stats(ip_address, name, mtu, incoming_packets, outgoing_packets, speed, status):
    """Insert or replace interface statistics into the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Use INSERT OR REPLACE to update existing entries or insert new ones
    cursor.execute('''
        INSERT OR REPLACE INTO interface_stats (id, ip_address, interface_name, mtu, incoming_packets, outgoing_packets, speed, interface_status, timestamp)
        VALUES (
            (SELECT id FROM interface_stats WHERE ip_address = ? AND interface_name = ?),
            ?, ?, ?, ?, ?, ?, ?,  CURRENT_TIMESTAMP
        )
    ''', (ip_address, name, ip_address, name, mtu, incoming_packets, outgoing_packets, speed, status))
    
    conn.commit()
    conn.close()


def print_interface_details(xml_response, ip_address):
    root = ET.fromstring(xml_response)
    
    # Define namespaces based on what you find in the XML
    ns = {
        'ocif': 'http://openconfig.net/yang/interfaces',
        'ocipv4': 'http://openconfig.net/yang/interfaces/ip',
        'ocvlan': 'http://openconfig.net/yang/vlan',
        'oceth': 'http://openconfig.net/yang/interfaces/ethernet',
    }

    # Extract and print interface details
    for interface in root.findall('.//ocif:interface', ns):
        name_elem = interface.find('ocif:name', ns)
        name = name_elem.text if name_elem is not None else "No Name"
        
        # Initialize default values
        mtu_ipv4 = "1500"
        incoming_packets = "N/A"
        outgoing_packets = "N/A"
        port_speed = "N/A"
        admin_status = "N/A"
        
        # Extract MTU for IPv4
        ipv4_elem = interface.find('.//ocipv4:ipv4', ns)
        if ipv4_elem is not None:
            mtu_elem_ipv4 = ipv4_elem.find('ocipv4:state/ocipv4:mtu', ns)
            mtu_ipv4 = mtu_elem_ipv4.text if mtu_elem_ipv4 is not None else "1500"

        # Extract interface counters
        counters_elem = interface.find('.//ocif:counters', ns)
        if counters_elem is not None:
            incoming_packets_elem = counters_elem.find('ocif:in-pkts', ns)
            outgoing_packets_elem = counters_elem.find('ocif:out-pkts', ns)
            incoming_packets = incoming_packets_elem.text if incoming_packets_elem is not None else "N/A"
            outgoing_packets = outgoing_packets_elem.text if outgoing_packets_elem is not None else "N/A"
        
        # Extract interface speed
        state_elem = interface.find('.//oceth:state', ns)
        if state_elem is not None:
            port_speed_elem = state_elem.find('oceth:port-speed', ns)
            port_speed = port_speed_elem.text.split('_')[1] if port_speed_elem is not None else "N/A"
        
        # Extract interface status
        oper_status_elem = interface.find('.//ocif:oper-status', ns)
        if oper_status_elem is not None:
            oper_status = oper_status_elem.text if oper_status_elem is not None else "N/A"

        # Print interface details
        print(f"Interface Name: {name}")
        print(f"MTU: {mtu_ipv4}")
        print(f"Incoming Total Packets: {incoming_packets}")
        print(f"Outgoing Total Packets: {outgoing_packets}")
        print(f"Speed: {port_speed}")
        print(f"Interface Status: {oper_status}")
        print()
        
        # Insert details into the database
        insert_interface_stats(ip_address, name, mtu_ipv4, incoming_packets, outgoing_packets, port_speed, oper_status)

def fetch_and_print_details(ip_address):
    try:
        with manager.connect(host=ip_address,
                             port=830,
                             username='admin',
                             password='admin',
                             hostkey_verify=False) as m:

            filter = """
            <filter type="subtree">
                <interfaces xmlns="http://openconfig.net/yang/interfaces"/>
            </filter>
            """
            
            response = m.get(filter)
            # Call the function to print details
            print("--------------------------------------")
            print(f"Details for {ip_address}:")
            print("--------------------------------------")
            print_interface_details(response.xml, ip_address)
    
    except RPCError as e:
        print(f"RPC Error for {ip_address}: {e}")
    except Exception as e:
        print(f"An error occurred for {ip_address}: {e}")

# Initialize the database
initialize_database()

# List of IP addresses
ip_addresses = [
    '192.168.100.5',
    '192.168.100.6',
    '192.168.100.3',
    '192.168.100.4',
    '192.168.100.7',
    '192.168.100.8'
]

# Run the script in a loop
while True:
    for ip in ip_addresses:
        fetch_and_print_details(ip)
    
    # Wait for 1 second before the next iteration
    time.sleep(1)

