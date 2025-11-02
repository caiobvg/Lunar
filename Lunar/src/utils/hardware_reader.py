# src/utils/hardware_reader.py

import psutil
import traceback

class HardwareReader:
    def __init__(self):
        """Inicializa o leitor de hardware."""
        # Inicializar o psutil para a CPU
        psutil.cpu_percent(interval=None)

    def get_cpu_percent(self):
        """Retorna o uso atual da CPU em %."""
        try:
            return psutil.cpu_percent(interval=None)
        except Exception:
            return 0.0

    def get_memory_percent(self):
        """Retorna o uso atual da memória em %."""
        try:
            memory = psutil.virtual_memory()
            return memory.percent
        except Exception:
            return 0.0

    def get_disk_percent(self, disk='C:'):
        """Retorna o uso do disco (padrão C:) em %."""
        try:
            disk_usage = psutil.disk_usage(disk)
            return disk_usage.percent
        except Exception:
            # Tenta encontrar outra partição se C: falhar
            try:
                partitions = psutil.disk_partitions()
                if partitions:
                    disk_usage = psutil.disk_usage(partitions[0].mountpoint)
                    return disk_usage.percent
            except Exception:
                return 0.0
        return 0.0
