"""
System cleaning paths and configurations
"""
import os

PROCESSES_TO_KILL = [
    'discord', 'fivem', 'steam', 'steamwebhelper',
    'epicgameslauncher', 'socialclub', 'rockstargames'
]

FIVEM_PATHS = [
    os.path.join(os.environ['LOCALAPPDATA'], 'FiveM', 'FiveM.app', 'cache'),
    os.path.join(os.environ['LOCALAPPDATA'], 'FiveM', 'FiveM.app', 'logs'),
    os.path.join(os.environ['LOCALAPPDATA'], 'FiveM', 'FiveM.app', 'crashes'),
    os.path.join(os.environ['LOCALAPPDATA'], 'DigitalEntitlements'),
    os.path.join(os.environ['APPDATA'], 'CitizenFX'),
    os.path.join(os.environ['LOCALAPPDATA'], 'FiveM', 'FiveM.app', 'data', 'cache'),
    os.path.join(os.environ['LOCALAPPDATA'], 'FiveM', 'FiveM.app', 'browser'),
    os.path.join(os.environ['USERPROFILE'], 'AppData', 'Roaming', 'CitizenFX'),
    os.path.join(os.environ['USERPROFILE'], 'Documents', 'Rockstar Games'),
]

SYSTEM_TEMP_PATHS = [
    os.environ.get('TEMP', ''),
    os.environ.get('TMP', ''),
    os.path.join(os.environ['LOCALAPPDATA'], 'Temp'),
    r'C:\Windows\Temp',
    os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Temp'),
]

BROWSER_CACHE_PATHS = [
    os.path.join(os.environ['LOCALAPPDATA'], 'Google', 'Chrome', 'User Data', 'Default', 'Cache'),
    os.path.join(os.environ['LOCALAPPDATA'], 'Microsoft', 'Edge', 'User Data', 'Default', 'Cache'),
    os.path.join(os.environ['APPDATA'], 'Mozilla', 'Firefox', 'Profiles'),
]

REGISTRY_CLEANING_PATHS = [
    (r'Software\CitizenFX', 'HKEY_CURRENT_USER'),
    (r'Software\FiveM', 'HKEY_CURRENT_USER'),
    (r'Software\Rockstar Games', 'HKEY_CURRENT_USER'),
    (r'Software\Valve\Steam', 'HKEY_CURRENT_USER'),
    (r'Software\Rockstar Games Launcher', 'HKEY_CURRENT_USER'),
    (r'Software\Epic Games', 'HKEY_CURRENT_USER'),
]

DISCORD_PATHS = [
    os.path.join(os.environ['APPDATA'], 'discord'),
    os.path.join(os.environ['LOCALAPPDATA'], 'Discord'),
    os.path.join(os.environ['LOCALAPPDATA'], 'DiscordCanary'),
    os.path.join(os.environ['LOCALAPPDATA'], 'DiscordPTB'),
]

DISCORD_CACHE_PATHS = [
    os.path.join(os.environ['LOCALAPPDATA'], 'Discord', 'Cache'),
    os.path.join(os.environ['LOCALAPPDATA'], 'DiscordCanary', 'Cache'),
    os.path.join(os.environ['LOCALAPPDATA'], 'DiscordPTB', 'Cache'),
    os.path.join(os.environ['LOCALAPPDATA'], 'Discord', 'Code Cache'),
    os.path.join(os.environ['LOCALAPPDATA'], 'Discord', 'GPUCache'),
]

DISCORD_STORAGE_PATHS = [
    os.path.join(os.environ['LOCALAPPDATA'], 'Discord', 'Local Storage'),
    os.path.join(os.environ['LOCALAPPDATA'], 'DiscordCanary', 'Local Storage'),
    os.path.join(os.environ['LOCALAPPDATA'], 'DiscordPTB', 'Local Storage'),
]
