from flask import Flask, render_template, request, redirect, url_for
import yaml  # Ensure PyYAML is installed

app = Flask(__name__)

# Route for the main page
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/grafana')
def grafana():
    return redirect("http://localhost:3000/d/ddysd3va691xce/device-statistics?orgId=1&refresh=5s")

def clean_empty_fields(data):
    return None if data == '' else data

@app.route('/add-device', methods=['GET', 'POST'])
def add_device():
    if request.method == 'POST':
        router_type = request.form['routerType']

        # Common device details
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
                    **({
                        'dhcp_enabled': request.form.getlist('dhcpEnabled[]')[i] == 'true',
                        'dhcp_range_start': clean_empty_fields(request.form.getlist('dhcpRangeStart[]')[i]),
                        'dhcp_range_end': clean_empty_fields(request.form.getlist('dhcpRangeEnd[]')[i]),
                        'default_gateway': clean_empty_fields(request.form.getlist('defaultGateway[]')[i]),
                        'dhcpv6_range_start': clean_empty_fields(request.form.getlist('dhcpv6RangeStart[]')[i]),
                        'dhcpv6_range_end': clean_empty_fields(request.form.getlist('dhcpv6RangeEnd[]')[i]),
                        'ipv4_virtual_router_address': clean_empty_fields(request.form.getlist('ipv4VRouter[]')[i]),
                        'ipv6_virtual_router_address': clean_empty_fields(request.form.getlist('ipv6VRouter[]')[i])
                    } if router_type == 'Access' else {})
                }
                for i in range(len(request.form.getlist('vlanId[]')))
            ],
            'interfaces': [
                {
                    'name': request.form.getlist('interfaceName[]')[i],
                    'ipv4': clean_empty_fields(request.form.getlist('ipv4[]')[i]),
                    'ipv6': clean_empty_fields(request.form.getlist('ipv6[]')[i]),
                    'speed': clean_empty_fields(request.form.getlist('speed[]')[i]),
                    'switchport_mode': clean_empty_fields(request.form.getlist('switchportMode[]')[i]),
                    'ospfv3_area': clean_empty_fields(request.form.getlist('ospfv3Area[]')[i]) if router_type == 'Core' else None
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
            }
        }

        # Handle routing protocols based on router type
        if router_type == 'Access':
            # For Access routers, handle OSPF and RIP
            device['routing_protocols'] = {
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
            filename = f"/home/student/git/csci5840/lab4/{device['name']}_access.yaml"

        elif router_type == 'Core':
            # For Core routers, handle OSPF, OSPFv3, and BGP
            device['routing_protocols'] = {
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
                'ospfv3': {
                    'address_family': 'ipv6',
                    'redistribute_bgp': request.form.get('redistributeBgp') == 'true',
                },
                'bgp': {
                    'as': clean_empty_fields(request.form['bgpAsCore']),
                    'neighbors': [
                        {
                            'ip': clean_empty_fields(request.form.getlist('neighborIp[]')[i]),
                            'remote_as': clean_empty_fields(request.form.getlist('remoteAs[]')[i])
                        }
                        for i in range(len(request.form.getlist('neighborIp[]')))
                    ],
                    'networks': [
                        clean_empty_fields(request.form.getlist('bgpNetwork[]')[i])
                        for i in range(len(request.form.getlist('bgpNetwork[]')))
                    ]
                }
            }
            filename = f"/home/student/git/csci5840/lab4/{device['name']}_core.yaml"

        # Generate and save the YAML file
        yaml_data = yaml.dump({'device': device}, sort_keys=False)
        with open(filename, 'w') as file:
            file.write(yaml_data)

        # Redirect to home or success page
        return redirect(url_for('index'))

    return render_template('add_device.html')


if __name__ == '__main__':
    app.run(debug=True)

