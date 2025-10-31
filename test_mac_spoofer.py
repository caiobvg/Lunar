#!/usr/bin/env python3
"""
Test script for MAC Spoofer functionality
Run this script to test if MAC spoofing is working correctly
"""

import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.spoofers.mac_spoofer.mac_spoofer import MACSpoofer
from src.utils.logger import logger

def test_mac_spoofer():
    """Test MAC Spoofer functionality"""
    print("TESTING MAC SPOOFER")
    print("=" * 50)

    try:
        # Initialize MAC Spoofer
        mac_spoofer = MACSpoofer()
        print("[OK] MAC Spoofer initialized successfully")

        # Get available interfaces
        interfaces = mac_spoofer.get_interfaces()
        if not interfaces:
            print("[ERROR] No network interfaces found!")
            return False

        print(f"Found {len(interfaces)} network interface(s):")
        for i, iface in enumerate(interfaces):
            print(f"  {i+1}. {iface['name']} - MAC: {iface['mac_address']}")

        # Test with first interface
        test_interface = interfaces[0]['name']
        print(f"\nTesting with interface: {test_interface}")

        # Get current MAC
        current_mac = mac_spoofer.get_current_mac(test_interface)
        print(f"MAC before spoofing: {current_mac}")

        if not current_mac:
            print("[ERROR] Could not read current MAC address!")
            return False

        # Test spoofing
        print("Attempting MAC spoofing...")
        success = mac_spoofer.spoof_mac_address(test_interface)

        if success:
            print("[OK] MAC spoofing reported success")

            # Verify the change
            new_mac = mac_spoofer.get_current_mac(test_interface)
            print(f"MAC after spoofing: {new_mac}")

            if new_mac and new_mac != current_mac:
                print("[OK] MAC address successfully changed!")
                print(f"   Before: {current_mac}")
                print(f"   After:  {new_mac}")
                return True
            else:
                print("[ERROR] MAC address did not change!")
                return False
        else:
            print("[ERROR] MAC spoofing failed!")
            return False

    except Exception as e:
        print(f"[ERROR] Test failed with error: {e}")
        return False

if __name__ == "__main__":
    print("Midnight Spoofer - MAC Spoofer Test")
    print("Make sure you're running as Administrator!")
    print()

    success = test_mac_spoofer()

    print()
    print("=" * 50)
    if success:
        print("MAC Spoofer test PASSED!")
    else:
        print("MAC Spoofer test FAILED!")
    print("=" * 50)
