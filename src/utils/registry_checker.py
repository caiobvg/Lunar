"""Centralized registry access helper for MidnightSpoofer.

Provides safe read/write/delete/enumeration helpers, dry-run mode,
backup/restore and transactional writes with rollback.
"""
# src/utils/registry_checker.py

from __future__ import annotations

import json
import os
import threading
import time
import hashlib
import getpass
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple

import winreg

from utils.logger import logger


class RegistryError(Exception):
    pass


class RegistryChecker:
    def __init__(self, backup_dir: Optional[str] = None):
        self.lock = threading.RLock()
        self.dry_run = False
        self.backup_dir = backup_dir or os.path.join(os.getcwd(), "registry_backups")
        os.makedirs(self.backup_dir, exist_ok=True)

    # ----------------------- Utilities -----------------------
    def _hive_from_string(self, hive: str):
        mapping = {
            "HKEY_LOCAL_MACHINE": winreg.HKEY_LOCAL_MACHINE,
            "HKLM": winreg.HKEY_LOCAL_MACHINE,
            "HKEY_CURRENT_USER": winreg.HKEY_CURRENT_USER,
            "HKCU": winreg.HKEY_CURRENT_USER,
            "HKEY_USERS": winreg.HKEY_USERS,
            "HKEY_CLASSES_ROOT": winreg.HKEY_CLASSES_ROOT,
        }
        try:
            return mapping[hive]
        except KeyError:
            raise RegistryError(f"Unknown hive: {hive}")

    def _backup_path(self, name: Optional[str] = None) -> str:
        ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        name = name or f"backup_{ts}.json"
        return os.path.join(self.backup_dir, name)

    def _hash_payload(self, payload: bytes) -> str:
        return hashlib.sha256(payload).hexdigest()

    # ----------------------- Modes -----------------------
    def set_dry_run(self, enabled: bool):
        self.dry_run = bool(enabled)
        logger.log_info(f"RegistryChecker dry-run set to {self.dry_run}", "RegistryChecker")

    def ensure_admin_or_raise(self):
        try:
            # Try to open a protected key for write to test permissions
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE", 0, winreg.KEY_WRITE):
                return True
        except Exception:
            raise RegistryError("Administrator privileges required to perform this operation")

    # ----------------------- Read / List -----------------------
    def read_value(self, hive: str, path: str, name: str) -> Tuple[Any, int]:
        hive_const = self._hive_from_string(hive)
        try:
            with winreg.OpenKey(hive_const, path, 0, winreg.KEY_READ) as key:
                value, vtype = winreg.QueryValueEx(key, name)
                logger.log_info(f"Read registry {hive}\\{path} :: {name} = {self._truncate_value(value)}", "RegistryChecker")
                return value, vtype
        except FileNotFoundError:
            raise RegistryError(f"Key or value not found: {hive}\\{path} -> {name}")
        except Exception as e:
            raise RegistryError(str(e))

    def list_values(self, hive: str, path: str) -> Dict[str, Tuple[Any, int]]:
        hive_const = self._hive_from_string(hive)
        results: Dict[str, Tuple[Any, int]] = {}
        try:
            with winreg.OpenKey(hive_const, path, 0, winreg.KEY_READ) as key:
                i = 0
                while True:
                    try:
                        name, value, vtype = winreg.EnumValue(key, i)
                        results[name] = (value, vtype)
                        i += 1
                    except OSError:
                        break
            logger.log_info(f"Listed {len(results)} values at {hive}\\{path}", "RegistryChecker")
            return results
        except FileNotFoundError:
            raise RegistryError(f"Key not found: {hive}\\{path}")
        except Exception as e:
            raise RegistryError(str(e))

    def enumerate_subkeys(self, hive: str, path: str) -> List[str]:
        hive_const = self._hive_from_string(hive)
        subs: List[str] = []
        try:
            with winreg.OpenKey(hive_const, path, 0, winreg.KEY_READ) as key:
                i = 0
                while True:
                    try:
                        sub = winreg.EnumKey(key, i)
                        subs.append(sub)
                        i += 1
                    except OSError:
                        break
            logger.log_info(f"Enumerated {len(subs)} subkeys at {hive}\\{path}", "RegistryChecker")
            return subs
        except FileNotFoundError:
            raise RegistryError(f"Key not found: {hive}\\{path}")
        except Exception as e:
            raise RegistryError(str(e))

    def find_subkey_by_value(self, hive: str, base_path: str, value_name: str, match_fn: Callable[[Any], bool]) -> Optional[str]:
        subs = self.enumerate_subkeys(hive, base_path)
        for sub in subs:
            try:
                val, _ = self.read_value(hive, os.path.join(base_path, sub), value_name)
                if match_fn(val):
                    return sub
            except RegistryError:
                continue
        return None

    # ----------------------- Write / Delete -----------------------
    def write_value(self, hive: str, path: str, name: str, value: Any, value_type: int = winreg.REG_SZ, backup: bool = True) -> bool:
        hive_const = self._hive_from_string(hive)
        full_path = f"{hive}\\{path}\\{name}"
        with self.lock:
            if self.dry_run:
                logger.log_info(f"[DRY-RUN] Write {full_path} = {self._truncate_value(value)}", "RegistryChecker")
                return True

            if backup:
                try:
                    self._save_backup_for_key(hive, path, [name])
                except Exception as e:
                    logger.log_warning(f"Failed to backup before write: {e}", "RegistryChecker")

            try:
                # ensure key exists (create if necessary)
                key = winreg.CreateKeyEx(hive_const, path, 0, winreg.KEY_WRITE)
                with key:
                    winreg.SetValueEx(key, name, 0, value_type, value)
                logger.log_info(f"Wrote registry {full_path}", "RegistryChecker")
                return True
            except Exception as e:
                raise RegistryError(str(e))

    def delete_value(self, hive: str, path: str, name: str, backup: bool = True) -> bool:
        hive_const = self._hive_from_string(hive)
        full_path = f"{hive}\\{path}\\{name}"
        with self.lock:
            if self.dry_run:
                logger.log_info(f"[DRY-RUN] Delete {full_path}", "RegistryChecker")
                return True

            if backup:
                try:
                    self._save_backup_for_key(hive, path, [name])
                except Exception as e:
                    logger.log_warning(f"Failed to backup before delete: {e}", "RegistryChecker")

            try:
                with winreg.OpenKey(hive_const, path, 0, winreg.KEY_SET_VALUE) as key:
                    winreg.DeleteValue(key, name)
                logger.log_info(f"Deleted registry value {full_path}", "RegistryChecker")
                return True
            except FileNotFoundError:
                raise RegistryError(f"Value not found: {full_path}")
            except Exception as e:
                raise RegistryError(str(e))

    # ----------------------- Transactional -----------------------
    def transactional_write(self, ops: List[Dict]) -> bool:
        """ops: list of {action: 'write'|'delete', hive, path, name, value?, value_type?}

        Rolls back all changes if any operation fails.
        """
        with self.lock:
            # Build backup for all affected keys
            backup_items: List[Tuple[str, str, List[str]]] = []  # (hive, path, [names])
            for op in ops:
                backup_items.append((op["hive"], op["path"], [op["name"]]))

            backup_file = self._save_backup_for_items(backup_items)

            # Apply operations
            try:
                for op in ops:
                    action = op.get("action")
                    if action == "write":
                        self.write_value(op["hive"], op["path"], op["name"], op.get("value"), op.get("value_type", winreg.REG_SZ), backup=False)
                    elif action == "delete":
                        self.delete_value(op["hive"], op["path"], op["name"], backup=False)
                    else:
                        raise RegistryError(f"Unknown op action: {action}")
                logger.log_info(f"Transactional write succeeded; backup: {backup_file}", "RegistryChecker")
                return True
            except Exception as e:
                logger.log_error(f"Transactional write failed: {e}; rolling back", "RegistryChecker")
                try:
                    self.restore(backup_file)
                except Exception as re:
                    logger.log_error(f"Rollback failed: {re}", "RegistryChecker")
                raise

    # ----------------------- Backup / Restore -----------------------
    def _save_backup_for_items(self, items: List[Tuple[str, str, List[str]]]) -> str:
        # items: list of (hive, path, [names])
        payload = {"meta": {"created_by": getpass.getuser(), "ts": time.time()}, "data": {}}
        for hive, path, names in items:
            try:
                values = self.list_values(hive, path)
            except RegistryError:
                values = {}
            # filter only requested names
            filtered = {k: v for k, v in values.items() if k in names}
            payload["data"][f"{hive}\\{path}"] = filtered

        raw = json.dumps(payload, default=str).encode("utf-8")
        fname = self._backup_path()
        with open(fname, "wb") as f:
            f.write(raw)

        sig = self._hash_payload(raw)
        metafname = fname + ".sig"
        with open(metafname, "w") as f:
            f.write(sig)

        logger.log_info(f"Saved registry backup: {fname}", "RegistryChecker")
        return fname

    def _save_backup_for_key(self, hive: str, path: str, names: List[str]) -> str:
        return self._save_backup_for_items([(hive, path, names)])

    def restore(self, backup_file: str) -> bool:
        if not os.path.exists(backup_file):
            raise RegistryError("Backup file not found")
        with open(backup_file, "rb") as f:
            raw = f.read()
        # Optional: verify signature
        sigfile = backup_file + ".sig"
        if os.path.exists(sigfile):
            with open(sigfile, "r") as f:
                sig = f.read().strip()
            if sig != self._hash_payload(raw):
                logger.log_warning("Backup signature mismatch", "RegistryChecker")

        payload = json.loads(raw.decode("utf-8"))
        data = payload.get("data", {})

        # Apply values
        for keypath, values in data.items():
            try:
                hive_str, reg_path = keypath.split("\\", 1)
            except ValueError:
                continue
            for name, (value, vtype) in values.items():
                try:
                    self.write_value(hive_str, reg_path, name, value, value_type=vtype, backup=False)
                except Exception as e:
                    logger.log_error(f"Failed to restore {keypath}::{name} -> {e}", "RegistryChecker")
        logger.log_info(f"Restored registry from {backup_file}", "RegistryChecker")
        return True

    # ----------------------- Helpers -----------------------
    def _truncate_value(self, value: Any, max_length: int = 50) -> str:
        try:
            s = str(value)
            if len(s) > max_length:
                return s[:max_length] + "..."
            return s
        except Exception:
            return "<unserializable>"

    # Backwards compat / reporting helpers
    def get_spoofing_readiness_report(self) -> Dict[str, Any]:
        report = {"ok": True, "checked_at": datetime.utcnow().isoformat()}
        return report