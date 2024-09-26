#!/bin/bash

# Update package list and install required packages
apt-get update
apt-get install -y iputils-ping net-tools curl vim apache2

# Remove the default index.html file
rm -f /var/www/html/index.html

# Create a new index.html file with custom content
echo '<html><body>Hello World!</body></html>' > /var/www/html/index.html

# Enable the default site configuration
a2ensite 000-default.conf

# Start Apache service
service apache2 start

# Configure network interface
ifconfig eth3 110.0.0.2 netmask 255.255.255.252

# Remove the existing default route
#ip route del default || true

# Add a new default route via the specified gateway
#ip route add default via 110.0.0.1 dev eth3

