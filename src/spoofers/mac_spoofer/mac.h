// src/spoofers/mac_spoofer/mac.h

#ifndef MAC_H
#define MAC_H

#include <string>
#include <vector>

struct NetworkInterface {
    std::string name;
    std::string description;
    std::string mac_address;
    std::string interface_guid;
    bool enabled;
};

class MacSpoofer {
public:
    MacSpoofer();
    ~MacSpoofer();
    
    // Interface management
    std::vector<NetworkInterface> getNetworkInterfaces();
    std::string getCurrentMac(const std::string& interfaceName);
    bool spoofMacAddress(const std::string& interfaceName, const std::string& newMac);
    bool resetMacAddress(const std::string& interfaceName);
    bool disableInterface(const std::string& interfaceName);
    bool enableInterface(const std::string& interfaceName);
    
    // MAC generation
    std::string generateRandomMac(const std::string& vendorOUI = "");
    std::string generateVendorMac(const std::string& vendorName);
    
    // Utility functions
    bool isValidMac(const std::string& mac);
    std::string normalizeMac(const std::string& mac);

private:
    std::string getInterfaceGUID(const std::string& interfaceName);
    bool setRegistryMac(const std::string& interfaceGuid, const std::string& newMac);
    std::string executeCommand(const std::string& command);
};

#endif