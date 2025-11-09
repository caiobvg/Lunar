import json
import os
from pathlib import Path

class Config:
    def __init__(self):
        self.config_path = Path("config.json")
        self.default_config = {
            "theme": "purple",
            "window_size": [1400, 900],
            "auto_start": False,
            "admin_required": True,
            "log_level": "INFO"
        }
        self.config = self.load_config()

    def load_config(self):
        """Carrega configuração do arquivo ou cria padrão"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return {**self.default_config, **json.load(f)}
            except Exception as e:
                print(f"Erro ao carregar config: {e}")
                return self.default_config
        else:
            self.save_config(self.default_config)
            return self.default_config

    def save_config(self, config=None):
        """Salva configuração no arquivo"""
        if config is None:
            config = self.config

        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erro ao salvar config: {e}")
            return False

    def get(self, key, default=None):
        """Obtém valor da configuração"""
        return self.config.get(key, default)

    def set(self, key, value):
        """Define valor da configuração"""
        self.config[key] = value
        return self.save_config()
