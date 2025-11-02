class SpoofingController:
    def __init__(self, cleaner, mac_spoofer, hwid_spoofer, guid_spoofer, hw_reader):
        self.cleaner = cleaner
        self.mac_spoofer = mac_spoofer
        self.hwid_spoofer = hwid_spoofer
        self.guid_spoofer = guid_spoofer
        self.hw_reader = hw_reader
