#!/usr/bin/env python3
"""
Correção automática para problema de memória no AutonoWrite
"""

import os
import subprocess
import sys
from typing import Optional

def check_system_memory():
    """Verifica memória disponível do sistema"""
    try:
        if os.name == 'posix':  # Linux/Mac
            result = subprocess.run(['free', '-h'], capture_output=True, text=True)
            print("Memória do sistema:")
            print(result.stdout)
        elif os.name == 'nt':  # Windows
            result = subprocess.run(['wmic', 'computersystem', 'get', 'TotalPhysicalMemory'], 
                                  capture_output=True, text=True)
            print("Informações de memória do Windows disponíveis via wmic")
    except:
        print("Não foi possível verificar memória automaticamente")

def fix_ollama_memory_issue():
    """Corrige problema de memória do Ollama"""
    print("🔧 CORREÇÃO DO PROBLEMA DE MEMÓRIA OLLAMA")
    print("=" * 50)
    
    check_system_memory()
    
    print("\n📋 Soluções disponíveis:")
    print("1. Usar modelo menor do Ollama")
    print("2. Mudar para Groq API (gratuita, sem uso de RAM local)")
    print("3. Usar simulação (para desenvolvimento)")
    print("4. Liberar memória do sistema")
    
    choice = input("\nEscolha a solução (1-4): ").strip()
    
    if choice == "1":
        fix_ollama_model()
    elif choice == "2":
        setup_groq_alternative()
    elif choice == "3":
        setup_simulation_mode()
    elif choice == "4":
        free_system_memory()
    else:
        print("Opção inválida")

