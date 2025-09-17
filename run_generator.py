#!/usr/bin/env python3
"""
Script para executar o gerador de conteúdo a partir do diretório raiz.
"""
import sys
from pathlib import Path

# Adiciona o diretório atual ao path para imports
sys.path.append(str(Path(__file__).parent))

def main():
    """Função principal para executar o gerador."""
    try:
        from src.content_generator import run_generator
        
        print("=== GERADOR DE CONTEÚDO AUTOMATIZADO ===")
        print("Este script gera conteúdo a partir de uma solicitação salva em JSON.\n")
        
        # Lista solicitações salvas
        requests_dir = Path("requests")
        if requests_dir.exists() and any(requests_dir.iterdir()):
            print("Solicitações encontradas:")
            for i, file in enumerate(requests_dir.glob("*.json"), 1):
                print(f"{i}. {file.name}")
            
            file_num = input("\nNúmero do arquivo (ou pressione Enter para digitar o caminho): ").strip()
            if file_num.isdigit():
                files = list(requests_dir.glob("*.json"))
                if 1 <= int(file_num) <= len(files):
                    filepath = str(files[int(file_num)-1])
                else:
                    print("Número inválido.")
                    return
            else:
                filepath = input("Caminho completo do arquivo: ").strip()
        else:
            filepath = input("Caminho do arquivo JSON: ").strip()
        
        # Executa o gerador
        print(f"\nProcessando: {filepath}")
        run_generator()
        
    except Exception as e:
        print(f"\nErro ao executar o gerador: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
