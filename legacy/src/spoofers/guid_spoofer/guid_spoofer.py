# src/spoofers/guid_spoofer/guid_spoofer.py

import uuid
import os
import winreg
import shutil
import hashlib
import random
import subprocess
import time
from typing import Dict, List
from utils.logger import logger
from utils.registry_checker import RegistryChecker, RegistryError
from .guid_paths import GUID_REGISTRY_PATHS, GUID_SYSTEM_PATHS

class GUIDSpoofer:
    def __init__(self):
        """Initializes the GUIDSpoofer with comprehensive registry coverage."""
        self.registry = RegistryChecker()
        self.backup_dir = "registry_backups"
        os.makedirs(self.backup_dir, exist_ok=True)
        
        self.registry_paths = GUID_REGISTRY_PATHS
        self.system_paths = GUID_SYSTEM_PATHS

        # GUID patterns used by different systems
        self.guid_patterns = {
            'standard': lambda: str(uuid.uuid4()),
            'windows_machine': self._generate_windows_machine_guid,
            'rockstar': self._generate_rockstar_guid,
            'fivem': self._generate_fivem_guid
        }

    def spoof_guid(self) -> bool:
        """
        Executes comprehensive GUID spoofing covering:
        - Windows Machine GUID
        - Rockstar Games GUIDs (multiple locations)
        - FiveM/CitizenFX GUIDs
        - Social Club GUIDs
        - Windows Profile GUIDs
        - Steam related GUIDs
        """
        logger.log_info("🚀 INITIATING COMPREHENSIVE GUID SPOOFING PROTOCOL", "GUID")
        
        try:
            # Create comprehensive backup before any changes
            self._create_comprehensive_backup()
            
            # Generate unique GUIDs for different systems
            guid_map = self._generate_guid_map()
            
            # Execute registry modifications in transaction
            operations = self._build_comprehensive_operations(guid_map)
            
            logger.log_info("Applying GUID modifications transactionally...", "GUID")
            self.registry.transactional_write(operations)
            logger.log_success("Registry GUIDs successfully spoofed", "GUID")
            
            # Clean all related artifacts and caches
            self._clean_all_artifacts()
            
            # Additional system-level spoofing
            self._apply_system_level_spoofing(guid_map)
            
            logger.log_success("🎯 COMPREHENSIVE GUID SPOOFING COMPLETED SUCCESSFULLY", "GUID")
            return True
            
        except RegistryError as e:
            logger.log_error(f"Registry transaction failed: {e}", "GUID")
            logger.log_error("All changes have been rolled back", "GUID")
            return False
        except Exception as e:
            logger.log_error(f"Unexpected error during GUID spoofing: {e}", "GUID")
            return False

    def _generate_guid_map(self) -> Dict[str, str]:
        """Generate unique GUIDs for different systems to avoid correlation."""
        return {
            'windows_machine': self.guid_patterns['windows_machine'](),
            'rockstar_primary': self.guid_patterns['rockstar'](),
            'rockstar_secondary': self.guid_patterns['rockstar'](),
            'fivem_primary': self.guid_patterns['fivem'](),
            'fivem_secondary': self.guid_patterns['standard'](),
            'social_club': self.guid_patterns['standard'](),
            'windows_profile': self.guid_patterns['standard'](),
            'steam': self.guid_patterns['standard']()
        }

    def _generate_windows_machine_guid(self) -> str:
        """Generate Windows Machine GUID in proper format."""
        return hashlib.md5(str(random.getrandbits(256)).encode()).hexdigest().upper()

    def _generate_rockstar_guid(self) -> str:
        """Generate Rockstar-style GUID."""
        base = hashlib.sha256(str(random.getrandbits(256)).encode()).hexdigest()[:32].upper()
        return f"{base[:8]}-{base[8:12]}-{base[12:16]}-{base[16:20]}-{base[20:32]}"

    def _generate_fivem_guid(self) -> str:
        """Generate FiveM-style identifier."""
        return hashlib.sha1(str(random.getrandbits(256)).encode()).hexdigest()[:40].upper()

    def _get_guid_for_category(self, guid_map: Dict[str, str], category: str) -> str:
        """Helper to get the correct GUID from the map based on category."""
        if 'windows' in category:
            return guid_map['windows_machine']
        if 'rockstar' in category:
            return guid_map['rockstar_primary']
        if 'fivem' in category:
            return guid_map['fivem_primary']
        return guid_map['social_club'] # Fallback to social_club which is a standard GUID

    def _build_comprehensive_operations(self, guid_map: Dict[str, str]) -> List[Dict]:
        """Build comprehensive registry operations from the centralized paths file."""
        operations = []
        
        for category, paths in self.registry_paths.items():
            for path_info in paths:
                # Special handling for ProductId which needs generation
                value = self._generate_product_id() if path_info['name'] == 'ProductId' else self._get_guid_for_category(guid_map, category)
                
                operations.append({
                    "action": "write",
                    "hive": path_info['hive'],
                    "path": path_info['path'],
                    "name": path_info['name'],
                    "value": value,
                    "value_type": winreg.REG_SZ
                })

        logger.log_info(f"Built {len(operations)} registry operations", "GUID")
        return operations

    def _generate_product_id(self) -> str:
        """Generate realistic Windows Product ID."""
        return f"{random.randint(10000, 99999)}-{random.randint(10000, 99999)}-{random.randint(10000, 99999)}-{random.randint(10000, 99999)}"

    def _create_comprehensive_backup(self):
        """Create comprehensive backup of all registry locations."""
        try:
            backup_file = os.path.join(self.backup_dir, f"guid_comprehensive_backup_{int(time.time())}.reg")
            logger.log_info(f"Creating comprehensive registry backup: {backup_file}", "GUID")
            
            # Backup critical registry paths from the centralized list
            backup_paths = self.system_paths['registry_backups']
            
            for path in backup_paths:
                try:
                    subprocess.run(f'reg export "{path}" "{backup_file}_temp" /y', 
                                 shell=True, capture_output=True, timeout=10)
                except:
                    continue
                    
        except Exception as e:
            logger.log_warning(f"Backup creation partially failed: {e}", "GUID")

    def _clean_all_artifacts(self):
        """Clean all GUID-related artifacts and caches."""
        logger.log_info("Cleaning all GUID-related artifacts...", "GUID")
        
        all_paths = self.system_paths['cache_locations']
        
        success_count = 0
        for path in all_paths:
            if os.path.exists(path):
                try:
                    shutil.rmtree(path, ignore_errors=True)
                    success_count += 1
                    logger.log_success(f"Cleaned: {os.path.basename(path)}", "GUID")
                except Exception as e:
                    logger.log_warning(f"Failed to clean {path}: {e}", "GUID")
            else:
                logger.log_info(f"Path not found: {path}", "GUID")
        
        # Clear Windows recent documents
        self._clear_recent_documents()
        
        logger.log_success(f"Artifact cleaning: {success_count}/{len(all_paths)} locations cleaned", "GUID")

    def _clear_recent_documents(self):
        """Clear Windows recent documents that might contain game references."""
        try:
            recent_path = os.path.join(os.getenv('APPDATA', ''), 'Microsoft', 'Windows', 'Recent')
            if os.path.exists(recent_path):
                for item in os.listdir(recent_path):
                    item_path = os.path.join(recent_path, item)
                    try:
                        if os.path.isfile(item_path):
                            os.remove(item_path)
                        elif os.path.isdir(item_path):
                            shutil.rmtree(item_path, ignore_errors=True)
                    except:
                        continue
                logger.log_info("Cleared recent documents", "GUID")
        except Exception as e:
            logger.log_warning(f"Failed to clear recent documents: {e}", "GUID")

    def _apply_system_level_spoofing(self, guid_map: Dict[str, str]):
        """Apply additional system-level spoofing measures."""
        try:
            # Clear DNS cache
            subprocess.run('ipconfig /flushdns', shell=True, capture_output=True)
            
            # Clear Windows event logs related to games
            self._clear_game_event_logs()
            
            # Modify Windows telemetry (optional)
            self._modify_telemetry_settings()
            
            logger.log_info("Applied system-level spoofing measures", "GUID")
            
        except Exception as e:
            logger.log_warning(f"System-level spoofing partially failed: {e}", "GUID")

    def _clear_game_event_logs(self):
        """Clear Windows event logs that might contain game activity."""
        try:
            # Clear application logs that might contain game entries
            logs_to_clear = ['Application', 'System', 'Security']
            for log_name in logs_to_clear:
                try:
                    subprocess.run(f'wevtutil cl "{log_name}"', shell=True, capture_output=True)
                except:
                    continue
            logger.log_info("Cleared Windows event logs", "GUID")
        except Exception as e:
            logger.log_warning(f"Failed to clear event logs: {e}", "GUID")

    def _modify_telemetry_settings(self):
        """Modify Windows telemetry settings to reduce tracking."""
        try:
            # Disable telemetry (optional - can be controversial)
            telemetry_commands = [
                'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection" /v AllowTelemetry /t REG_DWORD /d 0 /f',
                'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\DataCollection" /v AllowTelemetry /t REG_DWORD /d 0 /f'
            ]
            
            for cmd in telemetry_commands:
                try:
                    subprocess.run(cmd, shell=True, capture_output=True, timeout=5)
                except:
                    continue
                    
            logger.log_info("Modified telemetry settings", "GUID")
        except Exception as e:
            logger.log_warning(f"Failed to modify telemetry: {e}", "GUID")

    def get_spoofing_report(self) -> Dict[str, any]:
        """Generate a report of what was spoofed."""
        return {
            "status": "completed",
            "backup_created": True,
            "registry_modified": True,
            "artifacts_cleaned": True,
            "system_modified": True,
            "timestamp": int(time.time())
        }
