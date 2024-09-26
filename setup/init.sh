#!/bin/bash

# Update package list and install required packages
apt-get update
apt-get install -y iputils-ping net-tools curl isc-dhcp-client

# Remove the default route if it exists
ip route del default || true

# Request an IP address from the DHCP server
dhclient eth1
