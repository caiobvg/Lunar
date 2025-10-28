// src/spoofers/mac_spoofer/mac.cpp

#include "mac.h"
#include <windows.h>
#include <iphlpapi.h>
#include <iostream>
#include <sstream>
#include <iomanip>
#include <random>
#include <regex>
#include <algorithm>

#pragma comment(lib, "iphlpapi.lib")
#pragma comment(lib, "advapi32.lib")

// Vendor OUIs for realistic MAC addresses
std::unordered_map<std::string, std::string> VENDOR_OUI = {
    {"Cisco", "00:1C:58"},
    {"Dell", "00:1A:A0"},
    {"HP", "00:1A:4B"},
    {"Intel", "00:1B:21"},
    {"Apple", "00:1D:4F"},
    {"Samsung", "00:1E:7D"},
    {"Microsoft", "00:1D:60"},
    {"Realtek", "00:1E:68"},
    {"TP-Link", "00:1D:0F"},
    {"ASUS", "00:1A:92"}
};

MacSpoofer::MacSpoofer() {
    // Initialize any required components
}

MacSpoofer::~MacSpoofer() {
    // Cleanup if needed
}

std::vector<NetworkInterface> MacSpoofer::getNetworkInterfaces() {
    std::vector<NetworkInterface> interfaces;
    
    PIP_ADAPTER_INFO adapterInfo;
    ULONG bufferSize = sizeof(IP_ADAPTER_INFO);
    
    adapterInfo = (IP_ADAPTER_INFO*)malloc(bufferSize);
    if (adapterInfo == NULL) {
        return interfaces;
    }
    
    // Get adapter information
    if (GetAdaptersInfo(adapterInfo, &bufferSize) == ERROR_BUFFER_OVERFLOW) {
        free(adapterInfo);
        adapterInfo = (IP_ADAPTER_INFO*)malloc(bufferSize);
        if (adapterInfo == NULL) {
            return interfaces;
        }
    }
    
    if (GetAdaptersInfo(adapterInfo, &bufferSize) == NO_ERROR) {
        PIP_ADAPTER_INFO adapter = adapterInfo;
        
        while (adapter) {
            NetworkInterface iface;
            iface.name = adapter->AdapterName;
            iface.description = adapter->Description;
            
            // Format MAC address
            std::stringstream macStream;
            for (UINT i = 0; i < adapter->AddressLength; i++) {
                if (i > 0) macStream << ":";
                macStream << std::hex << std::setw(2) << std::setfill('0') 
                         << (int)adapter->Address[i];
            }
            iface.mac_address = macStream.str();
            
            // Get interface GUID (simplified)
            iface.interface_guid = adapter->AdapterName;
            iface.enabled = (adapter->Type == MIB_IF_TYPE_ETHERNET);
            
            interfaces.push_back(iface);
            adapter = adapter->Next;
        }
    }
    
    free(adapterInfo);
    return interfaces;
}

std::string MacSpoofer::getCurrentMac(const std::string& interfaceName) {
    auto interfaces = getNetworkInterfaces();
    for (const auto& iface : interfaces) {
        if (iface.name == interfaceName) {
            return iface.mac_address;
        }
    }
    return "";
}

bool MacSpoofer::spoofMacAddress(const std::string& interfaceName, const std::string& newMac) {
    std::string normalizedMac = normalizeMac(newMac);
    if (!isValidMac(normalizedMac)) {
        return false;
    }
    
    // Get interface GUID
    std::string interfaceGuid = getInterfaceGUID(interfaceName);
    if (interfaceGuid.empty()) {
        return false;
    }
    
    // Disable interface
    if (!disableInterface(interfaceName)) {
        return false;
    }
    
    // Set new MAC in registry
    if (!setRegistryMac(interfaceGuid, normalizedMac)) {
        enableInterface(interfaceName); // Re-enable if failed
        return false;
    }
    
    // Enable interface
    if (!enableInterface(interfaceName)) {
        return false;
    }
    
    // Verify change
    Sleep(2000); // Wait for interface to initialize
    std::string currentMac = getCurrentMac(interfaceName);
    return (currentMac == normalizedMac);
}

