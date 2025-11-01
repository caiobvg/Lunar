import os
import pathlib

def export_project_structure(root_dir, output_file):
    # Lista de extensões de arquivos de código (personalizável)
    code_extensions = {
        '.py', '.js', '.html', '.css', '.java', '.c', '.cpp', '.cs', '.php', '.rb',
        '.go', '.rs', '.ts', '.sql', '.json', '.xml', '.yaml', '.yml', '.md', '.cfg',
        '.conf', '.ini', '.sh', '.bat', '.ps1', '.vue', '.jsx',
        '.tsx', '.scss', '.sass', '.less', '.asm', '.swift', '.kt', '.dart'
    }
    
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for root, dirs, files in os.walk(root_dir):
            # Ignorar pastas de versão (personalizável)
            ignore_dirs = {'.git', '__pycache__', 'node_modules', 'vendor', 'dist', 'build'}
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            for file in files:
                file_path = pathlib.Path(root) / file
                relative_path = file_path.relative_to(root_dir)
                
                # Verificar se é um arquivo de código
                if file_path.suffix.lower() in code_extensions:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            content = infile.read()
                    except UnicodeDecodeError:
                        try:
                            with open(file_path, 'r', encoding='latin-1') as infile:
                                content = infile.read()
                        except Exception:
                            content = f"[ERRO: Não foi possível ler o arquivo {relative_path}]\n"
                    except Exception as e:
                        content = f"[ERRO: {str(e)}]\n"

                    # Escrever no arquivo de saída
                    outfile.write(f"# {relative_path}\n\n")
                    outfile.write(content)
                    outfile.write("\n\n")

if __name__ == "__main__":
    project_root = input("Digite o caminho completo do projeto (ou Enter para usar o diretório atual): ").strip()
    if not project_root:
        project_root = os.getcwd()
    
    output_filename = "projeto_completo.txt"
    export_project_structure(project_root, output_filename)
    print(f"Arquivo '{output_filename}' gerado com sucesso!")