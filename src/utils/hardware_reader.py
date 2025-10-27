# src/utils/hardware_reader.py

import wmi
import psutil
import platform
import uuid
import re

class HardwareReader:
    def __init__(self):
        self.c = wmi.WMI()
    
    def get_all_hardware_ids(self):
        """Coleta todos os IDs de hardware reais"""
        try:
            hardware = {}
            
            # Disk Serial (C: and D: drives)
            hardware['disk_c'] = self._get_disk_serial('C:')
            hardware['disk_d'] = self._get_disk_serial('D:')
            
            # Motherboard
            hardware['motherboard'] = self._get_motherboard_serial()
            
            # SMBIOS UUID
            hardware['smbios_uuid'] = self._get_uuid()
            
            # Chassis
            hardware['chassis'] = self._get_chassis_serial()
            
            # BIOS
            hardware['bios'] = self._get_bios_serial()
            
            # CPU
            hardware['cpu'] = self._get_cpu_id()
            
            # MAC Address
            hardware['mac'] = self._get_mac_address()
            
            return hardware
        except Exception as e:
            print(f"Error reading hardware: {e}")
            return self._get_fallback_data()
    
    def _get_disk_serial(self, drive_letter):
        try:
            for disk in self.c.Win32_LogicalDisk(DeviceID=drive_letter):
                if disk.VolumeSerialNumber:
                    return disk.VolumeSerialNumber
        except:
            pass
        return "N/A"
    
    def _get_motherboard_serial(self):
        try:
            for board in self.c.Win32_BaseBoard():
                if board.SerialNumber:
                    return board.SerialNumber.strip()
        except:
            pass
        return "N/A"
    
    def _get_uuid(self):
        try:
            for item in self.c.Win32_ComputerSystemProduct():
                if item.UUID:
                    return item.UUID
        except:
            pass
        return str(uuid.uuid4())
    
    def _get_chassis_serial(self):
        try:
            for chassis in self.c.Win32_SystemEnclosure():
                if chassis.SerialNumber:
                    return chassis.SerialNumber.strip()
        except:
            pass
        return "N/A"
    
    def _get_bios_serial(self):
        try:
            for bios in self.c.Win32_BIOS():
                if bios.SerialNumber:
                    return bios.SerialNumber.strip()
        except:
            pass
        return "N/A"
    
    def _get_cpu_id(self):
        try:
            for cpu in self.c.Win32_Processor():
                if cpu.ProcessorId:
                    return cpu.ProcessorId.strip()
        except:
            pass
        return "N/A"
    
    def _get_mac_address(self):
        try:
            for nic in self.c.Win32_NetworkAdapterConfiguration(IPEnabled=True):
                if nic.MACAddress:
                    return nic.MACAddress.replace(':', '')
        except:
            pass
        # Fallback usando uuid
        mac = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
        return mac.replace(':', '')
    
    def _get_fallback_data(self):
        """Dados de fallback caso WMI falhe"""
        return {
            'disk_c': "N/A",
            'disk_d': "N/A",
            'motherboard': "N/A",
            'smbios_uuid': str(uuid.uuid4()),
            'chassis': "N/A",
            'bios': "N/A",
            'cpu': "N/A",
            'mac': ':'.join(re.findall('..', '%012x' % uuid.getnode())).replace(':', '')
        }
