# check_icons.py
import os
import tkinter as tk
from tkinter import messagebox

def check_icons():
    print("Verificando arquivos de icone...")

    # Lista de possíveis locais dos ícones
    possible_locations = [
        'app.ico',
        'app.png',
        os.path.join('src', 'assets', 'app.ico'),
        os.path.join('assets', 'app.ico'),
        os.path.join('src', 'assets', 'app.png'),
        os.path.join('assets', 'app.png'),
    ]

    found_icons = []
    for icon_path in possible_locations:
        if os.path.exists(icon_path):
            found_icons.append(icon_path)
            print(f"[OK] Encontrado: {icon_path}")
        else:
            print(f"[MISSING] Nao encontrado: {icon_path}")

    if not found_icons:
        print("ERRO: Nenhum arquivo de icone encontrado!")
        print("Criando icone padrao...")
        create_default_icon()
    else:
        print(f"Encontrados {len(found_icons)} arquivo(s) de icone")

    # Testar se os ícones podem ser carregados
    test_icon_loading(found_icons)

def create_default_icon():
    """Cria um ícone padrão se nenhum for encontrado"""
    try:
        from PIL import Image, ImageDraw
        # Cria uma imagem 32x32 com fundo roxo
        img = Image.new('RGB', (32, 32), color='#6b21ff')
        draw = ImageDraw.Draw(img)
        # Desenha um 'M' branco
        draw.text((8, 8), "M", fill='white')
        img.save('app.png')
        print("[SUCCESS] Icone padrao criado: app.png")
    except ImportError:
        print("[WARNING] PIL nao disponivel para criar icone padrao")

def test_icon_loading(icon_paths):
    """Testa se os ícones podem ser carregados pelo Tkinter"""
    print("\nTestando carregamento de ícones...")

    root = tk.Tk()
    root.withdraw()

    for icon_path in icon_paths:
        try:
            if icon_path.endswith('.ico'):
                root.iconbitmap(icon_path)
                print(f"[SUCCESS] Icone carregado: {icon_path}")
            elif icon_path.endswith('.png'):
                # Tenta carregar como PNG
                from PIL import Image, ImageTk
                img = Image.open(icon_path)
                photo = ImageTk.PhotoImage(img)
                root.iconphoto(True, photo)
                print(f"[SUCCESS] PNG carregado: {icon_path}")
        except Exception as e:
            print(f"[ERROR] Falha ao carregar {icon_path}: {e}")

    root.destroy()

if __name__ == "__main__":
    check_icons()
