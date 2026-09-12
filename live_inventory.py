import json
from getpass import getpass
from pathlib import Path

import yaml
from netmiko import ConnectHandler


INVENTORY_FILE = Path("devices.yml")


def load_devices():
    """Load devices from YAML inventory."""

    with INVENTORY_FILE.open("r", encoding="utf-8") as file:
        inventory = yaml.safe_load(file)

    return inventory["devices"]


def format_uptime(seconds):
    """Convert seconds to a human-readable uptime."""

    try:
        seconds = int(float(seconds))
    except (TypeError, ValueError):
        return "Unknown"

    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    return f"{days}d {hours}h {minutes}m {seconds}s"


def get_connection_params(device, username, password):
    """Build Netmiko connection parameters."""

    return {
        "device_type": device["device_type"],
        "host": device["host"],
        "port": device.get("port", 22),
        "username": username,
        "password": password,
    }


def get_arista_inventory(device, username, password):
    """Collect inventory information from Arista EOS."""

    print(f"\nConnecting to {device['name']} ({device['host']})...")

    connection_params = get_connection_params(
        device,
        username,
        password,
    )

    with ConnectHandler(**connection_params) as connection:
        version_output = connection.send_command(
            "show version | json"
        )

        hostname_output = connection.send_command(
            "show hostname | json"
        )

    version = json.loads(version_output)
    hostname = json.loads(hostname_output)

    return {
        "hostname": hostname.get(
            "hostname",
            device["name"],
        ),
        "vendor": "Arista",
        "model": version.get(
            "modelName",
            "Unknown",
        ),
        "serial_number": version.get(
            "serialNumber",
            "Unknown",
        ),
        "software_version": version.get(
            "version",
            "Unknown",
        ),
        "architecture": version.get(
            "architecture",
            "Unknown",
        ),
        "uptime": format_uptime(
            version.get("uptime", 0)
        ),
        "management_ip": device["host"],
    }


def get_juniper_inventory(device, username, password):
    """Collect inventory information from Juniper Junos."""

    print(f"\nConnecting to {device['name']} ({device['host']})...")

    connection_params = get_connection_params(
        device,
        username,
        password,
    )

    with ConnectHandler(**connection_params) as connection:
        version_output = connection.send_command(
            "show version"
        )

        hardware_output = connection.send_command(
            "show chassis hardware"
        )

        uptime_output = connection.send_command(
            "show system uptime"
        )

    hostname = "Unknown"
    model = "Unknown"
    serial_number = "Unknown"
    software_version = "Unknown"
    uptime = "Unknown"

    for line in version_output.splitlines():
        line = line.strip()

        if line.startswith("Hostname:"):
            hostname = line.split(
                ":",
                1,
            )[1].strip()

        elif line.startswith("Model:"):
            model = line.split(
                ":",
                1,
            )[1].strip()

        elif "Junos:" in line:
            software_version = line.split(
                "Junos:",
                1,
            )[1].strip()

        elif line.startswith("version "):
            software_version = (
                line.replace(
                    "version ",
                    "",
                    1,
                )
                .replace(";", "")
                .strip()
            )

    for line in hardware_output.splitlines():
        line = line.strip()

        if line.startswith("Chassis"):
            parts = line.split()

            if len(parts) >= 2:
                serial_number = parts[1]

            break

    for line in uptime_output.splitlines():
        line = line.strip()

        if line.startswith("System booted:"):
            uptime = line.replace(
                "System booted:",
                "",
                1,
            ).strip()

            break

    return {
        "hostname": hostname,
        "vendor": "Juniper",
        "model": model,
        "serial_number": serial_number,
        "software_version": software_version,
        "architecture": "N/A",
        "uptime": uptime,
        "management_ip": device["host"],
    }


