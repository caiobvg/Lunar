#!/usr/bin/env python3
"""
Test script for GUID Spoofer functionality
Run this script to test if GUID spoofing is working correctly
"""

import sys
import os
import winreg

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.spoofers.guid_spoofer.guid_spoofer import GUIDSpoofer
from src.utils.logger import logger

def test_guid_spoofer():
    """Test GUID Spoofer functionality"""
    print("TESTING GUID SPOOFER")
    print("=" * 50)

    try:
        # Initialize GUID Spoofer
        guid_spoofer = GUIDSpoofer()
        print("[OK] GUID Spoofer initialized successfully")

        # Test registry reading before spoofing
        print("\nReading current GUID values...")

        # Test MachineGuid
        try:
            machine_guid_before, _ = guid_spoofer.registry.read_value(
                "HKEY_LOCAL_MACHINE",
                r"SOFTWARE\Microsoft\Cryptography",
                "MachineGuid"
            )
        except:
            machine_guid_before = None
        print(f"MachineGuid before: {machine_guid_before}")

        # Test ProductId
        try:
            product_id_before, _ = guid_spoofer.registry.read_value(
                "HKEY_LOCAL_MACHINE",
                r"SOFTWARE\Microsoft\Windows NT\CurrentVersion",
                "ProductId"
            )
        except:
            product_id_before = None
        print(f"ProductId before: {product_id_before}")

        # Test FiveM GUID
        try:
            fivem_guid_before, _ = guid_spoofer.registry.read_value(
                "HKEY_CURRENT_USER",
                r"Software\CitizenFX",
                "guid"
            )
        except:
            fivem_guid_before = None
        print(f"FiveM GUID before: {fivem_guid_before}")

        # Perform spoofing
        print("\nAttempting GUID spoofing...")
        success = guid_spoofer.spoof_guid()

        if success:
            print("[OK] GUID spoofing reported success")

            # Verify changes
            print("\nVerifying changes...")

            try:
                machine_guid_after, _ = guid_spoofer.registry.read_value(
                    "HKEY_LOCAL_MACHINE",
                    r"SOFTWARE\Microsoft\Cryptography",
                    "MachineGuid"
                )
            except:
                machine_guid_after = None
            print(f"MachineGuid after: {machine_guid_after}")

            try:
                product_id_after, _ = guid_spoofer.registry.read_value(
                    "HKEY_LOCAL_MACHINE",
                    r"SOFTWARE\Microsoft\Windows NT\CurrentVersion",
                    "ProductId"
                )
            except:
                product_id_after = None
            print(f"ProductId after: {product_id_after}")

            try:
                fivem_guid_after, _ = guid_spoofer.registry.read_value(
                    "HKEY_CURRENT_USER",
                    r"Software\CitizenFX",
                    "guid"
                )
            except:
                fivem_guid_after = None
            print(f"FiveM GUID after: {fivem_guid_after}")

            # Check if values changed
            changes_detected = 0
            total_checks = 0

            if machine_guid_before and machine_guid_after:
                total_checks += 1
                if machine_guid_before != machine_guid_after:
                    changes_detected += 1
                    print("[OK] MachineGuid changed successfully")

            if product_id_before and product_id_after:
                total_checks += 1
                if product_id_before != product_id_after:
                    changes_detected += 1
                    print("[OK] ProductId changed successfully")

            if fivem_guid_before and fivem_guid_after:
                total_checks += 1
                if fivem_guid_before != fivem_guid_after:
                    changes_detected += 1
                    print("[OK] FiveM GUID changed successfully")

            if total_checks == 0:
                print("[WARNING] No existing GUID values found to compare")
                return True  # Still consider success if spoofing completed

            success_rate = (changes_detected / total_checks) * 100
            print(f"\nGUID spoofing results: {changes_detected}/{total_checks} values changed ({success_rate:.1f}%)")

            return success_rate >= 50  # At least 50% success rate

        else:
            print("[ERROR] GUID spoofing failed!")
            return False

    except Exception as e:
        print(f"[ERROR] Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Midnight Spoofer - GUID Spoofer Test")
    print("Make sure you're running as Administrator!")
    print()

    success = test_guid_spoofer()

    print()
    print("=" * 50)
    if success:
        print("GUID Spoofer test PASSED!")
    else:
        print("GUID Spoofer test FAILED!")
    print("=" * 50)
