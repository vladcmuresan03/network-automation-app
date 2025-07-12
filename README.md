Python Command-Line Application for Network Automation and Configuration

This project is a Python application with the purpose of running on a Linux CLI and automating the configuration of Cisco network devices such as routers and switches. The application was tested in an emulated GNS3 environment and it provides an user-friendly interface which allows the user to perform various configurations just by providing the parameters needed, which reduces the risk of manual error that could happen when writing these commands by hand. Also, if connected to an access mode port of a switch, the script is able to connect to a larger network through SSH and configure devices remotely, without having to reconnect the end-device to another device.

Prerequisites:
- Python3 installed: verify using 'python3 --version'
- Required Python libraries: 'pip3 install netmiko simple-term-menu'
- Creation and basic configuration of a GNS3 network using Cisco devices.
- Configure SSH on each device:
```
crypto key generate rsa
How many bits in the modulus [512]: 1024
line vty 0 15
transport input ssh
password cisco
login local
username *user* password *pass*
```
- Add a 'NetworkAutomation' end-device (or an equivalent Linux CLI VM) to the topology and link it to a switch.
- Configure the switch port used for the Linux machine to be in access-mode:
'interface <x>'
'switchport mode access'
'switchport access vlan <y>'


Application Setup:
1. Create a directory for the application
'mkdir NetworkAutomation'
'cd NetworkAutomation'
2. Create the Python files required and paste the content of the files.
Follow these steps for each of these files: Menu.py, Device.py, Router.py, Switch.py
'copy the content of a file'
'nano <filename>.py'
'LeftClick after copying the code'
'CTRL+X'
'Y'
'Enter'
3. Create and fill the devices.json file using the device's properties (or repeat previous step for file 'devices.json')
Example .json file:
'''
  {
    "type": "switch",
    "hostname": "SW20",
    "ip_address": "20.20.20.5",
    "username": "admin",
    "password": "cisco",
    "exec_password": "pass",
    "device_type": "cisco_ios"
  },
  {
    "type": "router",
    "hostname": "R1",
    "ip_address": "192.168.1.3",
    "username": "admin",
    "password": "cisco",
    "exec_password": "pass",
    "device_type": "cisco_ios"
  }
'''

4. Run the application 
'python3 Menu.py'

Application Navigation:
The menus of this application can be easily navigated using the arrow keys and the enter key to select the highlighted menu option. Some configurations require the user to input data following the script's instructions.
