from datetime import datetime
from pathlib import Path

import yaml


INVENTORY_FILE = Path("devices.yml")


def load_devices():
    with INVENTORY_FILE.open("r", encoding="utf-8") as file:
        inventory = yaml.safe_load(file)

    return inventory["devices"]


def display_inventory(devices):
    print(f"Network Inventory Report - {datetime.now():%Y-%m-%d %H:%M:%S}")
    print("-" * 85)
    print(f"{'HOSTNAME':<15}{'VENDOR':<12}{'MODEL':<18}{'VERSION':<15}{'MGMT IP'}")
    print("-" * 85)

    for device in devices:
        print(
            f"{device['hostname']:<15}"
            f"{device['vendor']:<12}"
            f"{device['model']:<18}"
            f"{device['version']:<15}"
            f"{device['management_ip']}"
        )


def main():
    devices = load_devices()
    display_inventory(devices)


if __name__ == "__main__":
    main()
