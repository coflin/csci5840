import unittest
from nethealth import sshInfo, extract_cpu_usage, extract_ospf_neighbors, execute_ssh_command

class TestSSHInfo(unittest.TestCase):
    def test_ssh_info_returns_data(self):
        data = sshInfo()
        self.assertIsNotNone(data)  # Check that data is not None
        self.assertIn("Device_Type", data.get("r1", {}))  # Sample check for 'Device_Type' key

class TestExtractCPUUsage(unittest.TestCase):
    def test_extract_cpu_usage_valid(self):
        output = "%Cpu(s):  3.2 us,  5.6 sy,  0.0 ni, 91.3 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 st"
        result = extract_cpu_usage(output)
        self.assertEqual(result, "5.6%")

    def test_extract_cpu_usage_invalid(self):
        output = "%Cpu(s):  3.2 us,  0.0 ni, 91.3 id,  0.0 wa"
        result = extract_cpu_usage(output)
        self.assertEqual(result, "[bold red]Unable to extract CPU usage[/bold red]")

class TestExtractOSPFNeighbors(unittest.TestCase):
    def test_extract_ospf_neighbors_valid(self):
        ospf_output = """
        Neighbor ID     Instance VRF      Pri State                  Dead Time   Address         Interface
        200.0.0.1       1        default  1   FULL/BDR               00:00:33    100.0.0.3       Vlan50
        """
        neighbors = extract_ospf_neighbors(ospf_output)
        self.assertIn("Neighbor: 200.0.0.1, State: FULL/BDR, Interface: Vlan50", neighbors)

    def test_extract_ospf_neighbors_invalid(self):
        ospf_output = "No OSPF neighbors found"
        neighbors = extract_ospf_neighbors(ospf_output)
        self.assertEqual(neighbors, "[bold red]No OSPF neighbors found[/bold red]")

from unittest.mock import patch

class TestExecuteSSHCommand(unittest.TestCase):
    @patch("nethealth.ConnectHandler")
    def test_execute_ssh_command_success(self, MockConnectHandler):
        mock_conn = MockConnectHandler.return_value
        mock_conn.send_command.return_value = "CPU usage: 5.6 sy"

        result = execute_ssh_command("192.168.100.2", "admin", "admin", "show processes top once | grep Cpu")
        self.assertEqual(result, "CPU usage: 5.6 sy")

    @patch("nethealth.ConnectHandler")
    def test_execute_ssh_command_failure(self, MockConnectHandler):
        MockConnectHandler.side_effect = Exception("Connection failed")

        result = execute_ssh_command("192.168.100.2", "admin", "admin", "show processes top once | grep Cpu")
        self.assertIn("[bold red]Failed to connect", result)


