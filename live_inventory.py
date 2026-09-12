import json
import re
from getpass import getpass
from pathlib import Path

import yaml
from netmiko import ConnectHandler


INVENTORY_FILE = Path("devices.yml")


# ---------------------------------------------------------
# Inventory / utility functions
# ---------------------------------------------------------

def load_devices():
    """Load network devices from devices.yml."""

    with INVENTORY_FILE.open("r", encoding="utf-8") as file:
        inventory = yaml.safe_load(file)

    if not inventory or "devices" not in inventory:
        raise ValueError("No 'devices' section found in devices.yml")

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
    """
    Build Netmiko connection parameters.

    dell_os9 is our logical inventory name.
    Netmiko calls the driver dell_force10.
    """

    device_type = device["device_type"]

    if device_type == "dell_os9":
        netmiko_device_type = "dell_force10"
    else:
        netmiko_device_type = device_type

    return {
        "device_type": netmiko_device_type,
        "host": device["host"],
        "port": device.get("port", 22),
        "username": username,
        "password": password,
    }


# ---------------------------------------------------------
# Arista EOS
# ---------------------------------------------------------

def get_arista_inventory(device, username, password):
    """Collect inventory information from Arista EOS."""

    print(
        f"\nConnecting to {device['name']} "
        f"({device['host']})..."
    )

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
    hostname_data = json.loads(hostname_output)

    return {
        "hostname": hostname_data.get(
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


# ---------------------------------------------------------
# Juniper Junos
# ---------------------------------------------------------

def get_juniper_inventory(device, username, password):
    """Collect inventory information from Juniper Junos."""

    print(
        f"\nConnecting to {device['name']} "
        f"({device['host']})..."
    )

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

    # -------------------------
    # Parse show version
    # -------------------------

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

        elif line.startswith("Junos:"):

            software_version = line.split(
                ":",
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

        # Older Junos releases such as EX2200
        elif (
            software_version == "Unknown"
            and "JUNOS" in line.upper()
        ):

            version_match = re.search(
                r"\[(\d+\.\d+R[\w.\-]+)\]",
                line,
            )

            if version_match:
                software_version = version_match.group(1)

    # -------------------------
    # Parse chassis information
    # -------------------------

    for line in hardware_output.splitlines():

        line = line.strip()

        if line.startswith("Chassis"):

            parts = line.split()

            if len(parts) >= 2:
                serial_number = parts[1]

            break

    # -------------------------
    # Parse uptime
    # -------------------------

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


# ---------------------------------------------------------
# Cisco Nexus / NX-OS
# ---------------------------------------------------------

def get_cisco_nxos_inventory(device, username, password):
    """Collect inventory information from Cisco NX-OS."""

    print(
        f"\nConnecting to {device['name']} "
        f"({device['host']})..."
    )

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

        if line.startswith("Device name:"):

            hostname = line.split(
                ":",
                1,
            )[1].strip()

        elif line.lower().startswith("cisco nexus"):

            model = (
                line.replace(
                    "cisco ",
                    "",
                    1,
                )
                .replace(
                    " Chassis",
                    "",
                )
                .strip()
            )

        elif line.startswith("NXOS: version"):

            software_version = line.split(
                "NXOS: version",
                1,
            )[1].strip()

            if "[" in software_version:

                software_version = (
                    software_version
                    .split("[", 1)[0]
                    .strip()
                )

        elif line.startswith("Processor Board ID"):

            serial_number = line.split(
                "Processor Board ID",
                1,
            )[1].strip()

        elif line.startswith("Kernel uptime is"):

            uptime = line.replace(
                "Kernel uptime is",
                "",
                1,
            ).strip()

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


# ---------------------------------------------------------
# Dell EMC Networking OS9
# ---------------------------------------------------------

def get_dell_os9_inventory(device, username, password):
    """Collect inventory information from Dell EMC Networking OS9."""

    print(
        f"\nConnecting to {device['name']} "
        f"({device['host']})..."
    )

    connection_params = get_connection_params(
        device,
        username,
        password,
    )

    with ConnectHandler(**connection_params) as connection:

        prompt = connection.find_prompt()

        version_output = connection.send_command(
            "show version"
        )

        inventory_output = connection.send_command(
            "show inventory"
        )

    hostname = (
        prompt
        .replace("#", "")
        .replace(">", "")
        .strip()
    )

    model = "Unknown"
    serial_number = "Unknown"
    software_version = "Unknown"
    architecture = "Unknown"
    uptime = "Unknown"

    # -------------------------
    # Parse show version
    # -------------------------

    for line in version_output.splitlines():

        line = line.strip()

        if line.startswith(
            "Dell EMC Application Software Version:"
        ):

            software_version = line.split(
                ":",
                1,
            )[1].strip()

        elif line.startswith("System Type:"):

            model = line.split(
                ":",
                1,
            )[1].strip()

        elif line.startswith("Control Processor:"):

            architecture = line.split(
                ":",
                1,
            )[1].strip()

        elif (
            "Dell EMC Networking OS uptime is"
            in line
        ):

            uptime = line.split(
                "uptime is",
                1,
            )[1].strip()

    # -------------------------
    # Try to obtain Dell serial/service tag
    # -------------------------

    for line in inventory_output.splitlines():

        line = line.strip()

        if "Service Tag" in line:

            if ":" in line:

                candidate = line.split(
                    ":",
                    1,
                )[1].strip()

                if candidate:
                    serial_number = candidate

        elif (
            "Serial Number" in line
            and serial_number == "Unknown"
        ):

            if ":" in line:

                candidate = line.split(
                    ":",
                    1,
                )[1].strip()

                if candidate:
                    serial_number = candidate

    return {
        "hostname": hostname,
        "vendor": "Dell EMC",
        "model": model,
        "serial_number": serial_number,
        "software_version": software_version,
        "architecture": architecture,
        "uptime": uptime,
        "management_ip": device["host"],
    }


# ---------------------------------------------------------
# Display
# ---------------------------------------------------------

def display_inventory(inventory):
    """Display all collected network inventory."""

    print("\n")
    print("Network Device Inventory")
    print("=" * 80)

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

        print("-" * 80)


# ---------------------------------------------------------
# Main program
# ---------------------------------------------------------

def main():
    """Run multi-vendor network inventory collection."""

    devices = load_devices()

    credentials = {}
    inventory = []

    for device in devices:

        try:

            credential_group = device.get(
                "credential_group",
                "default",
            )

            # Ask once per credential group
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

            device_type = device["device_type"]

            # -------------------------
            # Select vendor collector
            # -------------------------

            if device_type == "arista_eos":

                result = get_arista_inventory(
                    device,
                    username,
                    password,
                )

            elif device_type == "juniper_junos":

                result = get_juniper_inventory(
                    device,
                    username,
                    password,
                )

            elif device_type == "cisco_nxos":

                result = get_cisco_nxos_inventory(
                    device,
                    username,
                    password,
                )

            elif device_type == "dell_os9":

                result = get_dell_os9_inventory(
                    device,
                    username,
                    password,
                )

            else:

                print(
                    f"\nUnsupported device type: "
                    f"{device_type} "
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
