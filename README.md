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
