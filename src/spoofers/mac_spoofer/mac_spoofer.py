import subprocess
import re
import random
import winreg
import time
import os
import platform
import ctypes
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from utils.logger import logger

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

class MACSpoofer:
    def __init__(self):
        if platform.system() != 'Windows':
            raise OSError("MAC spoofing only supported on Windows")
            
        if not is_admin():
            raise PermissionError("Administrator privileges required")
            
        self.current_interface = None
        self.original_interface_data = {}
        
        # Vendor OUIs para endereços MAC realistas
        self.VENDOR_OUI = {
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

    def get_interfaces(self):
        interfaces = []
        try:
            # Usa getmac com codificação cp850 (Windows console default)
            output = subprocess.check_output("getmac /v /fo csv", shell=True, encoding='cp850')
            
            # Pula a linha de cabeçalho
            lines = output.strip().split('\n')[1:]
            
            for line in lines:
                try:
                    # Remove aspas e divide campos
                    fields = line.strip('"').split('","')
                    
                    if len(fields) >= 3:
                        iface = {
                            'name': fields[0],
                            'description': fields[1],
                            'mac_address': fields[2].strip('"'),
                            'enabled': True  # getmac só mostra interfaces ativas
                        }
                        interfaces.append(iface)
                        logger.log_info(f"Found interface: {iface['name']} ({iface['mac_address']})", "MAC")
                except IndexError:
                    continue  # Pula linhas malformadas
                    
        except subprocess.CalledProcessError:
            logger.log_error("Failed to get network interfaces - Access denied", "MAC")
            raise PermissionError("Access denied when getting network interfaces")
        except Exception as e:
            # Tenta método alternativo usando wmic
            try:
                logger.log_info("Trying alternative method with wmic...", "MAC")
                output = subprocess.check_output("wmic nic get Name,MACAddress /format:csv", 
                                              shell=True, encoding='cp850')
                
                lines = output.strip().split('\n')[1:]  # Pula cabeçalho
                for line in lines:
                    if ',' not in line:
                        continue
                        
                    name, mac = line.strip().split(',', 1)
                    if mac and mac.strip():  # Só adiciona se tiver MAC
                        iface = {
                            'name': name,
                            'description': name,
                            'mac_address': mac.strip().replace(':', '-'),
                            'enabled': True
                        }
                        interfaces.append(iface)
                        logger.log_info(f"Found interface: {iface['name']} ({iface['mac_address']})", "MAC")
                        
            except Exception as e2:
                logger.log_error(f"Both methods failed to get interfaces: {str(e2)}", "MAC")
                raise RuntimeError(f"Failed to enumerate network interfaces: {str(e2)}")
        
        if not interfaces:
            logger.log_warning("No network interfaces found", "MAC")
            
        return interfaces

    def spoof_mac_address(self, interface_name, vendor_name=""):
        try:
            logger.log_info(f"Starting MAC spoofing for {interface_name}", "MAC")
            
            # Verifica se interface existe
            current_mac = self.get_current_mac(interface_name)
            if not current_mac:
                logger.log_error(f"Interface {interface_name} not found", "MAC")
                return False
                
            if not self.current_interface:
                # Salva MAC original
                self.original_interface_data[interface_name] = current_mac
                logger.log_info(f"Original MAC saved: {current_mac}", "MAC")
            
            self.current_interface = interface_name
            
            # Gera novo MAC
            if vendor_name in self.VENDOR_OUI:
                new_mac = self._generate_vendor_mac(vendor_name)
            else:
                new_mac = self._generate_random_mac()
            
            # Desativa interface
            if not self._disable_interface(interface_name):
                return False
            
            # Define novo MAC
            if not self._set_registry_mac(interface_name, new_mac):
                self._enable_interface(interface_name)
                return False
            
            # Reativa interface
            if not self._enable_interface(interface_name):
                return False
            
            # Verifica mudança
            time.sleep(2)
            current_mac = self.get_current_mac(interface_name)
            return current_mac and current_mac.upper() == new_mac.upper()
            
        except Exception as e:
            print(f"Error spoofing MAC: {e}")
            return False

    def reset_mac_address(self, interface_name):
        try:
            if not self._disable_interface(interface_name):
                return False
                
            # Remove chave do registro para resetar MAC
            interface_guid = self._get_interface_guid(interface_name)
            if interface_guid:
                key_path = f"SYSTEM\\CurrentControlSet\\Control\\Class\\{{4d36e972-e325-11ce-bfc1-08002be10318}}\\{interface_guid}"
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE) as key:
                        winreg.DeleteValue(key, "NetworkAddress")
                except WindowsError:
                    pass  # Chave pode não existir
            
            if not self._enable_interface(interface_name):
                return False
                
            time.sleep(2)
            
            if interface_name in self.original_interface_data:
                del self.original_interface_data[interface_name]
            if self.current_interface == interface_name:
                self.current_interface = None
                
            return True
            
        except Exception as e:
            print(f"Error resetting MAC: {e}")
            return False

    def get_current_mac(self, interface_name):
        try:
            output = subprocess.check_output(f'getmac /v /fo csv /nh', shell=True).decode()
            for line in output.split('\n'):
                if line.strip():
                    fields = line.strip('"').split('","')
                    if fields[0] == interface_name:
                        return fields[2].strip('"').replace('-', ':').upper()
        except:
            pass
        return None
        
    def _disable_interface(self, interface_name):
        try:
            subprocess.run(f'netsh interface set interface "{interface_name}" disable', 
                         shell=True, check=True)
            time.sleep(1)
            return True
        except:
            return False
            
    def _enable_interface(self, interface_name):
        try:
            subprocess.run(f'netsh interface set interface "{interface_name}" enable', 
                         shell=True, check=True)
            time.sleep(1)
            return True
        except:
            return False
            
    def _generate_random_mac(self):
        # Gera MAC com bit "locally administered" setado
        mac = ["02"]  # Primeiro byte com bit local setado
        for i in range(5):
            mac.append(f"{random.randint(0, 255):02x}")
        return ":".join(mac).upper()
        
    def _generate_vendor_mac(self, vendor_name):
        vendor_prefix = self.VENDOR_OUI.get(vendor_name, "")
        if not vendor_prefix:
            return self._generate_random_mac()
            
        # Usa OUI do vendor e gera 3 bytes aleatórios
        mac = vendor_prefix.split(":")
        for i in range(3):
            mac.append(f"{random.randint(0, 255):02x}")
        return ":".join(mac).upper()
        
    def _get_interface_guid(self, interface_name):
        try:
            # Primeiro, tenta obter NetCfgInstanceId usando PowerShell Get-NetAdapter
            try:
                ps_cmd = f"Get-NetAdapter -Name '{interface_name}' | Select-Object -ExpandProperty InterfaceGuid"
                output = subprocess.check_output(["powershell", "-Command", ps_cmd], shell=False, encoding='cp850')
                guid = output.strip()
                if guid:
                    # A chave na branch Class usa um número (0000, 0001...) não o GUID diretamente.
                    # Precisamos localizar a subchave cujo NetCfgInstanceId corresponde ao guid.
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}") as key:
                        for i in range(0, 200):
                            try:
                                subkey_name = winreg.EnumKey(key, i)
                                with winreg.OpenKey(key, subkey_name) as subkey:
                                    try:
                                        netcfg = winreg.QueryValueEx(subkey, "NetCfgInstanceId")[0]
                                        if netcfg.lower() == guid.lower():
                                            return subkey_name
                                    except WindowsError:
                                        continue
                            except WindowsError:
                                break
            except subprocess.CalledProcessError:
                logger.log_warning("PowerShell Get-NetAdapter failed; falling back to registry scan", "MAC")

            # Fallback: scan all subkeys and try to match DriverDesc or NetCfgInstanceId
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}") as key:
                for i in range(0, 200):
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, subkey_name) as subkey:
                            try:
                                # Tenta NetCfgInstanceId primeiro
                                netcfg = winreg.QueryValueEx(subkey, "NetCfgInstanceId")[0]
                                if netcfg and interface_name.lower() in netcfg.lower():
                                    return subkey_name
                            except WindowsError:
                                pass
                            try:
                                name = winreg.QueryValueEx(subkey, "DriverDesc")[0]
                                if name and interface_name.lower() in name.lower():
                                    return subkey_name
                            except WindowsError:
                                pass
                    except WindowsError:
                        break
        except Exception as e:
            logger.log_error(f"_get_interface_guid error: {e}", "MAC")
        return None
        
    def _set_registry_mac(self, interface_name, new_mac):
        try:
            interface_guid = self._get_interface_guid(interface_name)
            if not interface_guid:
                logger.log_error(f"Could not find registry subkey for interface {interface_name}", "MAC")
                return False

            key_path = f"SYSTEM\\CurrentControlSet\\Control\\Class\\{{4d36e972-e325-11ce-bfc1-08002be10318}}\\{interface_guid}"
            logger.log_info(f"Writing NetworkAddress to registry key: {key_path}", "MAC")
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE) as key:
                # Remove caracteres : do MAC para o registro
                mac_value = new_mac.replace(":", "")
                winreg.SetValueEx(key, "NetworkAddress", 0, winreg.REG_SZ, mac_value)
            logger.log_info(f"Registry NetworkAddress set to {mac_value}", "MAC")
            return True

        except PermissionError:
            logger.log_error("Permission denied when writing to registry", "MAC")
            return False
        except Exception as e:
            logger.log_error(f"Failed to set registry MAC: {e}", "MAC")
            return False
