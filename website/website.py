from flask import Flask, render_template, request, redirect, url_for
import subprocess
import yaml

app = Flask(__name__)

# Route for the main page
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/grafana')
def grafana():
    return redirect("http://10.224.77.53:3000/d/ddysd3va691xce/device-statistics?orgId=1&refresh=5s")

def clean_empty_fields(data):
    return None if data == '' else data

@app.route('/add-device', methods=['GET', 'POST'])
def add_device():
    if request.method == 'POST':
        router_type = request.form['routerType']

        # Separate handling for Access and Core
        if router_type == 'Access':
            # Access router details
            device = {
                'name': request.form['deviceName'],
                'vlans': [
                    {
                        'id': request.form.getlist('vlanId[]')[i],
                        'name': clean_empty_fields(request.form.getlist('vlanName[]')[i]),
                        'ipv4_subnet': clean_empty_fields(request.form.getlist('ipv4Subnet[]')[i]),
                        'ipv6_subnet': clean_empty_fields(request.form.getlist('ipv6Subnet[]')[i]),
                        'ospfv3': {
                            'area': clean_empty_fields(request.form.getlist('ospfv3Area[]')[i])
                        },
                        'dhcp_enabled': request.form.getlist('dhcpEnabled[]')[i] == 'true',
                        'dhcp_range_start': clean_empty_fields(request.form.getlist('dhcpRangeStart[]')[i]),
                        'dhcp_range_end': clean_empty_fields(request.form.getlist('dhcpRangeEnd[]')[i]),
                        'default_gateway': clean_empty_fields(request.form.getlist('defaultGateway[]')[i]),
                        'dhcpv6_range_start': clean_empty_fields(request.form.getlist('dhcpv6RangeStart[]')[i]),
                        'dhcpv6_range_end': clean_empty_fields(request.form.getlist('dhcpv6RangeEnd[]')[i]),
                        'ipv4_virtual_router_address': clean_empty_fields(request.form.getlist('ipv4VRouter[]')[i]),
                        'ipv6_virtual_router_address': clean_empty_fields(request.form.getlist('ipv6VRouter[]')[i])
                    }
                    for i in range(len(request.form.getlist('vlanId[]')))
                ],
                'interfaces': [
                    {
                        'name': request.form.getlist('interfaceName[]')[i],
                        'ipv4': clean_empty_fields(request.form.getlist('ipv4[]')[i]),
                        'ipv6': clean_empty_fields(request.form.getlist('ipv6[]')[i]),
                        'switchport_mode': clean_empty_fields(request.form.getlist('switchportMode[]')[i])
                    }
                    for i in range(len(request.form.getlist('interfaceName[]')))
                ],
                'routes': {
                    'static': [
                        {
                            'prefix': clean_empty_fields(request.form.getlist('staticPrefix[]')[i]),
                            'next_hop': clean_empty_fields(request.form.getlist('staticNextHop[]')[i])
                        }
                        for i in range(len(request.form.getlist('staticPrefix[]')))
                    ],
                    'ipv6_static': [
                        {
                            'prefix': clean_empty_fields(request.form.getlist('ipv6StaticPrefix[]')[i]),
                            'next_hop': clean_empty_fields(request.form.getlist('ipv6StaticNextHop[]')[i])
                        }
                        for i in range(len(request.form.getlist('ipv6StaticPrefix[]')))
                    ]
                },
                'routing_protocols': {
                    'ospf': {
                        'id': clean_empty_fields(request.form['ospfId']),
                        'networks': [
                            {
                                'prefix': clean_empty_fields(request.form.getlist('ospfNetwork[]')[i]),
                                'area': clean_empty_fields(request.form.getlist('ospfArea[]')[i])
                            }
                            for i in range(len(request.form.getlist('ospfNetwork[]')))
                        ]
                    },
                    'rip': {
                        'networks': [
                            {
                                'prefix': clean_empty_fields(request.form.getlist('ripNetwork[]')[i])
                            }
                            for i in range(len(request.form.getlist('ripNetwork[]')))
                        ]
                    }
                }
            }
            filename = f"/home/student/git/csci5840/template-generator/generated-configs/{device['name']}_access.yaml"

        elif router_type == 'Core':
            # Core router details
            device = {
                'name': request.form['deviceName'],
                'vlans': [
                    {
                        'id': request.form.getlist('vlanIdCore[]')[i],
                        'name': clean_empty_fields(request.form.getlist('vlanNameCore[]')[i]),
                        'ipv4_subnet': clean_empty_fields(request.form.getlist('ipv4SubnetCore[]')[i]),
                        'ipv6_subnet': clean_empty_fields(request.form.getlist('ipv6SubnetCore[]')[i]),
                        'ospfv3': {
                            'area': clean_empty_fields(request.form.getlist('ospfv3AreaCore[]')[i])
                        }
                    }
                    for i in range(len(request.form.getlist('vlanIdCore[]')))
                ],
                'interfaces': [
                    {
                        'name': request.form.getlist('interfaceNameCore[]')[i],
                        'ipv4': clean_empty_fields(request.form.getlist('ipv4Core[]')[i]),
                        'ipv6': clean_empty_fields(request.form.getlist('ipv6Core[]')[i]),
                        'switchport_mode': clean_empty_fields(request.form.getlist('switchportModeCore[]')[i]),
                        'ospfv3_area': clean_empty_fields(request.form.getlist('ospfv3AreaInterfaceCore[]')[i])
                    }
                    for i in range(len(request.form.getlist('interfaceNameCore[]')))
                ],
                'routes': {
                    'static': [
                        {
                            'prefix': clean_empty_fields(request.form.getlist('staticPrefixCore[]')[i]),
                            'next_hop': clean_empty_fields(request.form.getlist('staticNextHopCore[]')[i])
                        }
                        for i in range(len(request.form.getlist('staticPrefixCore[]')))
                    ],
                    'ipv6_static': [
                        {
                            'prefix': clean_empty_fields(request.form.getlist('ipv6StaticPrefixCore[]')[i]),
                            'next_hop': clean_empty_fields(request.form.getlist('ipv6StaticNextHopCore[]')[i])
                        }
                        for i in range(len(request.form.getlist('ipv6StaticPrefixCore[]')))
                    ]
                },
                'routing_protocols': {
                    'ospf': {
                        'id': clean_empty_fields(request.form['ospfId']),
                        'networks': [
                            {
                                'prefix': clean_empty_fields(request.form.getlist('ospfNetworkCore[]')[i]),
                                'area': clean_empty_fields(request.form.getlist('ospfAreaCore[]')[i])
                            }
                            for i in range(len(request.form.getlist('ospfNetworkCore[]')))
                        ]
                    },
                    'ospfv3': {
                        'address_family': 'ipv6',
                        'redistribute_bgp': 'true'
                    },
                    'bgp': {
                        'as': clean_empty_fields(request.form['bgpAsCore']),
                        'neighbors': [
                            {
                                'ip': clean_empty_fields(request.form.getlist('neighborIpCore[]')[i]),
                                'remote_as': clean_empty_fields(request.form.getlist('remoteAsCore[]')[i])
                            }
                            for i in range(len(request.form.getlist('neighborIpCore[]')))
                        ],
                        'networks': [
                            clean_empty_fields(request.form.getlist('bgpNetworkPrefixCore[]')[i])
                            for i in range(len(request.form.getlist('bgpNetworkPrefixCore[]')))
                        ]
                    }
                }
            }
            filename = f"/home/student/git/csci5840/template-generator/generated-configs/{device['name']}_core.yaml"

        # Generate and save the YAML file
        yaml_data = yaml.dump({'device': device}, sort_keys=False)
        with open(filename, 'w') as file:
            file.write(yaml_data)
        
        # Push to Github
        subprocess.run(["git", "add", "."], cwd="/home/student/git/csci5840")
        subprocess.run(["git", "commit", "-m", f"Added {device['name']} configuration"], cwd="/home/student/git/csci5840")
        subprocess.run(["git", "push"], cwd="/home/student/git/csci5840")

        # Redirect to home or success page
        return redirect(url_for('index'))

    return render_template('add_device.html')


if __name__ == '__main__':
    app.run(debug=True)

