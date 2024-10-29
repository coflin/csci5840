import unittest
from nethealth import sshInfo, extract_cpu_usage, extract_ospf_neighbors
from netmiko import ConnectHandler

class TestDeviceHealthChecks(unittest.TestCase):
    def setUp(self):
        # Load device info from CSV
        self.devices = sshInfo()
        self.assertIsNotNone(self.devices, "Device information could not be loaded")

    # def test_cpu_usage(self):
    #     for device_name, device_info in self.devices.items():
    #         with self.subTest(device=device_name):
    #             # Map the keys correctly for ConnectHandler
    #             connection_info = {
    #                 "device_type": device_info["Device_Type"],  # Convert to lowercase key
    #                 "ip": device_info["IP"],
    #                 "username": device_info["Username"],
    #                 "password": device_info["Password"]
    #             }
                
    #             # Connect and execute command
    #             connection = ConnectHandler(**connection_info)
    #             cpu_output = connection.send_command("show processes top once | grep Cpu")
    #             cpu_usage = extract_cpu_usage(cpu_output)
    #             connection.disconnect()

    #             # Check that the CPU usage output is in the expected format
    #             self.assertRegex(cpu_usage, r"\d+\.\d+%", "CPU usage extraction failed")

    def test_ospf_neighbors(self):
        for device_name, device_info in self.devices.items():
            with self.subTest(device=device_name):
                connection_info = {
                    "device_type": device_info["Device_Type"],
                    "ip": device_info["IP"],
                    "username": device_info["Username"],
                    "password": device_info["Password"]
                }

                connection = ConnectHandler(**connection_info)
                ospf_output = connection.send_command("show ip ospf neighbor")
                ospf_neighbors = extract_ospf_neighbors(ospf_output)
                connection.disconnect()

                if ospf_neighbors != "[bold red]No OSPF neighbors found[/bold red]":
                    self.assertIn("Neighbor:", ospf_neighbors, "OSPF neighbors extraction failed")

    def test_bgp_neighbors(self):
        for device_name, device_info in self.devices.items():
            with self.subTest(device=device_name):
                connection_info = {
                    "device_type": device_info["Device_Type"],
                    "ip": device_info["IP"],
                    "username": device_info["Username"],
                    "password": device_info["Password"],
                    "timeout": 10
                }

                connection = ConnectHandler(**connection_info)
                bgp_output = connection.send_command("show ip bgp summary")
                connection.disconnect()

                self.assertTrue(len(bgp_output) > 0, "BGP neighbors command returned empty output")

#if __name__ == "__main__":
#    unittest.main()
