import secrets
import string
import json
import os
from datetime import datetime

class LicenseGenerator:
    """Generate license keys for Midnight Spoofer"""

    def __init__(self):
        self.license_format = "MDSF-{segment1}-{segment2}-{segment3}"

    def generate_license_key(self) -> str:
        """Generate a single license key in MDSF-XXXX-XXXX-XXXX format"""
        segments = []
        for _ in range(3):
            segment = ''.join(secrets.choice(string.ascii_uppercase + string.digits)
                             for _ in range(4))
            segments.append(segment)
        return f"MDSF-{'-'.join(segments)}"

    def generate_multiple_keys(self, count: int) -> list[str]:
        """Generate multiple unique license keys"""
        keys = set()
        while len(keys) < count:
            keys.add(self.generate_license_key())
        return list(keys)

    def save_keys_to_file(self, keys: list[str], filename: str = "license_keys.txt"):
        """Save license keys to a file with metadata"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# Midnight Spoofer License Keys\n")
            f.write(f"# Generated: {timestamp}\n")
            f.write(f"# Total Keys: {len(keys)}\n")
            f.write("#" + "="*50 + "\n\n")

            for i, key in enumerate(keys, 1):
                f.write(f"{key}\n")

        print(f"Generated {len(keys)} license keys and saved to {filename}")

    def validate_license_format(self, license_key: str) -> bool:
        """Validate license key format"""
        if not license_key or not license_key.startswith("MDSF-"):
            return False

        parts = license_key.split("-")
        if len(parts) != 4:
            return False

        # Check each segment
        for part in parts[1:]:
            if len(part) != 4:
                return False
            if not all(c in string.ascii_uppercase + string.digits for c in part):
                return False

        return True

def main():
    """Command line interface for license generation"""
    generator = LicenseGenerator()

    try:
        count = int(input("How many license keys to generate? "))
        if count <= 0:
            print("Please enter a positive number")
            return

        keys = generator.generate_multiple_keys(count)

        # Save to file
        filename = f"license_keys_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        generator.save_keys_to_file(keys, filename)

        # Display first few keys
        print(f"\nFirst {min(5, len(keys))} keys:")
        for key in keys[:5]:
            print(f"  {key}")

        if len(keys) > 5:
            print(f"  ... and {len(keys) - 5} more")

    except ValueError:
        print("Please enter a valid number")
    except KeyboardInterrupt:
        print("\nOperation cancelled")

if __name__ == "__main__":
    main()
