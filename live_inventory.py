import json
from getpass import getpass
from pathlib import Path

import yaml
from netmiko import ConnectHandler


INVENTORY_FILE = Path("devices.yml")


def load_devices():
    with INVENTORY_FILE.open("r", encoding="utf-8") as file:
        inventory = yaml.safe_load(file)

    return inventory["devices"]


def get_arista_inventory(device, username, password):
    connection_params = {
        "device_type": device["device_type"],
        "host": device["host"],
        "port": device.get("port", 22),
        "username": username,
        "password": password,
    }

    print(f"\nConnecting to {device['name']} ({device['host']})...")

    with ConnectHandler(**connection_params) as connection:
        version_output = connection.send_command("show version | json")
        hostname_output = connection.send_command("show hostname | json")

    version = json.loads(version_output)
    hostname = json.loads(hostname_output)

    return {
        "hostname": hostname.get("hostname", device["name"]),
        "vendor": "Arista",
        "model": version.get("modelName", "Unknown"),
        "serial_number": version.get("serialNumber", "Unknown"),
        "software_version": version.get("version", "Unknown"),
        "architecture": version.get("architecture", "Unknown"),
        "uptime": version.get("uptime", "Unknown"),
        "management_ip": device["host"],
    }


def display_inventory(inventory):
    print("\nNetwork Device Inventory")
    print("=" * 70)

    for device in inventory:
        print(f"Hostname:         {device['hostname']}")
        print(f"Vendor:           {device['vendor']}")
        print(f"Model:            {device['model']}")
        print(f"Serial Number:    {device['serial_number']}")
        print(f"Software Version: {device['software_version']}")
        print(f"Architecture:     {device['architecture']}")
        print(f"Uptime:           {device['uptime']}")
        print(f"Management IP:    {device['management_ip']}")
        print("-" * 70)


def main():
    devices = load_devices()

    username = input("Username: ")
    password = getpass("Password: ")

    inventory = []

    for device in devices:
        try:
            if device["device_type"] == "arista_eos":
                result = get_arista_inventory(device, username, password)
                inventory.append(result)
            else:
                print(
                    f"Unsupported device type: "
                    f"{device['device_type']}"
                )

        except Exception as error:
            print(
                f"Failed to connect to {device['name']} "
                f"({device['host']}): {error}"
            )

    display_inventory(inventory)


if __name__ == "__main__":
    main()
