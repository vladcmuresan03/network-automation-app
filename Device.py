from netmiko import ConnectHandler
from netmiko import NetmikoAuthenticationException, NetmikoTimeoutException


class Device:
    def __init__(self, hostname, ip_address, username, password, exec_pass, device_type):
        self.hostname = hostname
        self.device_details = {
            'device_type': device_type,
            'host': ip_address,
            'username': username,
            'password': password,
            'secret': exec_pass,
        }

    def _connect(self):
        # Helper function for establishing connection
        try:
            print(f"\nAttempting to connect to {self.hostname} ({self.device_details['host']})...")
            net_connect = ConnectHandler(**self.device_details)
            print("Connection successful.")
            return net_connect
        except NetmikoTimeoutException:
            print(f"Connection timed out to {self.hostname}.")
            return None
        except NetmikoAuthenticationException:
            print(f"Authentication failed for {self.hostname}.")
            return None
        except Exception as e:
            print(f"An unexpected error occurred while connecting to {self.hostname}: {e}")
            return None

    def ping(self) -> None:
        # Sends the "ping <ip>" command to the selected device

        #check if ip address is correctly written using a method
        while True:
            destination_ip = input(f"Enter the destination IP address to ping from {self.hostname}: ").strip()
            if Device.check_ipv4(destination_ip):
                break
            else: print(f"'{destination_ip}' is not a valid IPv4 address. Please try again.")

        command = f'ping {destination_ip}'

        with self._connect() as net_connect:
            if net_connect:
                print(f"Sending command: {command}")
                # using expect_string for waiting until the command is finished and printing all of its output
                output = net_connect.send_command(command, expect_string=r'#')
                print(f"\n--- Ping Output from {self.hostname} ---")
                print(output)
                print("--- End of Ping Output ---")

    def show_ip_interface_brief(self) -> None:
        # Sends the 'show ip int br' command to the device
        command = 'show ip interface brief'

        with self._connect() as net_connect:
            if net_connect:
                print(f"Sending command: {command}")
                output = net_connect.send_command(command)
                print(f"\n--- Output of '{command}' from {self.hostname} ---")
                print(output)
                print("--- End of Output ---")

    @staticmethod
    def check_ipv4(ip: str) -> bool:
        # checker for ipv4 addresses

        # check if received ip variable is actually a string
        if not isinstance(ip, str):
            return False

        parts = ip.split('.')

        # check if the ip address has 4 numbers separated by the dots.
        if len(parts) != 4:
            return False

        for part in parts:
            # each of these numbers is in range 0-255
            if not part.isdigit() or not 0 <= int(part) <= 255:
                return False

        return True