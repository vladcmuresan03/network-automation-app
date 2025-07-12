from Switch import Switch
from Router import Router
from Device import Device
import json
import os
from simple_term_menu import TerminalMenu


def load_devices_from_json(filename='devices.json'):
    # method for loading details about known devices from a JSON file
    try:
        with open(filename, 'r') as file:
            devices_data = json.load(file)
        # Basic validation
        for i, device_entry in enumerate(devices_data):
             if not all(key in device_entry for key in ['type', 'hostname', 'ip_address', 'username', 'password', 'exec_password', 'device_type']):
                 print(f"Warning: Device entry for '{device_entry.get('hostname', 'N/A')}' is missing one or more required keys.")
        return devices_data
    except FileNotFoundError:
        print(f"Error: Device data file '{filename}' not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{filename}'.")
        return []
    except Exception as e:
        print(f"An unexpected error occurred while loading device data: {e}")
        return []

    def clear_screen():
        os.system('cls' if os.name == 'nt' else 'clear')

def main():
    # method for main menu
    devices = load_devices_from_json()
    if not devices:
        print("No devices loaded or error during loading. Please check 'devices.json'. Exiting application.")
        return

    main_menu_title = "=======================================\n" \
                      "======= Network Automation Tool =======\n" \
                      "============== Main Menu ==============\n" \
                      "=======================================\n"
    main_menu_items = [
        "List available devices",
        "Choose a device to manage",
        "Exit"
    ]
    main_menu = TerminalMenu(
        main_menu_items,
        title=main_menu_title,
        clear_screen=True,
    )

    while True:
        menu_entry_index = main_menu.show()

        if menu_entry_index is None or main_menu_items[menu_entry_index] == "Exit":
            print("Exiting application...")
            break

        choice = main_menu_items[menu_entry_index]

        if choice == "List available devices":
            list_available_devices(devices)
        elif choice == "Choose a device to manage":
            manage_device_menu(devices)


def list_available_devices(devices_data):

    print("\n----------- Available Devices -----------")
    for i, device_info in enumerate(devices_data):
        print(f"{i + 1}. Hostname: {device_info.get('hostname', 'N/A')}, "
              f"IP: {device_info.get('ip_address', 'N/A')}, "
              f"Type: {device_info.get('type', 'N/A')}")
    print("-----------------------------------------\n")
    input("Press Enter to return to the Main Menu...")


def manage_device_menu(devices_data):

    print("\n--- Manage Device ---")

    while True:
        selected_ip = input("Enter the IP address of the device to manage (or type 'back' to return): ").strip()

        if selected_ip.lower() == 'back':
            return

            # if ip is validated by the method from file Device, then the loop for inputing an ip address is ended.
        if Device.check_ipv4(selected_ip):
            break
        else:
            print(f"'{selected_ip}' is not a valid IPv4 address. Please try again.")


    target_device_info = next((dev for dev in devices_data if dev.get('ip_address') == selected_ip), None)

    if not target_device_info:
        print(f"Device with IP address '{selected_ip}' not found in the configuration.")
        input("\nPress Enter to continue...")
        return

    print(f"\nSelected device: {target_device_info.get('hostname', 'N/A')} ({target_device_info.get('ip_address', 'N/A')})")

    device_type = target_device_info.get('type', '').lower()

    try:
        if device_type == 'router':
            instance = Router(
                hostname=target_device_info['hostname'],
                ip_address=target_device_info['ip_address'],
                username=target_device_info['username'],
                password=target_device_info['password'],
                exec_pass=target_device_info['exec_password'],
                device_type=target_device_info['device_type']
            )
            router_configuration_menu(instance)
        elif device_type == 'switch':
            instance = Switch(
                hostname=target_device_info['hostname'],
                ip_address=target_device_info['ip_address'],
                username=target_device_info['username'],
                password=target_device_info['password'],
                exec_pass=target_device_info['exec_password'],
                device_type=target_device_info['device_type']
            )
            switch_configuration_menu(instance)
        else:
            print(f"Unsupported device type: '{target_device_info.get('type', 'N/A')}'.")
            input("\nPress Enter to continue...")
    except KeyError as e:
        print(f"Error: Device data for {selected_ip} is missing a required field: {e}")
        input("\nPress Enter to continue...")


