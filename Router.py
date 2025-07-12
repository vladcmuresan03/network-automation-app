from Device import Device


class Router(Device):
    def config_ripv2(self):
        # RIPv2 common config
        commands = [
            'router rip',
            'version 2',
            'no auto-summary'
        ]

        network_commands = []
        # loop for reading network addresses for being able to advertise as many as needed
        while True:
            network_ip = input("Enter a network to advertise (or press Enter to finish): ").strip()
            if not network_ip:
                if not network_commands:
                    print("No networks were entered. Aborting RIP configuration.")
                    return
                print("Finished adding networks.")
                break
            network_commands.append(f'network {network_ip}')

        # extend the commands list with the elements from the list containing the "network <ip>" commands
        commands.extend(network_commands)

        # ask if the user wants the router to share its static routes through ripv2
        redistribute_choice = input("Do you want to redistribute static routes? (yes/no): ").lower().strip()
        if redistribute_choice == "yes":
            commands.append('redistribute static')

        with self._connect() as net_connect:
            if net_connect:
                print("\nSending RIPv2 configuration commands...")
                output = net_connect.send_config_set(commands)
                print("--- Command Output ---")
                print(output)
                print("--- End of Output ---")
                print(f"RIPv2 configuration attempted on {self.hostname}.")

    def setup_dhcp(self):
        # configure DHCP server
        dhcp_pool_name = input("Enter the DHCP pool name (eg. LAN_POOL): ")
        network_address = input("Enter the network address (eg. 192.168.10.0): ")
        netmask = input("Enter the subnet mask (eg. 255.255.255.0): ")

        while True:
            default_router_ip = input("Enter the default router IP: ").strip()
            if Device.check_ipv4(default_router_ip):
                break
            else:
                print(f"'{default_router_ip}' is not a valid IPv4 address. Please try again.")


        while True:
            dns_server_ip = input("Enter the DNS server IP (default: 8.8.8.8): ").strip() or "8.8.8.8"
            if Device.check_ipv4(dns_server_ip):
                break
            else:
                print(f"'{dns_server_ip}' is not a valid IPv4 address. Please try again.")


        excluded_start = input("Enter the first IP to exclude (or press Enter to skip): ")
        excluded_end = input("Enter the last IP to exclude (or press Enter to skip): ")

        commands = [
            f"ip dhcp pool {dhcp_pool_name}",
            f"network {network_address} {netmask}",
            f"default-router {default_router_ip}",
            f"dns-server {dns_server_ip}"
        ]
        if excluded_start and excluded_end:
            commands.append("exit")
            # optional excluded-address command: appended only if the user inputs a start and an end to the excl list
            commands.append(f"ip dhcp excluded-address {excluded_start} {excluded_end}")

        with self._connect() as net_connect:
            if net_connect:
                print("\nSending DHCP configuration commands...")
                output = net_connect.send_config_set(commands)
                print("--- Command Output ---")
                print(output)
                print("--- End of Output ---")
                print(f"DHCP server configuration attempted on {self.hostname}.")

    def config_dhcp_helper(self):
        # DHCP helper address for making a router be a relay agent
        interface = input("Enter the interface to configure the helper address on (eg. g0/1): ")

        while True:
            helper_address = input("Enter the IP address of the DHCP server (the helper address): ").strip()
            if Device.check_ipv4(helper_address):
                break
            else:
                print(f"'{helper_address}' is not a valid IPv4 address. Please try again.")


        if not interface or not helper_address:
            print("Interface and helper address cannot be empty. Aborting.")
            return

        commands = [
            f"interface {interface}",
            f"ip helper-address {helper_address}"
        ]

        with self._connect() as net_connect:
            if net_connect:
                print(f"\nSending DHCP helper-address configuration to {interface}...")
                output = net_connect.send_config_set(commands)
                print("--- Command Output ---")
                print(output)
                print("--- End of Output ---")
                print(f"DHCP helper address configuration attempted on {self.hostname}.")

    def get_dhcp(self):
        # allow the device to lease an IP address from the DHCP server
        interface = input("Enter the interface which will get its address through DHCP: ")

        if not interface:
            print("Interface not provided. Aborting.")
            return

        commands = [
            f"interface {interface}",
            "ip address dhcp",
            "no shutdown"
        ]

        with self._connect() as net_connect:
            if net_connect:
                print(f"\bSending DHCP enabling configuration to {interface}...")
                output = net_connect.send_config_set(commands)
                print("--- Command Output ---")
                print(output)
                print("--- End of Output ---")
                print(f"DHCP client configuration attempted on {self.hostname}.")
                print(f"\n Note: It may take a minute for the interface to receive an IP address.")

    def config_hsrp(self):
        # configuring HSRP on an interface

        interface = input("Enter the interface for HSRP (e.g., GigabitEthernet0/0 or g0/0.10): ")
        is_subinterface = '.' in interface # if the interface's name contains a '.' it means it is a subinterface

        vlan_id_for_encap = ""
        if is_subinterface == 'yes':
            vlan_id_for_encap = input("Enter the VLAN ID for encapsulation (e.g., 10): ")

        while True:
            real_ip = input(f"Enter the REAL IP address for the interface '{interface}': ").strip()
            if Device.check_ipv4(real_ip):
                break
            else:
                print(f"'{real_ip}' is not a valid IPv4 address. Please try again.")

        subnet_mask = input(f"Enter the subnet mask for '{real_ip}': ")

        standby_group_id = input("Enter the HSRP standby group ID: ")

        while True:
            virtual_ip = input("Enter the HSRP virtual IP address: ").strip()
            if Device.check_ipv4(virtual_ip):
                break
            else:
                print(f"'{virtual_ip}' is not a valid IPv4 address. Please try again.")

        priority = input("Enter HSRP priority (default 100): ") or "100"
        preempt = input("Enable HSRP preemption? (yes/no, default yes): ").lower().strip() != 'no'

        commands = [
            f'interface {interface}',
        ]
        if is_subinterface == 'yes' and vlan_id_for_encap.isdigit():
            commands.append(f'encapsulation dot1q {vlan_id_for_encap}')

        commands.append(f'ip address {real_ip} {subnet_mask}')
        # HSRP group commands
        commands.extend([
            'standby version 2',
            f'standby {standby_group_id} ip {virtual_ip}',
            f'standby {standby_group_id} priority {priority}'
        ])

        if preempt:
            commands.append(f'standby {standby_group_id} preempt')

        with self._connect() as net_connect:
            if net_connect:
                print("\nSending complete HSRP and interface configuration...")
                output = net_connect.send_config_set(commands)
                print("--- Command Output ---")
                print(output)
                print("--- End of Output ---")
                print(f"HSRP and interface configuration attempted on {self.hostname}.")
