# src/controllers/spoofer_controller.py

import threading
from datetime import datetime
from utils.logger import logger

class SpoofingController:
    def __init__(self, cleaner, mac_spoofer, hw_reader, ui_callbacks):
        self.cleaner = cleaner
        self.mac_spoofer = mac_spoofer
        self.hw_reader = hw_reader
        self.ui_callbacks = ui_callbacks
        self.last_spoof_time = None

    def start_spoofing_thread(self, toggle_states, selected_interface, selected_vendor, selected_mac):
        """Inicia a sequência de spoofing em uma nova thread."""
        thread = threading.Thread(
            target=self.execute_spoofing,
            args=(toggle_states, selected_interface, selected_vendor, selected_mac),
            daemon=True
        )
        thread.start()

    def execute_spoofing(self, toggle_states, selected_interface, selected_vendor, selected_mac):
        """Executa a lógica de spoofing, chamando os callbacks da UI para atualizações."""
        try:
            logger.log_info("🚀 INITIATING SPOOFING PROTOCOL", "SPOOFING")
            logger.log_info("This will modify system files", "SPOOFING")
            logger.log_info("=" * 50, "SPOOFING")
            
            # Notifica a UI que o processo começou
            if 'on_start' in self.ui_callbacks:
                self.ui_callbacks['on_start']()

            # Mostra valores ANTES do spoof
            if self.hw_reader:
                logger.log_info("Current Hardware IDs (BEFORE):", "HARDWARE")
                try:
                    hw_before = self.hw_reader.get_all_hardware_ids()
                    for key, value in hw_before.items():
                        display_value = value if len(str(value)) <= 40 else str(value)[:37] + "..."
                        logger.log_info(f"{key}: {display_value}", "HARDWARE")
                except Exception as e:
                    logger.log_warning(f"Could not read hardware before spoof: {str(e)}", "HARDWARE")

            # Executa operações de limpeza
            logger.log_info("Executing cleaner operations...", "SPOOFING")
            cleaner_success = self.cleaner.execute_real_spoofing()

            # Executa spoofing de MAC se habilitado
            if toggle_states.get("NEW MAC") and self.mac_spoofer and selected_interface:
                logger.log_info("Executing MAC spoofing...", "MAC")
                try:
                    mac_success = self.mac_spoofer.spoof_mac_address(selected_interface, selected_vendor, selected_mac)
                    if mac_success:
                        logger.log_success("MAC address spoofed successfully", "MAC")
                    else:
                        logger.log_error("MAC spoofing failed", "MAC")
                except Exception as e:
                    logger.log_error(f"MAC spoofing error: {e}", "MAC")
            
            if cleaner_success:
                self.last_spoof_time = datetime.now()
                
                # Notifica a UI sobre o sucesso
                if 'on_success' in self.ui_callbacks:
                    self.ui_callbacks['on_success']()
                
                logger.log_success("✅ SPOOFING COMPLETED!", "SUCCESS")
                logger.log_success("System modifications applied", "SECURITY")
            else:
                # Notifica a UI sobre a falha parcial
                if 'on_failure' in self.ui_callbacks:
                    self.ui_callbacks['on_failure']("Some operations failed")
                logger.log_warning("⚠️ Some spoofing operations may have failed", "WARNING")
            
        except Exception as e:
            logger.log_error(f"Spoofing failed completely: {str(e)}", "CRITICAL")
            # Notifica a UI sobre a falha crítica
            if 'on_failure' in self.ui_callbacks:
                self.ui_callbacks['on_failure']("Critical failure")
        finally:
            # Notifica a UI que o processo terminou
            if 'on_finish' in self.ui_callbacks:
                self.ui_callbacks['on_finish']()
