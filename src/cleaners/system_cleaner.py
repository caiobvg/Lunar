# src/cleaners/system_cleaner.py

import os
import shutil
import subprocess
import winreg
import tempfile
import glob
from pathlib import Path
import psutil
import random
import string
import time
from datetime import datetime
from utils.logger import logger
from .system_paths import (
    PROCESSES_TO_KILL,
    FIVEM_PATHS,
    DISCORD_PATHS,
    SYSTEM_TEMP_PATHS,
    BROWSER_CACHE_PATHS,
    REGISTRY_CLEANING_PATHS,
    DISCORD_CACHE_PATHS,
    DISCORD_STORAGE_PATHS
)

class SystemCleaner:
    def __init__(self):
        self.total_operations = 0
        self.completed_operations = 0
        self.processes_to_kill = PROCESSES_TO_KILL
        self.fivem_paths = FIVEM_PATHS
        self.discord_paths = DISCORD_PATHS
        self.system_temp_paths = SYSTEM_TEMP_PATHS
        self.browser_cache_paths = BROWSER_CACHE_PATHS
        self.registry_cleaning_paths = REGISTRY_CLEANING_PATHS
        self.discord_cache_paths = DISCORD_CACHE_PATHS
        self.discord_storage_paths = DISCORD_STORAGE_PATHS

    def get_progress(self):
        """Calculate current progress percentage"""
        if self.total_operations == 0:
            return 0
        return (self.completed_operations / self.total_operations) * 100

    def timed_operation(self, operation_name, operation_func):
        """Execute operation with timing and logging"""
        start_time = time.time()
        logger.info(f"Starting: {operation_name}", context="CLEANER")
        
        try:
            result = operation_func()
            elapsed_time = time.time() - start_time
            logger.success(f"{operation_name} - Done in {elapsed_time:.2f}s", context="CLEANER")
            return result
        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"{operation_name} - Failed after {elapsed_time:.2f}s: {str(e)}", context="CLEANER")
            raise
    
    def kill_target_processes(self):
        """Kill target processes with better detection"""
        def _kill():
            killed = 0
            
            # First pass - normal kill
            for proc in psutil.process_iter(['name', 'pid']):
                try:
                    proc_name = proc.info['name'].lower() if proc.info['name'] else ''
                    for target in self.processes_to_kill:
                        if target in proc_name:
                            try:
                                proc.kill()
                                proc.wait(timeout=3)  # Wait for termination
                                killed += 1
                                logger.info(f"Killed: {proc.info['name']} (PID: {proc.info['pid']})", context="TERMINATE")
                                break
                            except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                                # Process already dead or stuck
                                continue
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            # Second pass - force kill stubborn processes
            time.sleep(1)  # Let system process kills
            for proc in psutil.process_iter(['name']):
                try:
                    proc_name = proc.info['name'].lower() if proc.info['name'] else ''
                    for target in self.processes_to_kill:
                        if target in proc_name:
                            try:
                                proc.kill()
                                killed += 1
                                logger.warning(f"Forcefully terminated: {proc.info['name']}", context="TERMINATE")
                            except:
                                continue
                except:
                    continue
            
            logger.info(f"{killed} processes terminated", context="STATUS")
            return killed > 0
        
        return self.timed_operation("Process Termination", _kill)
    
    def clean_fivem_cache(self):
        """Clean FiveM cache but keep important files"""
        def _clean():
            # Files we DON'T want to delete
            FILE_BLACKLIST = [
                'fivem.exe',
                'fiveguard.exe', 
                'fxserver.exe',
                'fivem.app',
                'fivem',
                'citizenfx.exe'
            ]
            
            cleaned_count = 0
            for path in self.fivem_paths:
                if os.path.exists(path):
                    try:
                        shutil.rmtree(path, ignore_errors=True)
                        cleaned_count += 1
                        logger.info(f"Purged directory: {os.path.basename(path)}", context="CLEAN")
                    except Exception as e:
                        logger.warning(f"Failed to delete {path}: {str(e)}", context="CLEAN")
            
            # Clean specific file types but skip blacklisted files
            fivem_app_path = os.path.join(os.environ['LOCALAPPDATA'], 'FiveM', 'FiveM.app')
            if os.path.exists(fivem_app_path):
                try:
                    # File patterns to clean
                    file_patterns = [
                        '*.bin', '*.dll', '*.ini', '*.xml', '*.log', '*.tmp',
                        'cache*.dat', '*.cfg', '*.json'
                    ]
                    
                    for pattern in file_patterns:
                        for file_path in glob.glob(os.path.join(fivem_app_path, '**', pattern), recursive=True):
                            try:
                                # Check if file is blacklisted
                                filename = os.path.basename(file_path).lower()
                                if any(blacklisted_file in filename for blacklisted_file in FILE_BLACKLIST):
                                    logger.debug(f"Preserved blacklisted file: {filename}", context="BLACKLIST")
                                    continue
                                    
                                os.remove(file_path)
                                cleaned_count += 1
                                logger.info(f"Removed file: {os.path.basename(file_path)}", context="DELETE")
                            except Exception as e:
                                logger.warning(f"Failed to remove {file_path}: {str(e)}", context="DELETE")
                except Exception as e:
                    logger.warning(f"Error scanning FiveM files: {str(e)}", context="CLEAN")
            
            logger.info(f"FiveM cleanup: {cleaned_count} items removed", context="STATUS")
            return cleaned_count > 0
        
        return self.timed_operation("FiveM Cache Purge", _clean)
    
    def spoof_discord_rpc(self):
        """Rename Discord RPC modules to break tracking"""
        def _clean():
            renamed_count = 0
            for base_path in self.discord_paths:
                if os.path.exists(base_path):
                    try:
                        # Find version folders (like 0.0.309)
                        for item in os.listdir(base_path):
                            version_path = os.path.join(base_path, item)
                            
                            # Check if it's a version folder
                            if os.path.isdir(version_path) and any(c.isdigit() for c in item):
                                modules_path = os.path.join(version_path, 'modules')
                                if os.path.exists(modules_path):
                                    for module_item in os.listdir(modules_path):
                                        # Find RPC modules
                                        if 'discord_rpc' in module_item.lower() or 'rpc' in module_item.lower():
                                            old_path = os.path.join(modules_path, module_item)
                                            new_name = f"discord_rpc_{random.randint(10000, 99999)}"
                                            new_path = os.path.join(modules_path, new_name)
                                            try:
                                                if os.path.exists(old_path):
                                                    os.rename(old_path, new_path)
                                                    renamed_count += 1
                                                    logger.info(f"Renamed RPC: {module_item} -> {new_name}", context="MODIFY")
                                            except Exception as e:
                                                logger.warning(f"Failed to rename {module_item}: {str(e)}", context="MODIFY")
                    except Exception as e:
                        logger.error(f"Error in {base_path}: {str(e)}", context="CLEAN")
            
            # Clean Discord caches
            for cache_path in self.discord_cache_paths:
                if os.path.exists(cache_path):
                    try:
                        shutil.rmtree(cache_path, ignore_errors=True)
                        logger.info(f"Cleared cache: {os.path.basename(cache_path)}", context="CLEAN")
                    except Exception as e:
                        logger.warning(f"Failed to clear {cache_path}: {str(e)}", context="CLEAN")
            
            # Clean Discord storage
            for storage_path in self.discord_storage_paths:
                if os.path.exists(storage_path):
                    try:
                        shutil.rmtree(storage_path, ignore_errors=True)
                        logger.info(f"Cleared storage: {os.path.basename(storage_path)}", context="CLEAN")
                    except Exception as e:
                        logger.warning(f"Failed to clear {storage_path}: {str(e)}", context="CLEAN")
            
            logger.info(f"Discord spoofing: {renamed_count} RPC modules modified", context="STATUS")
            return renamed_count > 0
        
        return self.timed_operation("Discord RPC Spoofing", _clean)
    
    def clean_system_temp(self):
        """Clean system temp files safely"""
        def _clean():
            cleaned_count = 0
            for temp_path in self.system_temp_paths:
                if os.path.exists(temp_path):
                    try:
                        # Be careful with system files
                        for item in os.listdir(temp_path):
                            item_path = os.path.join(temp_path, item)
                            try:
                                # Skip system-critical files
                                if not item.startswith('System') and not item in ['Windows', 'system']:
                                    if os.path.isfile(item_path):
                                        os.remove(item_path)
                                        cleaned_count += 1
                                    elif os.path.isdir(item_path):
                                        # Only safe directories
                                        dir_blacklist = ['Windows', 'System', 'Boot']
                                        if not any(blacklisted in item for blacklisted in dir_blacklist):
                                            shutil.rmtree(item_path, ignore_errors=True)
                                            cleaned_count += 1
                            except Exception as e:
                                # Skip problematic files
                                continue
                    except Exception as e:
                        logger.warning(f"Error cleaning {temp_path}: {str(e)}", context="CLEAN")
            
            for browser_path in self.browser_cache_paths:
                if os.path.exists(browser_path):
                    try:
                        shutil.rmtree(browser_path, ignore_errors=True)
                        cleaned_count += 1
                        logger.info(f"Cleared browser cache: {os.path.basename(browser_path)}", context="CLEAN")
                    except Exception as e:
                        logger.warning(f"Failed to clear {browser_path}: {str(e)}", context="CLEAN")
            
            logger.info(f"Temp files: {cleaned_count} items removed", context="CLEAN")
            return cleaned_count > 0
        
        return self.timed_operation("System Temp Cleanup", _clean)
    
    def reset_network(self):
        """Reset network stack and clear caches"""
        def _reset():
            commands = [
                ('DNS Flush', ['ipconfig', '/flushdns']),
                ('Winsock Reset', ['netsh', 'winsock', 'reset']),
                ('IP Reset', ['netsh', 'int', 'ip', 'reset', 'reset.log']),
                ('TCP Reset', ['netsh', 'int', 'tcp', 'set', 'global', 'autotuninglevel=normal']),
                ('Firewall Reset', ['netsh', 'advfirewall', 'reset']),
                ('Proxy Reset', ['netsh', 'winhttp', 'reset', 'proxy']),
            ]
            
            success_count = 0
            for name, cmd in commands:
                try:
                    # Special handling for IP reset
                    if name == 'IP Reset':
                        try:
                            # Run with file output
                            with open('reset.log', 'w') as f:
                                result = subprocess.run(cmd[:-1], stdout=f, stderr=subprocess.PIPE, 
                                                      timeout=30, shell=True, text=True)
                            if os.path.exists('reset.log'):
                                os.remove('reset.log')  # Cleanup log
                            success_count += 1
                            logger.info(f"{name}: Success", context="NETWORK")
                        except Exception as e:
                            logger.warning(f"{name}: Partial - {str(e)}", context="NETWORK")
                    else:
                        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, shell=True)
                        if result.returncode == 0:
                            success_count += 1
                            logger.info(f"{name}: Success", context="NETWORK")
                        else:
                            # Try alternative method
                            try:
                                alt_result = subprocess.run(cmd, timeout=30, shell=True)
                                if alt_result.returncode == 0:
                                    success_count += 1
                                    logger.info(f"{name}: Success (alt)", context="NETWORK")
                                else:
                                    logger.warning(f"{name}: Failed", context="NETWORK")
                            except:
                                logger.warning(f"{name}: Failed", context="NETWORK")
                except Exception as e:
                    logger.warning(f"{name}: Error - {str(e)}", context="NETWORK")
            
            # Extra network cleanup
            try:
                subprocess.run(['nbtstat', '-R'], capture_output=True, shell=True)
                subprocess.run(['nbtstat', '-RR'], capture_output=True, shell=True)
                logger.info("NetBIOS cache cleared", context="NETWORK")
            except:
                pass
            
            logger.info(f"Network reset: {success_count}/{len(commands)} operations", context="STATUS")
            return success_count >= 3  # Most should work
        
        return self.timed_operation("Network Stack Reset", _reset)
    
    def clean_registry_entries(self):
        """Clean registry entries safely"""
        def _clean():
            cleaned_count = 0
            
            # Try reg.exe first (better permissions)
            for key_path, hive_str in self.registry_cleaning_paths:
                try:
                    # Convert hive for reg.exe
                    if hive_str == 'HKEY_CURRENT_USER':
                        reg_hive = "HKCU"
                        hive = winreg.HKEY_CURRENT_USER
                    else:
                        continue # Add other hives later if needed
                    
                    # Try reg.exe deletion
                    cmd = ['reg', 'delete', f"{reg_hive}\\{key_path}", '/f']
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, shell=True)
                    
                    if result.returncode == 0:
                        cleaned_count += 1
                        logger.info(f"Deleted key: {key_path}", context="REGISTRY")
                    else:
                        # Fallback to Python method
                        try:
                            # Check if key exists
                            try:
                                key = winreg.OpenKey(hive, key_path, 0, winreg.KEY_READ)
                                winreg.CloseKey(key)
                                
                                # Try to delete
                                try:
                                    winreg.DeleteKey(hive, key_path)
                                    cleaned_count += 1
                                    logger.info(f"Cleaned key: {key_path}", context="REGISTRY")
                                except PermissionError:
                                    # Try recursive deletion
                                    try:
                                        key = winreg.OpenKey(hive, key_path, 0, winreg.KEY_ALL_ACCESS)
                                        # Delete subkeys first
                                        try:
                                            i = 0
                                            while True:
                                                try:
                                                    subkey_name = winreg.EnumKey(key, i)
                                                    winreg.DeleteKey(key, subkey_name)
                                                    i += 1
                                                except WindowsError:
                                                    break
                                            winreg.CloseKey(key)
                                            winreg.DeleteKey(hive, key_path)
                                            cleaned_count += 1
                                            logger.info(f"Recursively cleaned key: {key_path}", context="REGISTRY")
                                        except:
                                            logger.warning(f"Complex recursive delete failed for: {key_path}", context="REGISTRY")
                                    except:
                                        logger.warning(f"Permission denied for key: {key_path}", context="REGISTRY")
                            except FileNotFoundError:
                                logger.debug(f"Registry key not found: {key_path}", context="REGISTRY")
                        except Exception as e:
                            logger.warning(f"Failed to clean {key_path}: {str(e)}", context="REGISTRY")
                except Exception as e:
                    logger.error(f"Registry error for {key_path}: {str(e)}", context="REGISTRY")
            
            # Extra cleanup for stubborn keys
            stubborn_keys = [
                r"HKCU\Software\CitizenFX",
                r"HKCU\Software\FiveM", 
                r"HKCU\Software\Rockstar Games",
            ]
            
            for key in stubborn_keys:
                try:
                    # Multiple deletion methods
                    methods = [
                        ['reg', 'delete', key, '/f', '/va'],
                        ['reg', 'delete', key, '/f'],
                    ]
                    
                    for cmd in methods:
                        result = subprocess.run(cmd, capture_output=True, timeout=5, shell=True)
                        if result.returncode == 0:
                            cleaned_count += 1
                            logger.info(f"Removed stubborn key: {key}", context="REGISTRY")
                            break
                except:
                    continue
            
            logger.info(f"Registry cleanup: {cleaned_count} entries", context="STATUS")
            return cleaned_count > 0
        
        return self.timed_operation("Registry Cleanup", _clean)
    
    def execute_real_spoofing(self):
        """Main method - execute full spoofing routine"""
        start_time = time.time()
        logger.info("=" * 60, context="SPOOFING")
        logger.info("STARTING SPOOFING PROTOCOL", context="SPOOFING")
        logger.info("Performing ACTUAL system modifications", context="SPOOFING")
        logger.info("=" * 60, context="SPOOFING")
        
        # Operations in optimal order
        operations = [
            ("Killing processes", self.kill_target_processes),
            ("Cleaning temp files", self.clean_system_temp),
            ("Spoofing Discord", self.spoof_discord_rpc),
            ("Cleaning FiveM", self.clean_fivem_cache),
            ("Cleaning registry", self.clean_registry_entries),
            ("Resetting network", self.reset_network),
        ]
        
        self.total_operations = len(operations)
        self.completed_operations = 0
        
        results = []
        for op_name, op_function in operations:
            logger.info(f"Running: {op_name}", context="SPOOFING")
            try:
                result = op_function()
                results.append(result)
                self.completed_operations += 1
                progress = self.get_progress()
                logger.info(f"Progress: {self.completed_operations}/{self.total_operations} ({progress:.1f}%)", context="SPOOFING")
            except Exception as e:
                logger.error(f"{op_name} failed: {str(e)}", context="SPOOFING")
                results.append(False)
        
        success_count = sum(1 for r in results if r)
        total_time = time.time() - start_time
        
        logger.info("=" * 60, context="SPOOFING")
        logger.info(f"SPOOFING COMPLETE: {success_count}/{self.total_operations} operations successful", context="SPOOFING")
        logger.info(f"Total time: {total_time:.2f}s", context="STATS")
        
        if success_count >= 4:  # Most operations successful
            logger.success("✅ SPOOFING SUCCESSFUL!", context="SPOOFING")
            logger.info("Discord RPC modified", context="SPOOFING")
            logger.info("FiveM cache cleared", context="SPOOFING")
            logger.info("System identity spoofed", context="SPOOFING")
        else:
            logger.warning("⚠️ Partial success - some operations failed", context="SPOOFING")
        
        logger.info("=" * 60, context="SPOOFING")
        
        return success_count >= 4
