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

# Relative import for logger
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.logger import logger

class SystemCleaner:
    def __init__(self, realtime_callback=None):
        self.log_messages = []
        self.realtime_callback = realtime_callback
    
    def add_log_realtime(self, message):
        """Add message to log in real time"""
        if self.realtime_callback:
            self.realtime_callback(message)
        self.log_messages.append(message)
        return message
    
    def timed_operation(self, operation_name, operation_func):
        """Execute a timed operation"""
        start_time = time.time()
        self.add_log_realtime(f"[PROCESS] Initializing: {operation_name}")
        
        try:
            result = operation_func()
            elapsed_time = time.time() - start_time
            self.add_log_realtime(f"[SUCCESS] {operation_name} - Completed in {elapsed_time:.2f}s")
            return result
        except Exception as e:
            elapsed_time = time.time() - start_time
            self.add_log_realtime(f"[ERROR] {operation_name} - Failed after {elapsed_time:.2f}s: {str(e)}")
            raise
    
    def kill_process(self, process_name):
        """Kill specific processes"""
        def _kill():
            killed = 0
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] and process_name.lower() in proc.info['name'].lower():
                    try:
                        proc.kill()
                        killed += 1
                    except:
                        continue
            if killed > 0:
                self.add_log_realtime(f"[TERMINATE] {killed} instances of {process_name} terminated")
            return killed
        
        return self.timed_operation(f"Terminate {process_name}", _kill)
    
    def clean_fivem_cache(self):
        """Clean complete FiveM cache"""
        def _clean():
            fivem_paths = [
                os.path.join(os.environ['LOCALAPPDATA'], 'FiveM', 'FiveM.app', 'cache'),
                os.path.join(os.environ['LOCALAPPDATA'], 'FiveM', 'FiveM.app', 'logs'),
                os.path.join(os.environ['LOCALAPPDATA'], 'FiveM', 'FiveM.app', 'crashes'),
                os.path.join(os.environ['LOCALAPPDATA'], 'DigitalEntitlements'),
                os.path.join(os.environ['APPDATA'], 'CitizenFX')
            ]
            
            cleaned_count = 0
            for path in fivem_paths:
                if os.path.exists(path):
                    shutil.rmtree(path, ignore_errors=True)
                    cleaned_count += 1
                    self.add_log_realtime(f"[CLEAN] Directory purged: {os.path.basename(path)}")
            
            # Remove specific FiveM files
            fivem_app_path = os.path.join(os.environ['LOCALAPPDATA'], 'FiveM', 'FiveM.app')
            if os.path.exists(fivem_app_path):
                patterns = ['*.bin', '*.dll', '*.ini', '*.XML']
                for pattern in patterns:
                    for file_path in glob.glob(os.path.join(fivem_app_path, pattern)):
                        try:
                            os.remove(file_path)
                            cleaned_count += 1
                            self.add_log_realtime(f"[DELETE] File removed: {os.path.basename(file_path)}")
                        except:
                            continue
            
            self.add_log_realtime(f"[STATUS] FiveM cleanup: {cleaned_count} items removed")
            return cleaned_count
        
        return self.timed_operation("FiveM Cache Purge", _clean)
    
    def clean_discord_rpc(self):
        """Clean and rename Discord RPC"""
        def _clean():
            discord_base_paths = [
                os.path.join(os.environ['APPDATA'], 'discord'),
                os.path.join(os.environ['LOCALAPPDATA'], 'Discord')
            ]
            
            renamed_count = 0
            for base_path in discord_base_paths:
                if os.path.exists(base_path):
                    for item in os.listdir(base_path):
                        if item.replace('.', '').isdigit():  # Versions like 0.0.309
                            modules_path = os.path.join(base_path, item, 'modules')
                            if os.path.exists(modules_path):
                                for module_item in os.listdir(modules_path):
                                    if 'discord_rpc' in module_item.lower():
                                        old_path = os.path.join(modules_path, module_item)
                                        new_name = f"discord_rpc_midnight_{''.join(random.choices(string.ascii_lowercase + string.digits, k=8))}"
                                        new_path = os.path.join(modules_path, new_name)
                                        try:
                                            os.rename(old_path, new_path)
                                            renamed_count += 1
                                            self.add_log_realtime("[MODIFY] Discord RPC identifier modified")
                                        except:
                                            continue
            
            self.kill_process('discord')
            self.add_log_realtime(f"[STATUS] Discord spoofing: {renamed_count} RPC modules altered")
            return renamed_count
        
        return self.timed_operation("Discord RPC Spoofing", _clean)
    
    def block_xbox_services(self):
        """Block Xbox services via hosts file"""
        def _block():
            hosts_path = r'C:\Windows\System32\drivers\etc\hosts'
            xbox_domains = [
                'xboxlive.com',
                'user.auth.xboxlive.com',
                'presence-heartbeat.xboxlive.com',
                'device.auth.xboxlive.com',
                'title.mgt.xboxlive.com',
                'xsts.auth.xboxlive.com'
            ]
            
            blocked_count = 0
            if os.path.exists(hosts_path):
                with open(hosts_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if blocking already exists
                domains_to_block = [domain for domain in xbox_domains if domain not in content]
                
                if domains_to_block:
                    with open(hosts_path, 'a', encoding='utf-8') as f:
                        f.write('\n# Midnight Spoofer - Xbox Block\n')
                        for domain in domains_to_block:
                            f.write(f'127.0.0.1 {domain}\n')
                            f.write(f'::1 {domain}\n')
                            blocked_count += 1
                            self.add_log_realtime(f"[BLOCK] Domain blocked: {domain}")
                        f.write('# End Midnight Spoofer\n')
                else:
                    self.add_log_realtime("[INFO] Xbox services already blocked")
            
            return blocked_count
        
        return self.timed_operation("Xbox Services Block", _block)
    
    def clean_system_temp(self):
        """Clean system temporary files"""
        def _clean():
            temp_paths = [
                os.environ.get('TEMP', ''),
                os.environ.get('TMP', ''),
                r'C:\Windows\Temp',
                os.path.join(os.environ['LOCALAPPDATA'], 'Temp')
            ]
            
            cleaned_count = 0
            for temp_path in temp_paths:
                if os.path.exists(temp_path):
                    for item in os.listdir(temp_path):
                        item_path = os.path.join(temp_path, item)
                        try:
                            if os.path.isfile(item_path):
                                os.remove(item_path)
                                cleaned_count += 1
                            elif os.path.isdir(item_path):
                                shutil.rmtree(item_path, ignore_errors=True)
                                cleaned_count += 1
                        except:
                            continue
            
            self.add_log_realtime(f"[CLEAN] System temporary files: {cleaned_count} items removed")
            return cleaned_count
        
        return self.timed_operation("System Temp Cleanup", _clean)
    
    def reset_network(self):
        """Reset network configurations"""
        def _reset():
            commands = [
                ('IP Release', ['ipconfig', '/release']),
                ('IP Renew', ['ipconfig', '/renew']),
                ('DNS Flush', ['ipconfig', '/flushdns']),
                ('Winsock Reset', ['netsh', 'winsock', 'reset']),
                ('IP Reset', ['netsh', 'int', 'ip', 'reset']),
                ('Firewall Reset', ['netsh', 'advfirewall', 'reset'])
            ]
            
            for name, cmd in commands:
                try:
                    subprocess.run(cmd, capture_output=True, timeout=10, shell=True)
                    self.add_log_realtime(f"[NETWORK] {name}: Executed")
                except:
                    self.add_log_realtime(f"[NETWORK] {name}: Skipped")
            
            return len(commands)
        
        return self.timed_operation("Network Stack Reset", _reset)
    
    def clean_registry_entries(self):
        """Clean specific registry entries"""
        def _clean():
            registry_operations = [
                # FiveM related
                (winreg.HKEY_CURRENT_USER, r'Software\CitizenFX'),
                (winreg.HKEY_CURRENT_USER, r'Software\FiveM'),
                
                # System traces
                (winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Explorer\FeatureUsage\AppSwitched'),
                (winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Explorer\FeatureUsage\ShowJumpView'),
                (winreg.HKEY_CURRENT_USER, r'Software\WinRAR\ArcHistory'),
                
                # Game data
                (winreg.HKEY_CURRENT_USER, r'Software\Rockstar Games'),
            ]
            
            cleaned_count = 0
            for hive, key_path in registry_operations:
                try:
                    registry_name = key_path.split('\\')[-1]
                    
                    if winreg.QueryValueEx(winreg.OpenKey(hive, key_path), "")[0]:
                        winreg.DeleteKey(winreg.OpenKey(hive, key_path, 0, winreg.KEY_ALL_ACCESS), '')
                        cleaned_count += 1
                        self.add_log_realtime(f"[REGISTRY] Key cleared: {registry_name}")
                except:
                    continue
            
            self.add_log_realtime(f"[STATUS] Registry cleanup: {cleaned_count} entries modified")
            return cleaned_count
        
        return self.timed_operation("Registry Cleanup", _clean)
    
    def execute_full_spoof(self):
        """Execute complete spoofing - single function called by the button"""
        self.log_messages.clear()
        
        start_time = time.time()
        self.add_log_realtime("=" * 60)
        self.add_log_realtime("[MIDNIGHT] SPOOFING PROTOCOL INITIATED")
        self.add_log_realtime(f"[SYSTEM] Start time: {datetime.now().strftime('%H:%M:%S')}")
        self.add_log_realtime("=" * 60)
        
        # Kill processes first
        self.add_log_realtime("[PHASE 1] Process termination sequence")
        processes = ['FiveM', 'Discord', 'Steam', 'EpicGames', 'SocialClub']
        for proc in processes:
            self.kill_process(proc)
        
        # Execute all spoofing operations
        operations = [
            ("FiveM Trace Removal", self.clean_fivem_cache),
            ("Discord Identity Spoof", self.clean_discord_rpc),
            ("System Temp Purge", self.clean_system_temp),
            ("Registry Sanitization", self.clean_registry_entries),
            ("Xbox Service Block", self.block_xbox_services),
            ("Network Stack Reset", self.reset_network)
        ]
        
        total_operations = len(operations)
        completed_operations = 0
        
        self.add_log_realtime("[PHASE 2] System modification sequence")
        
        for name, operation in operations:
            try:
                self.add_log_realtime(f"[EXECUTE] Running: {name}")
                operation()
                completed_operations += 1
                progress = (completed_operations / total_operations) * 100
                self.add_log_realtime(f"[PROGRESS] {completed_operations}/{total_operations} operations ({progress:.1f}%)")
            except Exception as e:
                self.add_log_realtime(f"[WARNING] Operation {name} failed: {str(e)}")
        
        total_time = time.time() - start_time
        self.add_log_realtime("=" * 60)
        self.add_log_realtime(f"[SYSTEM] End time: {datetime.now().strftime('%H:%M:%S')}")
        self.add_log_realtime(f"[STATISTICS] Total execution time: {total_time:.2f}s")
        self.add_log_realtime("[STATUS] SPOOFING PROTOCOL COMPLETED SUCCESSFULLY")
        self.add_log_realtime("[SECURITY] System identity has been modified")
        self.add_log_realtime("[ADVISE] All traces have been eliminated")
        self.add_log_realtime("=" * 60)
        
        return self.log_messages