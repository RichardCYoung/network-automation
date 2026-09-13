"""
Multi-vendor network configuration compliance checker.

This module is currently under development.

Planned support:
- Arista EOS
- Cisco NX-OS
- Juniper Junos
- Dell EMC Networking OS9
"""


COMPLIANCE_CHECKS = {
    "ssh_enabled": {
        "description": "SSH Enabled",
        "severity": "HIGH",
    },
    "telnet_disabled": {
        "description": "Telnet Disabled",
        "severity": "HIGH",
    },
    "ntp_configured": {
        "description": "NTP Configured",
        "severity": "MEDIUM",
    },
    "dns_configured": {
        "description": "DNS Configured",
        "severity": "MEDIUM",
    },
    "syslog_configured": {
        "description": "Syslog Configured",
        "severity": "MEDIUM",
    },
    "aaa_configured": {
        "description": "AAA Configured",
        "severity": "HIGH",
    },
}


def display_compliance_checks():
    """Display currently defined compliance checks."""

    print("Network Configuration Compliance Checker")
    print("=" * 65)

    print(
        f"{'Check':25}"
        f"{'Severity':12}"
        f"Description"
    )

    print("-" * 65)

    for check_name, check in COMPLIANCE_CHECKS.items():

        print(
            f"{check_name:25}"
            f"{check['severity']:12}"
            f"{check['description']}"
        )


def main():
    """Run configuration compliance framework."""

    display_compliance_checks()

    print()
    print(
        "Configuration compliance functionality "
        "is currently under development."
    )


if __name__ == "__main__":
    main()
