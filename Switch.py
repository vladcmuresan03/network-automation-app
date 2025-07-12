from Device import Device


class Switch(Device):
    def config_security(self):  # Security configuration

        # Warning for interface selection
        print("\n==========================================================")
        print("WARNING! Applying port security to the wrong interface")
        print("(example: a management interface or trunk port) can result")
        print("in loss of connectivity of the end device to the switch.")
        print("==========================================================\n")

        # Input interface
        interface = input("Enter the ACCESS interface for port security (e.g., GigabitEthernet0/1): ")
        if not interface:
            print("Interface cannot be empty. Aborting.")
            return

        # Input vlan ID
        access_vlan = input(f"Enter the VLAN ID for this access port {interface} (eg. 10): ")
        if not access_vlan.isdigit():
            print("Invalid VLAN ID. Aborting.")
            return

        print("\nConfigure Port Security Violation Action:")
        print("1. shutdown (Port is disabled - most secure)")
        print("2. restrict (Drops violating packets; logs and port stay up)")
        print("3. protect (Drops violating packets, no logs sent, port stays up - least disruptive)")
        violation_choice = input("Choose violation action (1/2/3, default 3 'protect'): ").strip()

        violation_action = "switchport port-security violation protect"  # default
        if violation_choice == '1':
            violation_action = "switchport port-security violation shutdown"
        elif violation_choice == '2':
            violation_action = "switchport port-security violation restrict"

        # Numb of allowed MAC Addresses
        max_mac = input("Allow maximum how many MAC addresses on this port? (default 1): ").strip() or "1"
        if not max_mac.isdigit() or int(max_mac) < 1:
            print("Invalid input for maximum MACs. Defaulting to 1.")
            max_mac = "1"

        commands = [
            f'interface {interface}',
            'switchport mode access',
            f'switchport access vlan {access_vlan}',
            'switchport port-security',
            f'switchport port-security maximum {max_mac}',
            violation_action,
            'spanning-tree portfast',
            'spanning-tree bpduguard enable'
        ]

        with self._connect() as net_connect:
            if net_connect:
                print("\nSending Port Security configuration commands...")
                output = net_connect.send_config_set(commands)
                print("--- Command Output ---")
                print(output)
                print("--- End of Output ---")
                print(f"Port Security configuration attempted on {self.hostname}.")

    def config_vlan(self):
        # Input a VLAN ID and name
        vlan_id = input("Enter the VLAN ID (1-4094): ")
        vlan_name = input(f"Enter the name for VLAN {vlan_id} (e.g., DATA_VLAN): ")

        if not (vlan_id.isdigit() and 1 <= int(vlan_id) <= 4094):
            print("Invalid VLAN ID. Aborting.")
            return
        if not vlan_name:
            print("VLAN name cannot be empty. Aborting.")
            return

        commands = [
            f'vlan {vlan_id}',
            f'name {vlan_name}'
        ]

        with self._connect() as net_connect:
            if net_connect:
                print("\nSending VLAN configuration commands...")
                output = net_connect.send_config_set(commands)
                print("--- Command Output ---")
                print(output)
                print("--- End of Output ---")
                print(f"VLAN {vlan_id} ({vlan_name}) configuration attempted on {self.hostname}.")

    def show_vlan_brief(self):
        # Sends the 'show vlan br' command to the device
        command = 'show vlan brief'

        with self._connect() as net_connect:
            if net_connect:
                print(f"Sending command: {command}")
                output = net_connect.send_command(command)
                print(f"\n--- Output of '{command}' from {self.hostname} ---")
                print(output)
                print("--- End of Output ---")

    def config_stp(self):
        commands_to_send = []

        # Choose if rapid pvst mode should be on (default) or not
        stp_mode_choice = input("Set STP mode to 'rapid-pvst'? (yes/no, default yes): ").lower().strip()
        if stp_mode_choice in ["yes", ""]:
            commands_to_send.append('spanning-tree mode rapid-pvst')

        # Input primary vlan ID
        primary_vlan_str = input("Enter VLAN ID to be STP primary root (or press Enter to skip): ").strip()
        if primary_vlan_str.isdigit():
            commands_to_send.append(f'spanning-tree vlan {primary_vlan_str} root primary')

        # Input sec vlan ID
        secondary_vlan_str = input("Enter VLAN ID to be STP secondary root (or press Enter to skip): ").strip()
        if secondary_vlan_str.isdigit():
            if secondary_vlan_str == primary_vlan_str:
                print(f"Cannot set VLAN {secondary_vlan_str} as secondary; it's already primary. Skipping.")
            else:
                commands_to_send.append(f'spanning-tree vlan {secondary_vlan_str} root secondary')

        # if the user did not input any of the three options, the method will stop
        if not commands_to_send:
            print("No STP changes selected.")
            return

        with self._connect() as net_connect:
            if net_connect:
                print("\nSending STP configuration commands...")
                output = net_connect.send_config_set(commands_to_send)
                print("--- Command Output ---")
                print(output)
                print("--- End of Output ---")
                print(f"STP configuration attempted on {self.hostname}.")
