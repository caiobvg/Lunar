# src/utils/hardware_reader.py

import wmi
import psutil
import platform
import uuid
import re
import winreg
import subprocess
import json
import hashlib
import os
import tempfile
import time
from typing import Dict, Optional

class HardwareReader:
    def __init__(self):
        # WMI availability checking
        try:
            self.c = wmi.WMI()
            self.wmi_available = True
            from src.utils.logger import logger
            logger.log_info("WMI inicializado com sucesso", "HARDWARE_READER")
        except Exception as e:
            self.c = None
            self.wmi_available = False
            from src.utils.logger import logger
            logger.log_warning(f"WMI não disponível - usando métodos alternativos: {str(e)}", "HARDWARE_READER")

        # Cache attributes
        self.cache_file = os.path.join(tempfile.gettempdir(), "midnight_spoofer_cache.json")
        self.cache_timeout = 300  # 5 minutes
        self.last_cache_time = 0
        self.cached_data = None
    
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

    def get_formatted_hardware_data(self, mac_spoofer=None):
        """
        Obtém e formata os dados de hardware para exibição na UI.
        Opcionalmente, verifica se há um MAC spoofado ativo.
        """
        if not self:
            return {
                'disk_c': 'N/A', 'disk_d': 'N/A', 'motherboard': 'N/A',
                'smbios_uuid': 'N/A', 'chassis': 'N/A', 'bios': 'N/A',
                'cpu': 'N/A', 'mac': 'N/A'
            }
        
        try:
            hw_data = self.get_all_hardware_ids()
            
            # Se um spoofer de MAC for fornecido e houver um MAC spoofado, atualiza o valor
            if mac_spoofer and mac_spoofer.current_interface and \
               mac_spoofer.current_interface in mac_spoofer.original_interface_data:
                current_mac = mac_spoofer.get_current_mac(mac_spoofer.current_interface)
                if current_mac:
                    hw_data['mac'] = f"{current_mac} 🎭"
            
            return hw_data
        except Exception as e:
            # Em caso de erro, retorna dados de fallback para não quebrar a UI
            print(f"Error getting formatted hardware data: {e}")
            return self._get_fallback_data()

    def _get_windows_activation_status(self) -> str:
        """
        Detecta o status de ativação do Windows usando múltiplos métodos.
        Retorna: "Ativado", "Não Ativado", "Expirou", "Erro", "Status Desconhecido"
        """
        from src.utils.logger import logger

        # Método 1: SLMGR (mais confiável) - usando caminho completo
        try:
            logger.log_info("Tentando detectar ativação via SLMGR", "WINDOWS_ACTIVATION")
            slmgr_path = r"C:\Windows\System32\slmgr.vbs"
            result = subprocess.run(
                ['cscript', slmgr_path, '/xpr'],
                capture_output=True,
                text=True,
                timeout=15,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            output = result.stdout.lower()
            # Verificar tanto português quanto inglês
            if ("permanentemente" in output or "permanently" in output or
                "ativado" in output or "activated" in output or "licenciado" in output):
                logger.log_success("Windows detectado como ativado via SLMGR", "WINDOWS_ACTIVATION")
                return "Ativado"
            elif "expired" in output or "expirou" in output or "expirada" in output:
                logger.log_warning("Windows detectado como expirado via SLMGR", "WINDOWS_ACTIVATION")
                return "Expirou"
            else:
                logger.log_info(f"SLMGR output não reconhecido: {output[:100]}", "WINDOWS_ACTIVATION")

        except subprocess.TimeoutExpired:
            logger.log_warning("SLMGR timeout - método alternativo será usado", "WINDOWS_ACTIVATION")
        except FileNotFoundError:
            logger.log_warning("SLMGR não encontrado no sistema", "WINDOWS_ACTIVATION")
        except Exception as e:
            logger.log_error(f"Erro ao executar SLMGR: {str(e)}", "WINDOWS_ACTIVATION")

        # Método 2: Registry - múltiplas chaves
        registry_paths = [
            r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\SoftwareProtectionPlatform",
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsActivationTechnologies\LicensingState"
        ]

        for reg_path in registry_paths:
            try:
                logger.log_info(f"Tentando detectar ativação via Registry: {reg_path}", "WINDOWS_ACTIVATION")
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ) as key:
                    # Tentar diferentes valores dependendo da chave
                    if "SoftwareProtectionPlatform" in reg_path:
                        license_status, _ = winreg.QueryValueEx(key, "LicenseStatus")
                        if license_status == 1:
                            logger.log_success("Windows detectado como ativado via Registry (SPP)", "WINDOWS_ACTIVATION")
                            return "Ativado (Registry)"
                        elif license_status == 0:
                            logger.log_info("Windows detectado como não ativado via Registry (SPP)", "WINDOWS_ACTIVATION")
                            return "Não Ativado"
                    elif "LicensingState" in reg_path:
                        licensing_state, _ = winreg.QueryValueEx(key, "LicensingState")
                        # LicensingState: bit 0 = licensed, bit 1 = activated
                        if licensing_state & 1:  # Bit 0 set = licensed
                            logger.log_success("Windows detectado como ativado via Registry (LicensingState)", "WINDOWS_ACTIVATION")
                            return "Ativado (Registry)"
                        else:
                            logger.log_info("Windows detectado como não ativado via Registry (LicensingState)", "WINDOWS_ACTIVATION")
                            return "Não Ativado"
            except FileNotFoundError:
                continue  # Tentar próxima chave
            except Exception as e:
                logger.log_error(f"Erro ao ler registro {reg_path}: {str(e)}", "WINDOWS_ACTIVATION")
                continue

        logger.log_info("Chaves de registro de ativação não encontradas ou inacessíveis", "WINDOWS_ACTIVATION")

        # Método 3: WMI - verificação mais robusta
        if self.wmi_available:
            try:
                logger.log_info("Tentando detectar ativação via WMI", "WINDOWS_ACTIVATION")
                for os_info in self.c.Win32_OperatingSystem():
                    if hasattr(os_info, 'LicenseStatus') and os_info.LicenseStatus is not None:
                        if os_info.LicenseStatus == 1:  # Licensed
                            logger.log_success("Windows detectado como ativado via WMI (LicenseStatus)", "WINDOWS_ACTIVATION")
                            return "Ativado (WMI)"
                        elif os_info.LicenseStatus == 0:  # Unlicensed
                            logger.log_info("Windows detectado como não ativado via WMI", "WINDOWS_ACTIVATION")
                            return "Não Ativado"
                    # Verificar ProductType para Windows genuíno
                    if hasattr(os_info, 'ProductType') and os_info.ProductType == 1:  # Client OS
                        # Verificar se há chave de produto válida
                        if hasattr(os_info, 'SerialNumber') and os_info.SerialNumber:
                            logger.log_success("Windows detectado como ativado via WMI (ProductType)", "WINDOWS_ACTIVATION")
                            return "Ativado (WMI)"
            except Exception as e:
                logger.log_error(f"Erro ao verificar WMI para ativação: {str(e)}", "WINDOWS_ACTIVATION")

        logger.log_warning("Status de ativação do Windows não pôde ser determinado", "WINDOWS_ACTIVATION")
        return "Status Desconhecido"

    def _get_installation_id(self) -> str:
        """
        Gera um Installation ID único baseado em hardware + software.
        Formato: WIN-{SHA256 hash em maiúsculo}
        """
        from src.utils.logger import logger

        try:
            logger.log_info("Gerando Installation ID", "INSTALLATION_ID")

            # Coleta dados do sistema para gerar hash único
            system_data = {}

            # Machine GUID
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography", 0, winreg.KEY_READ) as key:
                    system_data['machine_guid'] = winreg.QueryValueEx(key, "MachineGuid")[0]
            except:
                system_data['machine_guid'] = str(uuid.uuid4())

            # Product ID
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion", 0, winreg.KEY_READ) as key:
                    system_data['product_id'] = winreg.QueryValueEx(key, "ProductId")[0]
            except:
                system_data['product_id'] = platform.version()

            # Computer name e Windows edition
            system_data['computer_name'] = platform.node()
            system_data['windows_edition'] = platform.version()

            # Hardware identifiers
            hw_data = self.get_all_hardware_ids()
            system_data['motherboard'] = hw_data.get('motherboard', 'N/A')
            system_data['bios'] = hw_data.get('bios', 'N/A')
            system_data['cpu'] = hw_data.get('cpu', 'N/A')

            # Gera hash único
            hash_input = json.dumps(system_data, sort_keys=True).encode('utf-8')
            installation_hash = hashlib.sha256(hash_input).hexdigest()[:16].upper()

            installation_id = f"WIN-{installation_hash}"
            logger.log_success(f"Installation ID gerado: {installation_id}", "INSTALLATION_ID")
            return installation_id

        except Exception as e:
            logger.log_error(f"Erro ao gerar Installation ID: {str(e)}", "INSTALLATION_ID")
            # Fallback: gerar ID baseado no erro
            error_hash = hashlib.md5(str(e).encode()).hexdigest()[:8].upper()
            return f"ERR-{error_hash}"

    def _cache_software_ids(self, data: Dict[str, str]) -> None:
        """
        Cache em arquivo temporário para performance.
        Invalida cache se hardware mudar significativamente.
        """
        try:
            from src.utils.logger import logger

            # Adiciona timestamp e dados de hardware para validação
            cache_data = {
                'timestamp': time.time(),
                'hardware_fingerprint': self._get_hardware_fingerprint(),
                'data': data
            }

            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)

            logger.log_info("Dados de software cached com sucesso", "CACHE")

        except Exception as e:
            from src.utils.logger import logger
            logger.log_error(f"Erro ao salvar cache: {str(e)}", "CACHE")

    def _load_cached_software_ids(self) -> Optional[Dict[str, str]]:
        """
        Carrega dados cached se ainda válidos.
        """
        try:
            if not os.path.exists(self.cache_file):
                return None

            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

            # Verifica timeout
            if time.time() - cache_data['timestamp'] > self.cache_timeout:
                from src.utils.logger import logger
                logger.log_info("Cache expirado", "CACHE")
                return None

            # Verifica se hardware mudou significativamente
            current_fingerprint = self._get_hardware_fingerprint()
            if cache_data['hardware_fingerprint'] != current_fingerprint:
                from src.utils.logger import logger
                logger.log_info("Hardware mudou - invalidando cache", "CACHE")
                return None

            from src.utils.logger import logger
            logger.log_info("Dados carregados do cache", "CACHE")
            return cache_data['data']

        except Exception as e:
            from src.utils.logger import logger
            logger.log_error(f"Erro ao carregar cache: {str(e)}", "CACHE")
            return None

    def _get_hardware_fingerprint(self) -> str:
        """
        Gera fingerprint do hardware para validar cache.
        """
        try:
            hw_data = self.get_all_hardware_ids()
            fingerprint_data = {
                'motherboard': hw_data.get('motherboard', ''),
                'bios': hw_data.get('bios', ''),
                'cpu': hw_data.get('cpu', ''),
                'smbios_uuid': hw_data.get('smbios_uuid', '')
            }
            return hashlib.md5(json.dumps(fingerprint_data, sort_keys=True).encode()).hexdigest()
        except:
            return "fingerprint_error"

    def _get_software_identifiers_safe(self) -> Dict[str, str]:
        """
        Versão robusta com fallback gradativo para coleta de identificadores de software:
        1. Tenta método principal
        2. Tenta método alternativo
        3. Usa valores cached se disponível
        4. Fallback para valores gerados
        """
        from src.utils.logger import logger

        start_time = time.time()
        logger.log_info("Iniciando coleta segura de identificadores de software", "SOFTWARE_IDS")

        # Tenta carregar do cache primeiro
        cached_data = self._load_cached_software_ids()
        if cached_data:
            logger.log_success("Dados carregados do cache", "SOFTWARE_IDS")
            return cached_data

        software_ids = {}

        # Windows MachineGuid
        try:
            logger.log_info("Coletando Machine GUID", "SOFTWARE_IDS")
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography", 0, winreg.KEY_READ) as key:
                software_ids['machine_guid'] = winreg.QueryValueEx(key, "MachineGuid")[0]
            logger.log_success("Machine GUID coletado com sucesso", "SOFTWARE_IDS")
        except FileNotFoundError:
            software_ids['machine_guid'] = "Não Encontrado"
            logger.log_warning("Machine GUID não encontrado no registro", "SOFTWARE_IDS")
        except PermissionError:
            software_ids['machine_guid'] = "Sem Permissão"
            logger.log_error("Sem permissão para ler Machine GUID", "SOFTWARE_IDS")
        except Exception as e:
            software_ids['machine_guid'] = f"Erro: {str(e)[:50]}"
            logger.log_error(f"Erro ao coletar Machine GUID: {str(e)}", "SOFTWARE_IDS")

        # Windows ProductId
        try:
            logger.log_info("Coletando Product ID", "SOFTWARE_IDS")
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion", 0, winreg.KEY_READ) as key:
                software_ids['product_id'] = winreg.QueryValueEx(key, "ProductId")[0]
            logger.log_success("Product ID coletado com sucesso", "SOFTWARE_IDS")
        except FileNotFoundError:
            software_ids['product_id'] = "Não Encontrado"
            logger.log_warning("Product ID não encontrado no registro", "SOFTWARE_IDS")
        except PermissionError:
            software_ids['product_id'] = "Sem Permissão"
            logger.log_error("Sem permissão para ler Product ID", "SOFTWARE_IDS")
        except Exception as e:
            software_ids['product_id'] = f"Erro: {str(e)[:50]}"
            logger.log_error(f"Erro ao coletar Product ID: {str(e)}", "SOFTWARE_IDS")

        # Rockstar Games GUID
        try:
            logger.log_info("Coletando Rockstar GUID", "SOFTWARE_IDS")
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Rockstar Games", 0, winreg.KEY_READ) as key:
                software_ids['rockstar_guid'] = winreg.QueryValueEx(key, "GUID")[0]
            logger.log_success("Rockstar GUID coletado com sucesso", "SOFTWARE_IDS")
        except FileNotFoundError:
            software_ids['rockstar_guid'] = "Não Instalado"
            logger.log_info("Rockstar Games não instalado", "SOFTWARE_IDS")
        except PermissionError:
            software_ids['rockstar_guid'] = "Sem Permissão"
            logger.log_error("Sem permissão para ler Rockstar GUID", "SOFTWARE_IDS")
        except Exception as e:
            software_ids['rockstar_guid'] = f"Erro: {str(e)[:50]}"
            logger.log_error(f"Erro ao coletar Rockstar GUID: {str(e)}", "SOFTWARE_IDS")

        # FiveM GUID (múltiplas localizações)
        fivem_guid = "Não Instalado"
        fivem_locations = [
            (winreg.HKEY_CURRENT_USER, r"Software\Cfx.re"),
            (winreg.HKEY_CURRENT_USER, r"Software\CitizenFX"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\CitizenFX")
        ]

        for hive, path in fivem_locations:
            try:
                logger.log_info(f"Verificando FiveM em {path}", "SOFTWARE_IDS")
                with winreg.OpenKey(hive, path, 0, winreg.KEY_READ) as key:
                    fivem_guid = winreg.QueryValueEx(key, "guid")[0] if path == r"Software\Cfx.re" else winreg.QueryValueEx(key, "GUID")[0]
                logger.log_success(f"FiveM GUID encontrado em {path}", "SOFTWARE_IDS")
                break
            except FileNotFoundError:
                continue
            except Exception as e:
                logger.log_error(f"Erro ao verificar FiveM em {path}: {str(e)}", "SOFTWARE_IDS")
                continue

        software_ids['fivem_guid'] = fivem_guid

        # Windows Activation
        try:
            logger.log_info("Detectando status de ativação do Windows", "SOFTWARE_IDS")
            software_ids['windows_activation'] = self._get_windows_activation_status()
        except Exception as e:
            software_ids['windows_activation'] = "Erro na Detecção"
            logger.log_error(f"Erro ao detectar ativação do Windows: {str(e)}", "SOFTWARE_IDS")

        # Installation ID
        try:
            logger.log_info("Gerando Installation ID", "SOFTWARE_IDS")
            software_ids['installation_id'] = self._get_installation_id()
        except Exception as e:
            software_ids['installation_id'] = f"ERR-{hashlib.md5(str(e).encode()).hexdigest()[:8]}"
            logger.log_error(f"Erro ao gerar Installation ID: {str(e)}", "SOFTWARE_IDS")

        # Cache os resultados
        self._cache_software_ids(software_ids)

        elapsed_time = time.time() - start_time
        logger.log_success(f"Coleta de identificadores concluída em {elapsed_time:.2f}s", "SOFTWARE_IDS")

        return software_ids

    def get_software_identifiers(self):
        """
        Coleta todos os identificadores de software do sistema usando método seguro.
        Mantém compatibilidade com interface existente.
        """
        try:
            return self._get_software_identifiers_safe()
        except Exception as e:
            from src.utils.logger import logger
            logger.log_error(f"Erro crítico na coleta de identificadores: {str(e)}", "SOFTWARE_IDS")
            # Fallback final para manter compatibilidade
            return {
                'machine_guid': 'Erro Crítico',
                'product_id': 'Erro Crítico',
                'rockstar_guid': 'Erro Crítico',
                'fivem_guid': 'Erro Crítico',
                'windows_activation': 'Erro Crítico',
                'installation_id': 'Erro Crítico'
            }

    def get_comprehensive_hardware_data(self, mac_spoofer=None):
        """
        Obtém dados completos de hardware + GUIDs do sistema
        """
        hw_data = self.get_formatted_hardware_data(mac_spoofer)
        software_ids = self.get_software_identifiers()
        
        # Combina ambos os datasets
        comprehensive_data = {**hw_data, **software_ids}
        return comprehensive_data