bool MacSpoofer::resetMacAddress(const std::string& interfaceName) {
    std::string interfaceGuid = getInterfaceGUID(interfaceName);
    if (interfaceGuid.empty()) {
        return false;
    }
    
    // Disable interface
    if (!disableInterface(interfaceName)) {
        return false;
    }
    
    // Remove registry key to reset to original MAC
    HKEY hKey;
    std::string keyPath = "SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e972-e325-11ce-bfc1-08002be10318}\\";
    keyPath += interfaceGuid;
    
    if (RegOpenKeyExA(HKEY_LOCAL_MACHINE, keyPath.c_str(), 0, KEY_WRITE, &hKey) == ERROR_SUCCESS) {
        RegDeleteValueA(hKey, "NetworkAddress");
        RegCloseKey(hKey);
    }
    
    // Enable interface
    if (!enableInterface(interfaceName)) {
        return false;
    }
    
    Sleep(2000); // Wait for interface to initialize
    return true;
}

bool MacSpoofer::disableInterface(const std::string& interfaceName) {
    std::string command = "netsh interface set interface \"" + interfaceName + "\" disable";
    std::string result = executeCommand(command);
    Sleep(1000); // Wait for disable to complete
    return result.find("Ok") != std::string::npos;
}

bool MacSpoofer::enableInterface(const std::string& interfaceName) {
    std::string command = "netsh interface set interface \"" + interfaceName + "\" enable";
    std::string result = executeCommand(command);
    Sleep(1000); // Wait for enable to complete
    return result.find("Ok") != std::string::npos;
}

std::string MacSpoofer::generateRandomMac(const std::string& vendorOUI) {
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> dis(0, 255);
    
    std::stringstream macStream;
    
    if (!vendorOUI.empty()) {
        macStream << vendorOUI;
    } else {
        // Generate random OUI (locally administered)
        macStream << "02:"; // Locally administered bit set
        macStream << std::hex << std::setw(2) << std::setfill('0') << dis(gen) << ":";
        macStream << std::hex << std::setw(2) << std::setfill('0') << dis(gen);
    }
    
    // Generate last 3 octets
    for (int i = 0; i < 3; i++) {
        macStream << ":" << std::hex << std::setw(2) << std::setfill('0') << dis(gen);
    }
    
    return macStream.str();
}

std::string MacSpoofer::generateVendorMac(const std::string& vendorName) {
    auto it = VENDOR_OUI.find(vendorName);
    if (it != VENDOR_OUI.end()) {
        return generateRandomMac(it->second);
    }
    return generateRandomMac();
}

bool MacSpoofer::isValidMac(const std::string& mac) {
    std::regex macRegex("^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$");
    return std::regex_match(mac, macRegex);
}

std::string MacSpoofer::normalizeMac(const std::string& mac) {
    std::string normalized = mac;
    // Replace hyphens with colons
    std::replace(normalized.begin(), normalized.end(), '-', ':');
    // Convert to uppercase
    std::transform(normalized.begin(), normalized.end(), normalized.begin(), ::toupper);
    return normalized;
}

std::string MacSpoofer::getInterfaceGUID(const std::string& interfaceName) {
    // Simplified implementation - in real scenario, you'd query registry
    // This is a placeholder that returns the adapter name as GUID
    return interfaceName;
}

bool MacSpoofer::setRegistryMac(const std::string& interfaceGuid, const std::string& newMac) {
    HKEY hKey;
    std::string keyPath = "SYSTEM\\CurrentControlSet\\Control\\Class\\{4d36e972-e325-11ce-bfc1-08002be10318}\\";
    keyPath += interfaceGuid;
    
    if (RegOpenKeyExA(HKEY_LOCAL_MACHINE, keyPath.c_str(), 0, KEY_WRITE, &hKey) == ERROR_SUCCESS) {
        if (RegSetValueExA(hKey, "NetworkAddress", 0, REG_SZ, 
                          (const BYTE*)newMac.c_str(), newMac.length() + 1) == ERROR_SUCCESS) {
            RegCloseKey(hKey);
            return true;
        }
        RegCloseKey(hKey);
    }
    return false;
}

std::string MacSpoofer::executeCommand(const std::string& command) {
    char buffer[128];
    std::string result = "";
    FILE* pipe = _popen(command.c_str(), "r");
    if (!pipe) return result;
    
    try {
        while (fgets(buffer, sizeof buffer, pipe) != NULL) {
            result += buffer;
        }
    } catch (...) {
        _pclose(pipe);
        throw;
    }
    _pclose(pipe);
    return result;
}