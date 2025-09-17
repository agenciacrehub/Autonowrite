#!/usr/bin/env python3
"""
Script para testar o construtor de inputs estruturados.
"""
import sys
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.append(str(Path(__file__).parent))

from src.input_builder import InputBuilder

def main():
    """Função principal para testar o construtor de inputs."""
    try:
        # Cria uma solicitação de conteúdo
        content_request = InputBuilder.build_content_request()
        
        # Exibe o resultado
        print("\n=== SOLICITAÇÃO DE CONTEÚDO CRIADA COM SUCESSO ===")
        print(f"Domínio: {content_request.context.knowledge_domain}")
        print(f"Público: {content_request.context.target_audience}")
        print(f"Propósito: {content_request.objectives.main_purpose}")
        print(f"Fontes: {len(content_request.sources.preferred_sources)} fontes especificadas")
        
        # Pergunta se deseja salvar
        save = input("\nDeseja salvar esta solicitação? (s/n): ").strip().lower()
        if save == 's':
            filename = input("Nome do arquivo (opcional): ").strip()
            if not filename:
                from datetime import datetime
                filename = f"content_request_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # Cria diretório de saída se não existir
            output_dir = Path("requests")
            output_dir.mkdir(exist_ok=True)
            
            # Salva o arquivo
            filepath = output_dir / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                import json
                json.dump(content_request.to_dict(), f, indent=2, ensure_ascii=False)
            
            print(f"\nSolicitação salva em: {filepath}")
        
    except Exception as e:
        print(f"\nErro ao criar solicitação: {e}", file=sys.stderr)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
