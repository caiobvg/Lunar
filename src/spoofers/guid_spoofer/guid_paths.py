"""
GUID-specific registry paths and system locations
"""
import os

GUID_REGISTRY_PATHS = {
    'windows_system': [
        {
            'hive': 'HKLM',
            'path': r"SOFTWARE\Microsoft\Cryptography",
            'name': 'MachineGuid',
            'description': 'Windows Machine GUID',
            'backup': True,
            'critical': True
        },
        {
            'hive': 'HKLM',
            'path': r"SOFTWARE\Microsoft\SQMClient",
            'name': 'MachineId',
            'description': 'Windows SQM Client Machine ID',
            'backup': True,
            'critical': False
        },
        {
            'hive': 'HKLM',
            'path': r"SOFTWARE\Microsoft\Windows NT\CurrentVersion",
            'name': 'ProductId',
            'description': 'Windows Product ID',
            'backup': True,
            'critical': False
        },
        {
            'hive': 'HKLM',
            'path': r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileGuid",
            'name': 'ProfileGuid',
            'description': 'Windows Profile GUID',
            'backup': True,
            'critical': False
        }
    ],
    'rockstar_games': [
        {
            'hive': 'HKLM',
            'path': r"SOFTWARE\WOW6432Node\Rockstar Games\Grand Theft Auto V",
            'name': 'MachineGUID',
            'description': 'Rockstar GTA V Machine GUID',
            'backup': True,
            'critical': False
        },
        {
            'hive': 'HKLM',
            'path': r"SOFTWARE\Rockstar Games",
            'name': 'MachineGUID',
            'description': 'Rockstar Games Machine GUID',
            'backup': True,
            'critical': False
        },
        {
            'hive': 'HKLM',
            'path': r"SOFTWARE\Rockstar Games\Launcher",
            'name': 'GUID',
            'description': 'Rockstar Launcher GUID',
            'backup': True,
            'critical': False
        },
        {
            'hive': 'HKLM',
            'path': r"SOFTWARE\Rockstar Games\Social Club",
            'name': 'MachineGUID',
            'description': 'Rockstar Social Club Machine GUID',
            'backup': True,
            'critical': False
        },
        {
            'hive': 'HKCU',
            'path': r"SOFTWARE\Rockstar Games\Social Club",
            'name': 'GUID',
            'description': 'Rockstar Social Club User GUID',
            'backup': True,
            'critical': False
        }
    ],
    'fivem': [
        {
            'hive': 'HKCU',
            'path': r"Software\Cfx.re",
            'name': 'guid',
            'description': 'FiveM Cfx.re GUID',
            'backup': True,
            'critical': True
        },
        {
            'hive': 'HKCU',
            'path': r"Software\CitizenFX",
            'name': 'guid',
            'description': 'FiveM CitizenFX GUID',
            'backup': True,
            'critical': True
        }
    ],
    'steam_tweaks': [
        {
            'hive': 'HKCU',
            'path': r"Software\Valve\Steam",
            'name': 'ActiveProcess',
            'description': 'Steam Active Process Flag',
            'backup': True,
            'critical': False
        }
    ]
}

GUID_SYSTEM_PATHS = {
    'cache_locations': [
        os.path.join(os.getenv('LOCALAPPDATA', ''), 'FiveM'),
        os.path.join(os.getenv('APPDATA', ''), 'CitizenFX'),
        os.path.join(os.getenv('LOCALAPPDATA', ''), 'Rockstar Games'),
        os.path.join(os.getenv('DOCUMENTS', ''), 'Rockstar Games'),
        os.path.join(os.getenv('PROGRAMDATA', ''), 'Rockstar Games'),
        os.path.join(os.getenv('APPDATA', ''), 'Social Club'),
        os.path.join(os.getenv('LOCALAPPDATA', ''), 'Steam'),
    ],
    'registry_backups': [
        "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Cryptography",
        "HKEY_LOCAL_MACHINE\\SOFTWARE\\Rockstar Games",
        "HKEY_LOCAL_MACHINE\\SOFTWARE\\WOW6432Node\\Rockstar Games",
        "HKEY_CURRENT_USER\\Software\\Cfx.re",
        "HKEY_CURRENT_USER\\Software\\CitizenFX",
        "HKEY_LOCAL_MACHINE\\SOFTWARE\\CitizenFX"
    ]
}
