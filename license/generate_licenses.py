#!/usr/bin/env python3
"""Generate test license keys for Midnight Spoofer"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.auth.license_generator import LicenseGenerator

def main():
    generator = LicenseGenerator()
    keys = generator.generate_multiple_keys(5)
    generator.save_keys_to_file(keys, 'license_keys.txt')

    print("Generated 5 test license keys:")
    for key in keys:
        print(f"  {key}")

if __name__ == "__main__":
    main()
