"""
MAC-specific configurations and paths
"""

VENDOR_OUI = {
    "Cisco": "00:1C:58",
    "Dell": "00:1A:A0",
    "HP": "00:1A:4B",
    "Intel": "00:1B:21",
    "Apple": "00:1D:4F",
    "Samsung": "00:1E:7D",
    "Microsoft": "00:1D:60",
    "Realtek": "00:1E:68",
    "TP-Link": "00:1D:0F",
    "ASUS": "00:1A:92"
}

MAC_REGISTRY_BASE = r"SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}"

NETWORK_INTERFACE_PATHS = {
    'registry_locations': [
        # Placeholder for future registry paths related to network interfaces
    ],
    'system_locations': [
        # Placeholder for future system paths for network configurations
    ]
}
