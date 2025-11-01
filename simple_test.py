#!/usr/bin/env python3
"""
Simple test to verify basic functionality
"""
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_basic_import():
    """Test basic import without emojis"""
    print("Testing basic import...")

    try:
        # Test if we can import without issues
        import firebase_admin
        print("Firebase admin imported successfully")

        # Test if credentials file exists
        cred_path = 'firebase-key.json'
        if os.path.exists(cred_path):
            print("Firebase credentials file found")
        else:
            print("Firebase credentials file not found - this is expected in test environment")

        print("Basic import test passed!")
        return True

    except Exception as e:
        print(f"Basic import failed: {e}")
        return False

if __name__ == "__main__":
    test_basic_import()
