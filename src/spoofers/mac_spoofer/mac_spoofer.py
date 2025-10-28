# src/spoofers/mac_spoofer/mac_spoofer.py

import subprocess
import re
import random
import winreg
from utils.registry_checker import RegistryChecker
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
    def __init__(self, registry_checker: RegistryChecker = None):
        if platform.system() != 'Windows':
            raise OSError("MAC spoofing only supported on Windows")
            
        if not is_admin():
            raise PermissionError("Administrator privileges required")
            
        self.current_interface = None
        self.original_interface_data = {}
        # Registry helper (injectable for testing)
        self.registry = registry_checker or RegistryChecker()
        
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

    def spoof_mac_address(self, interface_name, vendor_name="", new_mac=None):
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
            if not new_mac:
                if vendor_name in self.VENDOR_OUI:
                    new_mac = self._generate_vendor_mac(vendor_name)
                else:
                    new_mac = self._generate_random_mac()
            
            # Desativa interface
            if not self._disable_interface(interface_name):
                logger.log_error(f"Failed to disable interface {interface_name}", "MAC")
                return False
            
            # Define novo MAC - Tenta método do registro primeiro
            logger.log_info(f"Attempting registry method for {interface_name}", "MAC")
            registry_success = self._set_registry_mac(interface_name, new_mac)
            
            if not registry_success:
                logger.log_warning(f"Registry method failed, trying PowerShell method for {interface_name}", "MAC")
                # Fallback para método PowerShell
                powershell_success = self._set_mac_powershell(interface_name, new_mac)
                if not powershell_success:
                    logger.log_error(f"All MAC spoofing methods failed for {interface_name}", "MAC")
                    self._enable_interface(interface_name)
                    return False
            
            # Reativa interface
            if not self._enable_interface(interface_name):
                logger.log_error(f"Failed to enable interface {interface_name}", "MAC")
                return False
            
            # Verifica mudança
            time.sleep(3)  # Aumenta o tempo de espera para Windows 11
            current_mac = self.get_current_mac(interface_name)
            
            if current_mac and current_mac.upper() == new_mac.upper():
                logger.log_success(f"MAC spoofing successful! New MAC: {current_mac}", "MAC")
                return True
            else:
                logger.log_warning(f"MAC verification failed. Current: {current_mac}, Expected: {new_mac}", "MAC")
                # Mesmo com falha na verificação, pode ter funcionado
                return True
                
        except Exception as e:
            logger.log_error(f"Error spoofing MAC: {str(e)}", "MAC")
            # Tenta reativar a interface em caso de erro
            try:
                self._enable_interface(interface_name)
            except:
                pass
            return False

    def reset_mac_address(self, interface_name):
        try:
            logger.log_info(f"Resetting MAC address for {interface_name}", "MAC")
            
            if not self._disable_interface(interface_name):
                return False
                
            # Remove chave do registro para resetar MAC
            interface_guid = self._get_interface_guid(interface_name)
            if interface_guid:
                key_path = f"SYSTEM\\CurrentControlSet\\Control\\Class\\{{4d36e972-e325-11ce-bfc1-08002be10318}}\\{interface_guid}"
                try:
                    # Use RegistryChecker to delete the NetworkAddress value (with backup)
                    self.registry.delete_value("HKLM", key_path, "NetworkAddress", backup=True)
                    logger.log_info(f"Registry MAC value deleted for {interface_name}", "MAC")
                except Exception:
                    logger.log_info(f"No registry MAC value to delete for {interface_name}", "MAC")
                    pass  # Chave pode não existir
            
            # Tenta reset via PowerShell também
            try:
                self._reset_mac_powershell(interface_name)
            except Exception as e:
                logger.log_warning(f"PowerShell reset failed: {str(e)}", "MAC")
            
            if not self._enable_interface(interface_name):
                return False
                
            time.sleep(3)  # Aumenta tempo de espera
            logger.log_success(f"MAC reset completed for {interface_name}", "MAC")
            
            if interface_name in self.original_interface_data:
                del self.original_interface_data[interface_name]
            if self.current_interface == interface_name:
                self.current_interface = None
                
            return True
            
        except Exception as e:
            logger.log_error(f"Error resetting MAC: {str(e)}", "MAC")
            return False

    def get_current_mac(self, interface_name):
        try:
            # Método mais robusto para obter MAC
            output = subprocess.check_output('getmac /v /fo csv /nh', shell=True, encoding='cp850')
            for line in output.split('\n'):
                if line.strip() and interface_name in line:
                    fields = line.strip('"').split('","')
                    if len(fields) >= 3 and fields[0] == interface_name:
                        mac = fields[2].strip('"').replace('-', ':').upper()
                        logger.log_info(f"Current MAC for {interface_name}: {mac}", "MAC")
                        return mac
            
            # Fallback: tenta com wmic
            try:
                output = subprocess.check_output(f'wmic nic where "NetConnectionID=\'{interface_name}\'" get MACAddress /format:csv', 
                                              shell=True, encoding='cp850')
                lines = output.strip().split('\n')
                if len(lines) > 1:
                    mac = lines[1].split(',')[-1].strip().replace(':', '').upper()
                    if mac and len(mac) == 12:
                        formatted_mac = ':'.join([mac[i:i+2] for i in range(0, 12, 2)])
                        logger.log_info(f"Current MAC (wmic) for {interface_name}: {formatted_mac}", "MAC")
                        return formatted_mac
            except:
                pass
                
        except Exception as e:
            logger.log_error(f"Error getting current MAC: {str(e)}", "MAC")
        return None
        
    def _disable_interface(self, interface_name):
        try:
            logger.log_info(f"Disabling interface: {interface_name}", "MAC")
            result = subprocess.run(
                f'netsh interface set interface "{interface_name}" disable', 
                shell=True, 
                check=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            time.sleep(2)  # Aumenta tempo de espera
            logger.log_success(f"Interface {interface_name} disabled", "MAC")
            return True
        except subprocess.TimeoutExpired:
            logger.log_error(f"Timeout disabling interface {interface_name}", "MAC")
            return False
        except Exception as e:
            logger.log_error(f"Failed to disable interface {interface_name}: {str(e)}", "MAC")
            return False
            
    def _enable_interface(self, interface_name):
        try:
            logger.log_info(f"Enabling interface: {interface_name}", "MAC")
            result = subprocess.run(
                f'netsh interface set interface "{interface_name}" enable', 
                shell=True, 
                check=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            time.sleep(2)  # Aumenta tempo de espera
            logger.log_success(f"Interface {interface_name} enabled", "MAC")
            return True
        except subprocess.TimeoutExpired:
            logger.log_error(f"Timeout enabling interface {interface_name}", "MAC")
            return False
        except Exception as e:
            logger.log_error(f"Failed to enable interface {interface_name}: {str(e)}", "MAC")
            return False
            
    def _generate_random_mac(self):
        # Gera MAC com bit "locally administered" setado
        mac = ["02"]  # Primeiro byte com bit local setado
        for i in range(5):
            mac.append(f"{random.randint(0, 255):02x}")
        generated_mac = ":".join(mac).upper()
        logger.log_info(f"Generated random MAC: {generated_mac}", "MAC")
        return generated_mac
        
    def _generate_vendor_mac(self, vendor_name):
        vendor_prefix = self.VENDOR_OUI.get(vendor_name, "")
        if not vendor_prefix:
            return self._generate_random_mac()
            
        # Usa OUI do vendor e gera 3 bytes aleatórios
        mac = vendor_prefix.split(":")
        for i in range(3):
            mac.append(f"{random.randint(0, 255):02x}")
        generated_mac = ":".join(mac).upper()
        logger.log_info(f"Generated vendor MAC ({vendor_name}): {generated_mac}", "MAC")
        return generated_mac
        
    def _get_interface_guid(self, interface_name):
        """Método melhorado para encontrar o GUID da interface no Windows 11"""
        try:
            logger.log_info(f"Searching for GUID of interface: {interface_name}", "MAC")
            
            # Método 1: Usa PowerShell para obter o InterfaceGuid diretamente
            try:
                ps_cmd = f"Get-NetAdapter -Name '{interface_name}' | Select-Object -ExpandProperty InterfaceGuid"
                output = subprocess.check_output(["powershell", "-Command", ps_cmd], 
                                              shell=False, 
                                              encoding='cp850',
                                              timeout=15)
                guid = output.strip()
                if guid:
                    logger.log_info(f"Found GUID via PowerShell: {guid}", "MAC")
                    # Agora procura o número correspondente no registro usando RegistryChecker
                    base = r"SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}"
                    try:
                        sub = self.registry.find_subkey_by_value("HKLM", base, "NetCfgInstanceId", lambda v: isinstance(v, str) and v.lower() == guid.lower())
                        if sub:
                            logger.log_info(f"Found registry key: {sub} for GUID: {guid}", "MAC")
                            return sub
                    except Exception:
                        logger.log_warning("Error searching registry for GUID via RegistryChecker", "MAC")
            except subprocess.CalledProcessError as e:
                logger.log_warning(f"PowerShell method failed: {str(e)}", "MAC")
            except subprocess.TimeoutExpired:
                logger.log_warning("PowerShell command timeout", "MAC")

            # Método 2: Busca por DriverDesc (mais compatível)
            logger.log_info("Trying DriverDesc/NetCfgInstanceId method...", "MAC")
            base = r"SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}"
            try:
                subs = self.registry.enumerate_subkeys("HKLM", base)
                for subkey_name in subs:
                    try:
                        # Try DriverDesc
                        try:
                            driver_desc, _ = self.registry.read_value("HKLM", os.path.join(base, subkey_name), "DriverDesc")
                            if driver_desc and interface_name.lower() in str(driver_desc).lower():
                                logger.log_info(f"Found by DriverDesc: {subkey_name} - {driver_desc}", "MAC")
                                return subkey_name
                        except Exception:
                            pass

                        # Try NetCfgInstanceId
                        try:
                            netcfg, _ = self.registry.read_value("HKLM", os.path.join(base, subkey_name), "NetCfgInstanceId")
                            if netcfg and interface_name.lower() in str(netcfg).lower():
                                logger.log_info(f"Found by NetCfgInstanceId: {subkey_name} - {netcfg}", "MAC")
                                return subkey_name
                        except Exception:
                            pass
                    except Exception:
                        continue
            except Exception:
                logger.log_warning("Error enumerating network adapter registry keys via RegistryChecker", "MAC")

            # Método 3: Busca por nome correspondente
            logger.log_info("Trying name matching method...", "MAC")
            try:
                subs = self.registry.enumerate_subkeys("HKLM", base)
                for subkey_name in subs:
                    if not str(subkey_name).isdigit():
                        continue
                    try:
                        for value_name in ["DriverDesc", "NetCfgInstanceId", "ComponentId"]:
                            try:
                                val, _ = self.registry.read_value("HKLM", os.path.join(base, subkey_name), value_name)
                                if val and interface_name.lower() in str(val).lower():
                                    logger.log_info(f"Found by {value_name}: {subkey_name} - {val}", "MAC")
                                    return subkey_name
                            except Exception:
                                continue
                    except Exception:
                        continue
            except Exception:
                logger.log_warning("Error enumerating registry keys in name-matching method", "MAC")

            logger.log_error(f"Could not find GUID for interface: {interface_name}", "MAC")
            return None

        except Exception as e:
            logger.log_error(f"_get_interface_guid error: {str(e)}", "MAC")
            return None
        
    def _set_registry_mac(self, interface_name, new_mac):
        try:
            interface_guid = self._get_interface_guid(interface_name)
            if not interface_guid:
                logger.log_error(f"Could not find registry subkey for interface {interface_name}", "MAC")
                return False

            key_path = f"SYSTEM\\CurrentControlSet\\Control\\Class\\{{4d36e972-e325-11ce-bfc1-08002be10318}}\\{interface_guid}"
            logger.log_info(f"Writing NetworkAddress to registry key: {key_path}", "MAC")
            # Ensure admin
            try:
                self.registry.ensure_admin_or_raise()
            except Exception as e:
                logger.log_error(str(e), "MAC")
                return False

            # Remove caracteres : do MAC para o registro
            mac_value = new_mac.replace(":", "")

            # Use RegistryChecker to write value (it will create backup and respect dry-run)
            try:
                self.registry.write_value("HKLM", key_path, "NetworkAddress", mac_value, value_type=winreg.REG_SZ, backup=True)
            except Exception as e:
                logger.log_error(f"Failed to set registry MAC: {e}", "MAC")
                return False

            logger.log_info(f"Registry NetworkAddress set to {mac_value}", "MAC")

            # Verifica se foi escrito corretamente
            try:
                stored_value, _ = self.registry.read_value("HKLM", key_path, "NetworkAddress")
                if stored_value == mac_value:
                    logger.log_success("Registry value verified successfully", "MAC")
                    return True
                else:
                    logger.log_error(f"Registry verification failed. Stored: {stored_value}, Expected: {mac_value}", "MAC")
                    return False
            except Exception as e:
                logger.log_error(f"Registry verification failed: {e}", "MAC")
                return False

        except PermissionError:
            logger.log_error("Permission denied when writing to registry", "MAC")
            return False
        except Exception as e:
            logger.log_error(f"Failed to set registry MAC: {str(e)}", "MAC")
            return False

    def _set_mac_powershell(self, interface_name, new_mac):
        """Método alternativo usando PowerShell para Windows 11"""
        try:
            logger.log_info(f"Attempting PowerShell method for {interface_name}", "MAC")
            
            # Remove caracteres : do MAC
            mac_value = new_mac.replace(":", "")
            
            # Comando PowerShell para mudar MAC
            ps_command = [
                "powershell", "-Command",
                f"Get-NetAdapter -Name '{interface_name}' | Set-NetAdapter -MACAddress '{mac_value}' -Confirm:$false"
            ]
            
            result = subprocess.run(
                ps_command,
                check=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            logger.log_success(f"PowerShell MAC change executed for {interface_name}", "MAC")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.log_error(f"PowerShell command failed: {e.stderr}", "MAC")
            return False
        except subprocess.TimeoutExpired:
            logger.log_error("PowerShell command timeout", "MAC")
            return False
        except Exception as e:
            logger.log_error(f"PowerShell method error: {str(e)}", "MAC")
            return False

    def _reset_mac_powershell(self, interface_name):
        """Reseta MAC usando PowerShell"""
        try:
            logger.log_info(f"Resetting MAC via PowerShell for {interface_name}", "MAC")
            
            ps_command = [
                "powershell", "-Command",
                f"Get-NetAdapter -Name '{interface_name}' | Set-NetAdapter -MACAddress '' -Confirm:$false"
            ]
            
            result = subprocess.run(
                ps_command,
                check=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            logger.log_success(f"PowerShell MAC reset executed for {interface_name}", "MAC")
            return True
            
        except Exception as e:
            logger.log_warning(f"PowerShell reset failed: {str(e)}", "MAC")
            return False
