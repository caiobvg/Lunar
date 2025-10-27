import psutil

class SystemStats:
    @staticmethod
    def get_cpu_usage():
        return psutil.cpu_percent(interval=0.1)
    
    @staticmethod
    def get_memory_usage():
        memory = psutil.virtual_memory()
        return memory.percent
    
    @staticmethod
    def get_disk_usage():
        disk = psutil.disk_usage('/')
        return disk.percent