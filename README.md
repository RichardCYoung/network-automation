# Network Automation

A practical multi-vendor network automation project for discovering, collecting, and reporting network device inventory.

This project demonstrates the use of Python, Netmiko, YAML, and Git to automate common network engineering tasks across multiple network operating systems.

## Current Capabilities

The inventory collector connects to lab network devices over SSH and automatically collects:

- Hostname
- Vendor
- Hardware model
- Serial number
- Software version
- Architecture/platform information
- System uptime
- Management IP address

The collected information is displayed as a consolidated network inventory report.

## Supported Platforms

Currently tested against:

- Arista EOS / vEOS
- Cisco Nexus / NX-OS
- Juniper Junos
- Dell EMC Networking OS9

The lab currently includes physical and virtual network devices representing multiple vendors and operating systems.

## Project Structure

```text
network-automation/
├── live_inventory.py
├── devices.yml
├── requirements.txt
└── README.md


ive_inventory.py
Main Python inventory collector.
The script:
1. Reads devices from the YAML inventory
2. Groups devices by credential group
3. Securely prompts for credentials at runtime
4. Connects to devices using Netmiko
5. Executes vendor-specific commands
6. Parses device information
7. Produces a consolidated inventory report
devices.yml
Defines the network devices and their connection parameters.
Example:

devices:
  - name: cisco-nexus-01
    device_type: cisco_nxos
    host: 10.100.1.101
    port: 22
    credential_group: lab-cisco


Credentials are deliberately not stored in the YAML inventory.
Credential Handling
Credentials are requested interactively when the script runs.
Devices can share a credential group, allowing credentials to be entered once and reused during that execution.
For example:

Credentials for: lab-cisco
Username:
Password:

Passwords are entered securely and are not displayed on screen or stored in the repository.
Example Inventory
Example sanitized output:

Network Device Inventory
================================================================================

Hostname:         LAB-ARISTA-SW-01
Vendor:           Arista
Model:            vEOS-lab
Software Version: 4.x
Management IP:    10.x.x.x

Hostname:         LAB-JUNIPER-SW-01
Vendor:           Juniper
Model:            ex2200-48p-4g
Software Version: 12.x
Management IP:    192.168.x.x

Hostname:         LAB-NXOS-SW-01
Vendor:           Cisco
Model:            Nexus9000 C9300v
Software Version: 10.x
Management IP:    10.x.x.x

Hostname:         LAB-DELL-SW-01
Vendor:           Dell EMC
Model:            S3048-ON
Software Version: 9.x
Management IP:    192.168.x.x

Installation
Clone the repository:

git clone https://github.com/RichardCYoung/network-automation.git
cd network-automation

Create a Python virtual environment:

python -m venv .venv

Activate the virtual environment on Windows:

.venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt

Run the inventory collector:

python live_inventory.py


Technologies
- Python
- Netmiko
- PyYAML
- SSH
- Git / GitHub
- Arista EOS
- Cisco NX-OS
- Juniper Junos
- Dell EMC Networking OS9
Roadmap
Planned additions include:
- CSV and JSON inventory export
- Configuration backup
- Interface and VLAN auditing
- Configuration compliance validation
- Palo Alto firewall automation
- Meraki Dashboard API integration
- NetBox integration
- Ansible network automation
- Azure network auditing
- Automated reporting
Security
This repository contains lab-built and sanitized examples only.
No customer, employer, or production credentials, configurations, certificates, API keys, or sensitive network information are published.


## Configuration Backup

The repository also includes an early-stage multi-vendor configuration backup workflow.

The goal is to connect to devices defined in the existing YAML inventory and retrieve their active configuration using vendor-specific commands.

Currently targeted platforms include:

- Arista EOS
- Cisco NX-OS
- Juniper Junos
- Dell EMC Networking OS9

Example workflow:

1. Read devices from `devices.yml`
2. Prompt securely for credentials
3. Connect to each device using Netmiko
4. Run the appropriate configuration command for each vendor
5. Save the configuration using the device hostname
6. Record the date and time of the backup
7. Report successful and failed backups

Example backup structure:

```text
backups/
├── E2-ARISTA-SW-01/
│   └── 2026-09-13_running-config.txt
├── E2-NXOS-SW-1/
│   └── 2026-09-13_running-config.txt
├── n4t-sw01/
│   └── 2026-09-13_configuration.txt
└── SW03/
    └── 2026-09-13_running-config.txt

For the commit message use:

```text
Improve project documentation and usage examples

## Configuration Backup

The repository also includes an early-stage multi-vendor configuration backup workflow.

The goal is to connect to devices defined in the existing YAML inventory and retrieve their active configuration using vendor-specific commands.

Currently targeted platforms include:

- Arista EOS
- Cisco NX-OS
- Juniper Junos
- Dell EMC Networking OS9

Example workflow:

1. Read devices from `devices.yml`
2. Prompt securely for credentials
3. Connect to each device using Netmiko
4. Run the appropriate configuration command for each vendor
5. Save the configuration using the device hostname
6. Record the date and time of the backup
7. Report successful and failed backups

Example backup structure:

```text
backups/
├── E2-ARISTA-SW-01/
│   └── 2026-09-13_running-config.txt
├── E2-NXOS-SW-1/
│   └── 2026-09-13_running-config.txt
├── n4t-sw01/
│   └── 2026-09-13_configuration.txt
└── SW03/
    └── 2026-09-13_running-config.txt

## Interface and VLAN Audit

The repository also includes an early-stage interface and VLAN auditing workflow.

The goal is to collect interface and VLAN information from multiple network vendors and normalize the results into a common report.

Currently targeted platforms include:

- Arista EOS
- Cisco NX-OS
- Juniper Junos
- Dell EMC Networking OS9

Planned audit data includes:

- Interface name
- Administrative status
- Operational status
- Interface description
- Access or trunk mode
- Assigned VLAN
- Native VLAN
- Allowed VLANs
- Speed
- Duplex
- Error counters
- Management IP association where applicable

Example workflow:

1. Read devices from `devices.yml`
2. Prompt securely for credentials
3. Connect to each device using Netmiko
4. Run vendor-specific interface and VLAN commands
5. Parse the output
6. Normalize the data into a common format
7. Export the results to CSV or JSON
8. Highlight inconsistent or unexpected VLAN assignments

Example vendor commands:

| Platform | Interface Command | VLAN Command |
| --- | --- | --- |
| Arista EOS | `show interfaces status` | `show vlan` |
| Cisco NX-OS | `show interface status` | `show vlan brief` |
| Juniper Junos | `show interfaces terse` | `show vlans` |
| Dell OS9 | `show interfaces status` | `show vlan` |

Example normalized output:

```text
Hostname        Interface   Status   Mode    VLAN   Description
----------------------------------------------------------------
LAB-NXOS-SW-1   Eth1/1      up       trunk   10     ESXi-Uplink
LAB-NXOS-SW-1   Eth1/2      up       access  20     Server-01
LAB-JUNIPER-01  ge-0/0/1    up       access  10     Management
LAB-DELL-01     Te1/49      up       trunk   10     Core-Uplink