def router_configuration_menu(router_instance: Router):
    # method for config settings on a Router
    menu_title = f"--- Router Configuration: {router_instance.hostname} ---"
    menu_items = [
        "Configure HSRP",
        "DHCP Configuration",
        "Set up RIPv2",
        "Ping another device",
        "Show IP Interface Brief",
        "Return to Main Menu"
    ]
    config_menu = TerminalMenu(menu_items, title=menu_title, clear_screen=True)

    while True:
        menu_entry_index = config_menu.show()
        if menu_entry_index is None or menu_items[menu_entry_index] == "Return to Main Menu":
            break

        selected_action = menu_items[menu_entry_index]
        action_taken = False

        if selected_action == "Configure HSRP":
            router_instance.config_hsrp()
            action_taken = True

        elif selected_action == "DHCP Configuration":
            # submenu for DHCP configuration options
            dhcp_menu_title = f"--- DHCP Configuration: {router_instance.hostname} ---"
            dhcp_menu_items = ["Configure a DHCP Server",
                               "Add Helper Address",
                               "Enable DHCP Client on interface",
                               "Return to previous menu"]
            dhcp_menu = TerminalMenu(dhcp_menu_items, title=dhcp_menu_title, clear_screen=True)

            while True:
                dhcp_menu_entry_index = dhcp_menu.show()
                if dhcp_menu_entry_index is None or dhcp_menu_items[dhcp_menu_entry_index] == "Return to previous menu":
                    break

                dhcp_choice = dhcp_menu_items[dhcp_menu_entry_index]
                if dhcp_choice == "Configure a DHCP Server":
                    router_instance.setup_dhcp()
                    action_taken = True
                    break  # Exit sub-menu after action
                elif dhcp_choice == "Add Helper Address":
                    router_instance.config_dhcp_helper()
                    action_taken = True
                    break  # Exit sub-menu after action
                elif dhcp_choice == "Enable DHCP Client on interface":
                    router_instance.get_dhcp()
                    action_taken = True
                    break

        elif selected_action == "Set up RIPv2":
            router_instance.config_ripv2()
            action_taken = True
        elif selected_action == "Ping another device":
            router_instance.ping()
            action_taken = True
        elif selected_action == "Show IP Interface Brief":
            router_instance.show_ip_interface_brief()
            action_taken = True

        if action_taken:
            input("\nOperation complete. Press Enter to continue...")


def switch_configuration_menu(switch_instance: Switch):
    # menu for Switch configuration
    menu_title = f"--- Switch Configuration: {switch_instance.hostname} ---"
    menu_items = [
        "Configure a VLAN",
        "Configure Port Security",
        "Configure STP (Spanning Tree)",
        "Ping another device",
        "Show IP Interface Brief",
        "Show VLAN Information",
        "Return to Main Menu"
    ]
    config_menu = TerminalMenu(menu_items, title=menu_title, clear_screen=True)

    while True:
        menu_entry_index = config_menu.show()
        if menu_entry_index is None or menu_items[menu_entry_index] == "Return to Main Menu":
            break

        selected_action = menu_items[menu_entry_index]
        action_taken = False

        if selected_action == "Configure a VLAN":
            switch_instance.config_vlan()
            action_taken = True
        elif selected_action == "Configure Port Security":
            switch_instance.config_security()
            action_taken = True
        elif selected_action == "Configure STP (Spanning Tree)":
            switch_instance.config_stp()
            action_taken = True
        elif selected_action == "Ping another device":
            switch_instance.ping()
            action_taken = True
        elif selected_action == "Show IP Interface Brief":
            switch_instance.show_ip_interface_brief()
            action_taken = True
        elif selected_action == "Show VLAN Information":
            switch_instance.show_vlan_brief()
            action_taken = True

        if action_taken:
            input("\nOperation complete. Press Enter to continue...")


if __name__ == "__main__":
    main()