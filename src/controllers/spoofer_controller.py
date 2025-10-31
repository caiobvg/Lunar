# src/controllers/spoofer_controller.py

import threading
from datetime import datetime
import psutil
from utils.logger import logger

class SpoofingController:
    def __init__(self, cleaner, mac_spoofer, hwid_spoofer, guid_spoofer, hw_reader):
        self.cleaner = cleaner
        self.mac_spoofer = mac_spoofer
        self.hwid_spoofer = hwid_spoofer
        self.guid_spoofer = guid_spoofer
        self.hw_reader = hw_reader
        self.ui_callbacks = {}  # Will be set by the GUI
        self.last_spoof_time = None

    def set_ui_callbacks(self, callbacks):
        """Allows the GUI to register its callbacks with the controller."""
        self.ui_callbacks = callbacks

    def check_discord_process(self):
        """Verifica e encerra processos do Discord corretamente"""
        discord_processes = ["discord.exe", "discordptb.exe", "discordcanary.exe"]
        processes_found = []

        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] and proc.info['name'].lower() in discord_processes:
                    processes_found.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if processes_found:
            logger.log_info(f"Found {len(processes_found)} Discord process(es), terminating...", "DISCORD")
            for process in processes_found:
                try:
                    process.terminate()
                    process.wait(timeout=5)  # Wait for process to terminate
                    logger.log_success(f"Terminated: {process.name()}", "DISCORD")
                except Exception as e:
                    logger.log_warning(f"Failed to terminate {process.name()}: {str(e)}", "DISCORD")
            return True
        else:
            logger.log_info("Discord is not running (this is OK)", "DISCORD")
            return True  # ← MUDANÇA CRÍTICA: Retorna True mesmo quando não encontrado

    def start_spoofing_thread(self, toggle_states, selected_interface, selected_vendor, selected_mac):
        """Inicia a sequência de spoofing em uma nova thread."""
        thread = threading.Thread(
            target=self.execute_spoofing,
            args=(toggle_states, selected_interface, selected_vendor, selected_mac),
            daemon=True
        )
        thread.start()

    def execute_spoofing(self, toggle_states, selected_interface, selected_vendor, selected_mac):
        """Executa a lógica de spoofing CORRIGIDA"""
        try:
            logger.log_info("🚀 INICIANDO SPOOFING COMPLETO", "SPOOFING")

            # 1. Primeiro executar limpeza
            cleaner_success = self.cleaner.execute_real_spoofing()

            # 2. Executar MAC spoofing SE habilitado
            mac_success = False
            if toggle_states.get("MAC SPOOFING") and self.mac_spoofer and selected_interface:
                logger.log_info("Executando MAC spoofing...", "MAC")
                mac_success = self.mac_spoofer.spoof_mac_address(
                    selected_interface,
                    selected_vendor,
                    selected_mac
                )

            # 3. Executar GUID spoofing SE habilitado
            guid_success = False
            if toggle_states.get("GUID SPOOFING") and self.guid_spoofer:
                logger.log_info("Executando GUID spoofing...", "GUID")
                guid_success = self.guid_spoofer.spoof_guid()

            # 4. Executar HWID spoofing SE habilitado
            hwid_success = False
            if toggle_states.get("HWID SPOOFER") and self.hwid_spoofer:
                logger.log_info("Executando HWID spoofing...", "HWID")
                hwid_success = self.hwid_spoofer.spoof_hwid()

            # Verificar resultados
            success_count = sum([cleaner_success, mac_success, guid_success, hwid_success])
            total_operations = sum([1,  # cleaner sempre executa
                                  int(toggle_states.get("MAC SPOOFING", False)),
                                  int(toggle_states.get("GUID SPOOFING", False)),
                                  int(toggle_states.get("HWID SPOOFER", False))])

            if success_count >= total_operations * 0.7:  # 70% de sucesso
                self.last_spoof_time = datetime.now()
                if 'on_success' in self.ui_callbacks:
                    self.ui_callbacks['on_success']()
                logger.log_success(f"✅ SPOOFING COMPLETO: {success_count}/{total_operations} operações", "SUCCESS")
                return True
            else:
                if 'on_failure' in self.ui_callbacks:
                    self.ui_callbacks['on_failure'](f"Apenas {success_count}/{total_operations} operações")
                logger.log_warning(f"⚠️ SPOOFING PARCIAL: {success_count}/{total_operations} operações", "WARNING")
                return False

        except Exception as e:
            logger.log_error(f"❌ SPOOFING FALHOU: {str(e)}", "CRITICAL")
            if 'on_failure' in self.ui_callbacks:
                self.ui_callbacks['on_failure']("Falha crítica")
            return False