def get_cisco_inventory(device, username, password):
    """Collect inventory information from Cisco IOS/IOS-XE."""

    print(f"\nConnecting to {device['name']} ({device['host']})...")

    connection_params = get_connection_params(
        device,
        username,
        password,
    )

    with ConnectHandler(**connection_params) as connection:
        version_output = connection.send_command(
            "show version"
        )

    hostname = "Unknown"
    model = "Unknown"
    serial_number = "Unknown"
    software_version = "Unknown"
    uptime = "Unknown"

    for line in version_output.splitlines():
        line = line.strip()

        if " uptime is " in line:
            hostname, uptime = line.split(
                " uptime is ",
                1,
            )

            hostname = hostname.strip()
            uptime = uptime.strip()

        elif (
            "Cisco IOS XE Software" in line
            and "Version" in line
        ):
            software_version = (
                line.split(
                    "Version",
                    1,
                )[1]
                .split(",", 1)[0]
                .strip()
            )

        elif (
            line.startswith("Cisco IOS Software")
            and "Version" in line
        ):
            software_version = (
                line.split(
                    "Version",
                    1,
                )[1]
                .split(",", 1)[0]
                .strip()
            )

        elif line.startswith("Model Number"):
            model = line.split(
                ":",
                1,
            )[1].strip()

        elif line.startswith("System serial number"):
            serial_number = line.split(
                ":",
                1,
            )[1].strip()

        elif "Processor board ID" in line:
            if serial_number == "Unknown":
                serial_number = line.split(
                    "Processor board ID",
                    1,
                )[1].strip()

    return {
        "hostname": hostname,
        "vendor": "Cisco",
        "model": model,
        "serial_number": serial_number,
        "software_version": software_version,
        "architecture": "N/A",
        "uptime": uptime,
        "management_ip": device["host"],
    }


def display_inventory(inventory):
    """Display collected inventory."""

    print("\n")
    print("Network Device Inventory")
    print("=" * 75)

    if not inventory:
        print("No inventory was collected.")
        return

    for device in inventory:
        print(
            f"Hostname:         "
            f"{device['hostname']}"
        )

        print(
            f"Vendor:           "
            f"{device['vendor']}"
        )

        print(
            f"Model:            "
            f"{device['model']}"
        )

        print(
            f"Serial Number:    "
            f"{device['serial_number']}"
        )

        print(
            f"Software Version: "
            f"{device['software_version']}"
        )

        print(
            f"Architecture:     "
            f"{device['architecture']}"
        )

        print(
            f"Uptime:           "
            f"{device['uptime']}"
        )

        print(
            f"Management IP:    "
            f"{device['management_ip']}"
        )

        print("-" * 75)


def main():
    """Run network inventory collection."""

    devices = load_devices()

    credentials = {}
    inventory = []

    for device in devices:

        try:
            credential_group = device.get(
                "credential_group",
                "default",
            )

            if credential_group not in credentials:

                print(
                    f"\nCredentials for: "
                    f"{credential_group}"
                )

                username = input(
                    "Username: "
                )

                password = getpass(
                    "Password: "
                )

                credentials[credential_group] = {
                    "username": username,
                    "password": password,
                }

            username = credentials[
                credential_group
            ]["username"]

            password = credentials[
                credential_group
            ]["password"]

            if device["device_type"] == "arista_eos":

                result = get_arista_inventory(
                    device,
                    username,
                    password,
                )

            elif device["device_type"] == "juniper_junos":

                result = get_juniper_inventory(
                    device,
                    username,
                    password,
                )

            elif device["device_type"] == "cisco_ios":

                result = get_cisco_inventory(
                    device,
                    username,
                    password,
                )

            else:

                print(
                    f"\nUnsupported device type: "
                    f"{device['device_type']} "
                    f"for {device['name']}"
                )

                continue

            inventory.append(result)

        except Exception as error:

            print(
                f"\nFailed to collect inventory from "
                f"{device['name']} "
                f"({device['host']}):"
            )

            print(error)

    display_inventory(inventory)


if __name__ == "__main__":
    main()
