"""
Módulo para geração de conteúdo a partir de solicitações estruturadas.
"""
import json
import sys
import os
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

# Adiciona o diretório src ao path para importações
sys.path.append(os.path.join(os.path.dirname(__file__)))

# Agora importa sem usar importação relativa
from structured_inputs import ContentRequest

class ContentGenerator:
    """Gerencia a geração de conteúdo a partir de solicitações."""
    
    def __init__(self, system):
        self.system = system
        
    def load_request(self, filepath: str) -> ContentRequest:
        """Carrega uma solicitação de um arquivo JSON."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return ContentRequest.from_dict(data)
    
    def generate_content(self, request: ContentRequest) -> Dict[str, Any]:
        """Gera conteúdo a partir da solicitação."""
        topic = f"{request.context.knowledge_domain} - {request.objectives.main_purpose}"
        
        # Gera o conteúdo
        result = self.system.generate_content(
            topic=topic,
            max_iterations=3
        )
        
        # Verifica se o resultado é um dicionário ou objeto
        if hasattr(result, 'final_content'):
            # Se for um objeto com atributos
            return {
                "topic": topic,
                "content": result.final_content,
                "score": getattr(result, 'final_score', 0.0),
                "iterations": getattr(result, 'iterations_used', 0),
                "timestamp": datetime.now().isoformat()
            }
        elif isinstance(result, dict):
            # Se for um dicionário
            return {
                "topic": topic,
                "content": result.get('final_content', ''),
                "score": result.get('final_score', 0.0),
                "iterations": result.get('iterations_used', 0),
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Se for outro tipo de dado
            return {
                "topic": topic,
                "content": str(result),
                "score": 0.0,
                "iterations": 0,
                "timestamp": datetime.now().isoformat()
            }

def run_generator():
    """Executa o gerador de conteúdo."""
    # Adiciona o diretório raiz ao path
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    
    from main import AutonoWriteSystem, LLMProvider
    
    # Inicializa o sistema
    provider_env = os.getenv("LLM_PROVIDER", "auto").strip().lower()
    chosen = provider_env if provider_env in {"groq", "ollama", "simulation", "auto"} else "auto"
    llm_provider = LLMProvider(provider_type=chosen)
    system = AutonoWriteSystem(llm_provider=llm_provider)
    generator = ContentGenerator(system)
    
    # Lista arquivos JSON disponíveis
    requests_dir = Path("requests")
    if requests_dir.exists():
        json_files = list(requests_dir.glob("*.json"))
        if json_files:
            print("\nArquivos JSON disponíveis:")
            for i, file in enumerate(json_files, 1):
                print(f"{i}. {file.name}")
            
            try:
                choice = int(input("\nEscolha o número do arquivo: ")) - 1
                filepath = json_files[choice]
            except (ValueError, IndexError):
                print("Opção inválida!")
                return
        else:
            print("Nenhum arquivo JSON encontrado na pasta 'requests'")
            return
    else:
        filepath = input("\nCaminho do arquivo JSON: ").strip()
    
    try:
        # Carrega e exibe a solicitação
        request = generator.load_request(str(filepath))
        print(f"\nTópico: {request.context.knowledge_domain}")
        print(f"Público: {request.context.target_audience}")
        print(f"Objetivo: {request.objectives.main_purpose}")
        
        # Confirmação
        if input("\nGerar conteúdo? (s/n): ").lower() != 's':
            return
            
        # Gera e salva o conteúdo
        print("\nGerando conteúdo...")
        result = generator.generate_content(request)
        
        # Salva o resultado
        output_dir = Path("generated_content")
        output_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"content_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
            
        print(f"\nConteúdo gerado com sucesso!")
        print(f"Score: {result['score']}")
        print(f"Iterações: {result['iterations']}")
        print(f"Arquivo salvo em: {output_file}")
        
        # Exibe uma prévia do conteúdo
        preview = result['content'][:200] + "..." if len(result['content']) > 200 else result['content']
        print(f"\nPrévia do conteúdo:\n{preview}")
        
    except FileNotFoundError:
        print(f"Arquivo não encontrado: {filepath}")
    except Exception as e:
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_generator()