def fix_ollama_model():
    """Instala modelo menor do Ollama"""
    print("\n🔧 Instalando modelo menor...")
    
    # Modelos leves disponíveis
    light_models = [
        ("phi:2.7b", "2.7B parâmetros - ~1.5GB RAM"),
        ("gemma:2b", "2B parâmetros - ~1.3GB RAM"),
        ("tinyllama", "1.1B parâmetros - ~700MB RAM"),
        ("orca-mini", "3B parâmetros - ~1.9GB RAM")
    ]
    
    print("\nModelos leves disponíveis:")
    for i, (model, desc) in enumerate(light_models, 1):
        print(f"{i}. {model} - {desc}")
    
    model_choice = input(f"\nEscolha modelo (1-{len(light_models)}): ").strip()
    
    try:
        model_idx = int(model_choice) - 1
        if 0 <= model_idx < len(light_models):
            model_name = light_models[model_idx][0]
            
            print(f"\n📥 Baixando {model_name}...")
            result = subprocess.run(['ollama', 'pull', model_name], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ {model_name} instalado com sucesso!")
                update_main_py_ollama_model(model_name)
            else:
                print(f"❌ Erro ao instalar: {result.stderr}")
        else:
            print("Número inválido")
    except ValueError:
        print("Entrada inválida")

def setup_groq_alternative():
    """Configura alternativa com Groq"""
    print("\n🚀 CONFIGURAÇÃO GROQ (RECOMENDADA)")
    print("-" * 40)
    
    print("Vantagens da Groq:")
    print("✅ Sem uso de RAM local")
    print("✅ Muito mais rápida que Ollama")
    print("✅ 15,000 tokens/dia gratuitos")
    print("✅ Qualidade alta (Llama 3)")
    
    print("\n📋 Passos:")
    print("1. Acesse: https://console.groq.com/")
    print("2. Cadastre-se gratuitamente")
    print("3. Crie uma API key")
    print("4. Cole a chave abaixo")
    
    api_key = input("\nCole sua GROQ_API_KEY (ou Enter para pular): ").strip()
    
    if api_key:
        # Atualiza arquivo .env
        env_content = f"GROQ_API_KEY={api_key}\n"
        
        if os.path.exists('.env'):
            with open('.env', 'r') as f:
                existing = f.read()
            if 'GROQ_API_KEY' not in existing:
                env_content = existing + env_content
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("✅ GROQ_API_KEY salva no arquivo .env")
        
        # Testa conexão
        test_groq_connection(api_key)
    else:
        print("⚠️ Configure a API key manualmente depois")
        print("📝 Edite o arquivo .env e adicione: GROQ_API_KEY=sua_chave")

def test_groq_connection(api_key: str):
    """Testa conexão com Groq"""
    try:
        print("\n🔍 Testando conexão com Groq...")
        
        # Importa e testa
        sys.path.append('.')
        from main import LLMProvider
        
        llm = LLMProvider("groq")
        response = llm.generate("Responda apenas: OK", max_tokens=10)
        
        if "OK" in response or len(response) > 0:
            print("✅ Groq funcionando perfeitamente!")
            print(f"📝 Resposta de teste: {response[:100]}")
            return True
        else:
            print("⚠️ Resposta inesperada de Groq")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar Groq: {e}")
        return False

def setup_simulation_mode():
    """Configura modo simulação"""
    print("\n🎭 CONFIGURAÇÃO MODO SIMULAÇÃO")
    print("-" * 40)
    
    print("Vantagens da simulação:")
    print("✅ Sem uso de internet")
    print("✅ Sem limites de uso")
    print("✅ Perfeito para desenvolvimento")
    print("✅ Testa lógica do sistema")
    
    print("\nDesvantagens:")
    print("❌ Conteúdo fictício")
    print("❌ Não adequado para resultados finais do TCC")
    
    # Atualiza configuração
    update_main_py_provider("simulation")
    print("\n✅ Modo simulação ativado")
    print("💡 Para usar APIs reais depois, execute este script novamente")

def free_system_memory():
    """Orientações para liberar memória"""
    print("\n🧹 LIBERANDO MEMÓRIA DO SISTEMA")
    print("-" * 40)
    
    print("Passos para liberar memória:")
    print("\n1. Feche programas desnecessários:")
    print("   - Navegadores web (Chrome, Firefox)")
    print("   - Editores pesados (VSCode, PyCharm)")
    print("   - Aplicações de mídia")
    
    print("\n2. Limpe cache do sistema:")
    if os.name == 'posix':
        print("   sudo sync && sudo sysctl vm.drop_caches=3")
    else:
        print("   Use Disk Cleanup ou reinicie o sistema")
    
    print("\n3. Pare outros containers Docker:")
    print("   docker stop $(docker ps -q)")
    
    print("\n4. Reinicie o sistema se necessário")
    
    input("\nPressione Enter após liberar memória...")
    check_system_memory()

def update_main_py_ollama_model(new_model: str):
    """Atualiza modelo do Ollama no main.py"""
    try:
        if not os.path.exists('main.py'):
            print("❌ Arquivo main.py não encontrado")
            return
        
        with open('main.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Substitui modelo padrão
        old_pattern = 'self.model_name = "llama3:8b"'
        new_pattern = f'self.model_name = "{new_model}"'
        
        if old_pattern in content:
            content = content.replace(old_pattern, new_pattern)
            
            with open('main.py', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ main.py atualizado para usar {new_model}")
        else:
            print("⚠️ Não foi possível atualizar automaticamente")
            print(f"💡 Edite manualmente: self.model_name = \"{new_model}\"")
            
    except Exception as e:
        print(f"❌ Erro ao atualizar main.py: {e}")

def update_main_py_provider(provider: str):
    """Atualiza provider padrão no main.py"""
    try:
        if not os.path.exists('main.py'):
            print("❌ Arquivo main.py não encontrado")
            return
        
        with open('main.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Substitui provider na função main()
        old_pattern = 'llm = LLMProvider("auto")'
        new_pattern = f'llm = LLMProvider("{provider}")'
        
        if old_pattern in content:
            content = content.replace(old_pattern, new_pattern)
            
            with open('main.py', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ main.py atualizado para usar provider '{provider}'")
        else:
            print("⚠️ Não foi possível atualizar automaticamente")
            print(f"💡 Edite manualmente: llm = LLMProvider(\"{provider}\")")
            
    except Exception as e:
        print(f"❌ Erro ao atualizar main.py: {e}")

def quick_test_system():
    """Teste rápido do sistema após correção"""
    print("\n🧪 TESTE RÁPIDO DO SISTEMA")
    print("-" * 30)
    
    try:
        sys.path.append('.')
        from main import AutonoWriteSystem, LLMProvider
        
        # Testa provider configurado
        llm = LLMProvider("auto")
        print(f"✅ Provider ativo: {llm.provider_type}")
        
        if llm.provider_type == "ollama":
            print("⚠️ Ainda usando Ollama - pode ter problemas de memória")
            print("💡 Considere usar Groq ou simulação")
        
        # Teste muito básico
        system = AutonoWriteSystem(llm)
        print("✅ Sistema AutonoWrite inicializado")
        
        print("\n🎯 Sistema pronto para uso!")
        print("Execute: python main.py")
        
    except Exception as e:
        print(f"❌ Sistema ainda com problemas: {e}")
        print("💡 Execute as correções sugeridas acima")

if __name__ == "__main__":
    try:
        fix_ollama_memory_issue()
        quick_test_system()
        
        print("\n" + "=" * 50)
        print("✅ CORREÇÃO CONCLUÍDA")
        print("=" * 50)
        print("Próximos passos:")
        print("1. Execute: python main.py")
        print("2. Teste geração de conteúdo")
        print("3. Se houver problemas, execute este script novamente")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Correção interrompida")
    except Exception as e:
        print(f"\n❌ Erro na correção: {e}")