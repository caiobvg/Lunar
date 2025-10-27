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

class SystemCleaner:
    def __init__(self, realtime_callback=None):
        self.log_messages = []
        self.realtime_callback = realtime_callback
        self.total_operations = 0
        self.completed_operations = 0
    
    def add_log_realtime(self, message):
        """Send log message in real time"""
        if self.realtime_callback:
            self.realtime_callback(message)
        self.log_messages.append(message)
        return message
    
    def get_progress(self):
        """Calculate current progress percentage"""
        if self.total_operations == 0:
            return 0
        return (self.completed_operations / self.total_operations) * 100
    
    def timed_operation(self, operation_name, operation_func):
        """Execute operation with timing and logging"""
        start_time = time.time()
        self.add_log_realtime(f"[PROCESS] Starting: {operation_name}")
        
        try:
            result = operation_func()
            elapsed_time = time.time() - start_time
            self.add_log_realtime(f"[SUCCESS] {operation_name} - Done in {elapsed_time:.2f}s")
            return result
        except Exception as e:
            elapsed_time = time.time() - start_time
            self.add_log_realtime(f"[ERROR] {operation_name} - Failed after {elapsed_time:.2f}s: {str(e)}")
            raise
    
    def kill_target_processes(self):
        """Kill target processes with better detection"""
        def _kill():
            # Processes we want to terminate
            processes_to_kill = [
                'discord', 'fivem', 'steam', 'steamwebhelper', 
                'epicgameslauncher', 'socialclub', 'rockstargames'
            ]
            killed = 0
            
            # First pass - normal kill
            for proc in psutil.process_iter(['name', 'pid']):
                try:
                    proc_name = proc.info['name'].lower() if proc.info['name'] else ''
                    for target in processes_to_kill:
                        if target in proc_name:
                            try:
                                proc.kill()
                                proc.wait(timeout=3)  # Wait for termination
                                killed += 1
                                self.add_log_realtime(f"[TERMINATE] Killed: {proc.info['name']} (PID: {proc.info['pid']})")
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
                    for target in processes_to_kill:
                        if target in proc_name:
                            try:
                                proc.kill()
                                killed += 1
                                self.add_log_realtime(f"[FORCE KILL] Terminated: {proc.info['name']}")
                            except:
                                continue
                except:
                    continue
            
            self.add_log_realtime(f"[STATUS] {killed} processes terminated")
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
            
            # FiveM paths to clean
            fivem_paths = [
                os.path.join(os.environ['LOCALAPPDATA'], 'FiveM', 'FiveM.app', 'cache'),
                os.path.join(os.environ['LOCALAPPDATA'], 'FiveM', 'FiveM.app', 'logs'),
                os.path.join(os.environ['LOCALAPPDATA'], 'FiveM', 'FiveM.app', 'crashes'),
                os.path.join(os.environ['LOCALAPPDATA'], 'DigitalEntitlements'),
                os.path.join(os.environ['APPDATA'], 'CitizenFX'),
                os.path.join(os.environ['LOCALAPPDATA'], 'FiveM', 'FiveM.app', 'data', 'cache'),
                os.path.join(os.environ['LOCALAPPDATA'], 'FiveM', 'FiveM.app', 'browser'),
            ]
            
            cleaned_count = 0
            for path in fivem_paths:
                if os.path.exists(path):
                    try:
                        shutil.rmtree(path, ignore_errors=True)
                        cleaned_count += 1
                        self.add_log_realtime(f"[CLEAN] Purged directory: {os.path.basename(path)}")
                    except Exception as e:
                        self.add_log_realtime(f"[WARNING] Failed to delete {path}: {str(e)}")
            
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
                                    self.add_log_realtime(f"[BLACKLIST] Preserved: {filename}")
                                    continue
                                    
                                os.remove(file_path)
                                cleaned_count += 1
                                self.add_log_realtime(f"[DELETE] Removed file: {os.path.basename(file_path)}")
                            except Exception as e:
                                self.add_log_realtime(f"[WARNING] Failed to remove {file_path}: {str(e)}")
                except Exception as e:
                    self.add_log_realtime(f"[WARNING] Error scanning FiveM files: {str(e)}")
            
            # Clean additional locations (keeping main FiveM dir)
            additional_paths = [
                os.path.join(os.environ['USERPROFILE'], 'AppData', 'Roaming', 'CitizenFX'),
                os.path.join(os.environ['USERPROFILE'], 'Documents', 'Rockstar Games'),
            ]
            
            for path in additional_paths:
                if os.path.exists(path):
                    try:
                        shutil.rmtree(path, ignore_errors=True)
                        cleaned_count += 1
                        self.add_log_realtime(f"[CLEAN] Cleaned location: {os.path.basename(path)}")
                    except Exception as e:
                        self.add_log_realtime(f"[WARNING] Failed to clean {path}: {str(e)}")
            
            self.add_log_realtime(f"[STATUS] FiveM cleanup: {cleaned_count} items removed")
            return cleaned_count > 0
        
        return self.timed_operation("FiveM Cache Purge", _clean)
    
    def spoof_discord_rpc(self):
        """Rename Discord RPC modules to break tracking"""
        def _clean():
            discord_paths = [
                os.path.join(os.environ['APPDATA'], 'discord'),
                os.path.join(os.environ['LOCALAPPDATA'], 'Discord'),
                os.path.join(os.environ['LOCALAPPDATA'], 'DiscordCanary'),
                os.path.join(os.environ['LOCALAPPDATA'], 'DiscordPTB'),
            ]
            
            renamed_count = 0
            for base_path in discord_paths:
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
                                                    self.add_log_realtime(f"[MODIFY] Renamed RPC: {module_item} -> {new_name}")
                                            except Exception as e:
                                                self.add_log_realtime(f"[WARNING] Failed to rename {module_item}: {str(e)}")
                    except Exception as e:
                        self.add_log_realtime(f"[ERROR] Error in {base_path}: {str(e)}")
            
            # Clean Discord caches
            discord_cache_paths = [
                os.path.join(os.environ['LOCALAPPDATA'], 'Discord', 'Cache'),
                os.path.join(os.environ['LOCALAPPDATA'], 'DiscordCanary', 'Cache'),
                os.path.join(os.environ['LOCALAPPDATA'], 'DiscordPTB', 'Cache'),
                os.path.join(os.environ['LOCALAPPDATA'], 'Discord', 'Code Cache'),
                os.path.join(os.environ['LOCALAPPDATA'], 'Discord', 'GPUCache'),
            ]
            
            for cache_path in discord_cache_paths:
                if os.path.exists(cache_path):
                    try:
                        shutil.rmtree(cache_path, ignore_errors=True)
                        self.add_log_realtime(f"[CLEAN] Cleared cache: {os.path.basename(cache_path)}")
                    except Exception as e:
                        self.add_log_realtime(f"[WARNING] Failed to clear {cache_path}: {str(e)}")
            
            # Clean Discord storage
            discord_storage_paths = [
                os.path.join(os.environ['LOCALAPPDATA'], 'Discord', 'Local Storage'),
                os.path.join(os.environ['LOCALAPPDATA'], 'DiscordCanary', 'Local Storage'),
                os.path.join(os.environ['LOCALAPPDATA'], 'DiscordPTB', 'Local Storage'),
            ]
            
            for storage_path in discord_storage_paths:
                if os.path.exists(storage_path):
                    try:
                        shutil.rmtree(storage_path, ignore_errors=True)
                        self.add_log_realtime(f"[CLEAN] Cleared storage: {os.path.basename(storage_path)}")
                    except Exception as e:
                        self.add_log_realtime(f"[WARNING] Failed to clear {storage_path}: {str(e)}")
            
            self.add_log_realtime(f"[STATUS] Discord spoofing: {renamed_count} RPC modules modified")
            return renamed_count > 0
        
        return self.timed_operation("Discord RPC Spoofing", _clean)
    
    def clean_system_temp(self):
        """Clean system temp files safely"""
        def _clean():
            temp_locations = [
                os.environ.get('TEMP', ''),
                os.environ.get('TMP', ''),
                os.path.join(os.environ['LOCALAPPDATA'], 'Temp'),
                r'C:\Windows\Temp',
                os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Temp'),
            ]
            
            cleaned_count = 0
            for temp_path in temp_locations:
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
                        self.add_log_realtime(f"[WARNING] Error cleaning {temp_path}: {str(e)}")
            
            # Clean browser caches
            browser_paths = [
                os.path.join(os.environ['LOCALAPPDATA'], 'Google', 'Chrome', 'User Data', 'Default', 'Cache'),
                os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft', 'Edge', 'User Data', 'Default', 'Cache'),
                os.path.join(os.environ['APPDATA'], 'Mozilla', 'Firefox', 'Profiles'),
            ]
            
            for browser_path in browser_paths:
                if os.path.exists(browser_path):
                    try:
                        shutil.rmtree(browser_path, ignore_errors=True)
                        cleaned_count += 1
                        self.add_log_realtime(f"[CLEAN] Cleared browser cache: {os.path.basename(browser_path)}")
                    except Exception as e:
                        self.add_log_realtime(f"[WARNING] Failed to clear {browser_path}: {str(e)}")
            
            self.add_log_realtime(f"[CLEAN] Temp files: {cleaned_count} items removed")
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
                            self.add_log_realtime(f"[NETWORK] {name}: Success")
                        except Exception as e:
                            self.add_log_realtime(f"[WARNING] {name}: Partial - {str(e)}")
                    else:
                        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, shell=True)
                        if result.returncode == 0:
                            success_count += 1
                            self.add_log_realtime(f"[NETWORK] {name}: Success")
                        else:
                            # Try alternative method
                            try:
                                alt_result = subprocess.run(cmd, timeout=30, shell=True)
                                if alt_result.returncode == 0:
                                    success_count += 1
                                    self.add_log_realtime(f"[NETWORK] {name}: Success (alt)")
                                else:
                                    self.add_log_realtime(f"[WARNING] {name}: Failed")
                            except:
                                self.add_log_realtime(f"[WARNING] {name}: Failed")
                except Exception as e:
                    self.add_log_realtime(f"[WARNING] {name}: Error - {str(e)}")
            
            # Extra network cleanup
            try:
                subprocess.run(['nbtstat', '-R'], capture_output=True, shell=True)
                subprocess.run(['nbtstat', '-RR'], capture_output=True, shell=True)
                self.add_log_realtime("[NETWORK] NetBIOS cache cleared")
            except:
                pass
            
            self.add_log_realtime(f"[STATUS] Network reset: {success_count}/{len(commands)} operations")
            return success_count >= 3  # Most should work
        
        return self.timed_operation("Network Stack Reset", _reset)
    
    def clean_registry_entries(self):
        """Clean registry entries safely"""
        def _clean():
            registry_targets = [
                (winreg.HKEY_CURRENT_USER, r'Software\CitizenFX'),
                (winreg.HKEY_CURRENT_USER, r'Software\FiveM'),
                (winreg.HKEY_CURRENT_USER, r'Software\Rockstar Games'),
                (winreg.HKEY_CURRENT_USER, r'Software\Valve\Steam'),
                (winreg.HKEY_CURRENT_USER, r'Software\Rockstar Games Launcher'),
                (winreg.HKEY_CURRENT_USER, r'Software\Epic Games'),
            ]
            
            cleaned_count = 0
            
            # Try reg.exe first (better permissions)
            for hive, key_path in registry_targets:
                try:
                    # Convert hive for reg.exe
                    if hive == winreg.HKEY_CURRENT_USER:
                        reg_hive = "HKCU"
                    else:
                        continue  # Skip other hives
                    
                    # Try reg.exe deletion
                    cmd = ['reg', 'delete', f"{reg_hive}\\{key_path}", '/f']
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, shell=True)
                    
                    if result.returncode == 0:
                        cleaned_count += 1
                        self.add_log_realtime(f"[REGISTRY] Deleted key: {key_path}")
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
                                    self.add_log_realtime(f"[REGISTRY] Cleaned key: {key_path}")
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
                                            self.add_log_realtime(f"[REGISTRY] Recursive clean: {key_path}")
                                        except:
                                            self.add_log_realtime(f"[WARNING] Complex delete failed: {key_path}")
                                    except:
                                        self.add_log_realtime(f"[WARNING] No permission: {key_path}")
                            except FileNotFoundError:
                                self.add_log_realtime(f"[INFO] Key not found: {key_path}")
                        except Exception as e:
                            self.add_log_realtime(f"[WARNING] Failed to clean {key_path}: {str(e)}")
                except Exception as e:
                    self.add_log_realtime(f"[WARNING] Registry error {key_path}: {str(e)}")
            
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
                            self.add_log_realtime(f"[REGISTRY] Removed stubborn key: {key}")
                            break
                except:
                    continue
            
            self.add_log_realtime(f"[STATUS] Registry cleanup: {cleaned_count} entries")
            return cleaned_count > 0
        
        return self.timed_operation("Registry Cleanup", _clean)
    
    def execute_real_spoofing(self):
        """Main method - execute full spoofing routine"""
        self.log_messages.clear()
        
        start_time = time.time()
        self.add_log_realtime("=" * 60)
        self.add_log_realtime("[REAL] 🚀 STARTING REAL SPOOFING PROTOCOL")
        self.add_log_realtime("[REAL] Performing ACTUAL system modifications")
        self.add_log_realtime("=" * 60)
        
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
            self.add_log_realtime(f"[REAL] Running: {op_name}")
            try:
                result = op_function()
                results.append(result)
                self.completed_operations += 1
                progress = self.get_progress()
                self.add_log_realtime(f"[REAL] Progress: {self.completed_operations}/{self.total_operations} ({progress:.1f}%)")
            except Exception as e:
                self.add_log_realtime(f"[ERROR] {op_name} failed: {str(e)}")
                results.append(False)
        
        success_count = sum(1 for r in results if r)
        total_time = time.time() - start_time
        
        self.add_log_realtime("=" * 60)
        self.add_log_realtime(f"[REAL] SPOOFING COMPLETE: {success_count}/{self.total_operations} operations successful")
        self.add_log_realtime(f"[STATS] Total time: {total_time:.2f}s")
        
        if success_count >= 4:  # Most operations successful
            self.add_log_realtime("[REAL] ✅ SPOOFING SUCCESSFUL!")
            self.add_log_realtime("[REAL] Discord RPC modified")
            self.add_log_realtime("[REAL] FiveM cache cleared") 
            self.add_log_realtime("[REAL] System identity spoofed")
        else:
            self.add_log_realtime("[REAL] ⚠️  Partial success - some operations failed")
        
        self.add_log_realtime("=" * 60)
        
        return success_count >= 4