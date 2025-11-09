"""
PONTO DE ENTRADA PRINCIPAL - Lunar Spoofer
"""
import sys
import os
import ctypes
import traceback

def check_admin_privileges():
    """Verifica se está executando como administrador"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def setup_environment():
    """Configura o ambiente Python"""
    # Adicionar src ao path
    src_path = os.path.join(os.path.dirname(__file__), 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

def main():
    """Função principal"""
    print("Inicializando Lunar Spoofer...")

    # Configurar ambiente
    setup_environment()

    # Verificar privilégios
    if not check_admin_privileges():
        print("ERRO: Execute como Administrador!")
        input("Pressione Enter para sair...")
        return 1

    try:
        from src.core.app import LunarApp

        # Criar e executar aplicação
        app = LunarApp()
        return app.run()

    except Exception as e:
        print(f"Erro fatal na inicialização: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        input("Pressione Enter para sair...")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
