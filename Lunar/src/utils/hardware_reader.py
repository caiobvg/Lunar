# src/utils/hardware_reader.py

import psutil
import traceback
import time # NEW IMPORT

class HardwareReader:
    def __init__(self):
        """Inicializa o leitor de hardware."""
        # Inicializar o psutil para a CPU
        psutil.cpu_percent(interval=None)

        # NEW: Inicializar contadores de Disco
        # Pegar os contadores totais (sem ser por partição)
        self.last_disk_io = psutil.disk_io_counters(perdisk=False)
        self.last_disk_time = time.time()

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

    def get_disk_mbs(self): # CHANGED: Name and logic
        """Retorna a atividade de R/W do disco em MB/s."""
        try:
            current_disk_io = psutil.disk_io_counters(perdisk=False)
            current_disk_time = time.time()

            # Delta de tempo (em segundos)
            time_delta = current_disk_time - self.last_disk_time
            if time_delta == 0:
                # Evita divisão por zero se chamado rápido demais
                return 0.0

            # Calcular bytes lidos/escritos no intervalo
            read_delta = current_disk_io.read_bytes - self.last_disk_io.read_bytes
            write_delta = current_disk_io.write_bytes - self.last_disk_io.write_bytes
            total_bytes_delta = read_delta + write_delta

            # Calcular MB/s
            bytes_per_second = total_bytes_delta / time_delta
            mb_per_second = bytes_per_second / (1024 * 1024) # 1 MB = 1024*1024 Bytes

            # Atualizar "last" para o próximo cálculo
            self.last_disk_io = current_disk_io
            self.last_disk_time = current_disk_time

            return mb_per_second

        except Exception as e:
            print(f"Erro ao ler atividade do disco (MB/s): {e}")
            return 0.0
