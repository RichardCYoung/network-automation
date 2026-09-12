def main():
    devices = load_devices()

    credentials = {}
    inventory = []

    for device in devices:
        try:
            credential_group = device.get("credential_group", "default")

            if credential_group not in credentials:
                print(f"\nCredentials for: {credential_group}")
                username = input("Username: ")
                password = getpass("Password: ")

                credentials[credential_group] = {
                    "username": username,
                    "password": password,
                }

            username = credentials[credential_group]["username"]
            password = credentials[credential_group]["password"]

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

            else:
                print(
                    f"Unsupported device type: "
                    f"{device['device_type']}"
                )
                continue

            inventory.append(result)

        except Exception as error:
            print(
                f"Failed to connect to {device['name']} "
                f"({device['host']}): {error}"
            )

    display_inventory(inventory)
