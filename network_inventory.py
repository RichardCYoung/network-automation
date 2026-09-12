from datetime import datetime

devices = [
    {
        "hostname": "R1",
        "vendor": "Cisco",
        "model": "CSR1000v",
        "version": "17.x",
        "management_ip": "192.168.1.10",
    },
    {
        "hostname": "SW1",
        "vendor": "Arista",
        "model": "vEOS",
        "version": "4.34.7M",
        "management_ip": "192.168.1.11",
    },
    {
        "hostname": "SW2",
        "vendor": "Juniper",
        "model": "vEX",
        "version": "23.x",
        "management_ip": "192.168.1.12",
    },
]

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
