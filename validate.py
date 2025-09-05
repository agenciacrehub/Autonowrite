#!/usr/bin/env python3
"""
Script de Validação - AutonoWrite
Testes automatizados para verificar funcionamento do sistema
"""

import sys
import os
import traceback
from datetime import datetime

def test_imports():
    """Testa se todas as dependências estão instaladas"""
    print("🧪 Testando imports...")
    
    required_modules = [
        ("os", "Biblioteca padrão Python"),
        ("json", "Biblioteca padrão Python"), 
        ("datetime", "Biblioteca padrão Python"),
        ("typing", "Biblioteca padrão Python")
    ]
    
    optional_modules = [
        ("groq", "API Groq - pip install groq"),
        ("ollama", "Ollama local - pip install ollama"),
        ("dotenv", "Variáveis ambiente - pip install python-dotenv")
    ]
    
    # Testes obrigatórios
    for module, desc in required_modules:
        try:
            __import__(module)
            print(f"   ✅ {module} - {desc}")
        except ImportError as e:
            print(f"   ❌ {module} - ERRO: {e}")
            return False
    
    # Testes opcionais
    available_providers = []
    for module, desc in optional_modules:
        try:
            __import__(module)
            print(f"   ✅ {module} - {desc}")
            if module in ['groq', 'ollama']:
                available_providers.append(module)
        except ImportError:
            print(f"   ⚠️ {module} - Não instalado: {desc}")
    
    if not available_providers:
        print("   ⚠️ Nenhum provider LLM disponível - usará simulação")
        available_providers.append("simulation")
    
    return True, available_providers

def test_environment():
    """Testa configuração do ambiente"""
    print("\n🔧 Testando ambiente...")
    
    # Testa arquivo .env
    env_file = ".env"
    if os.path.exists(env_file):
        print(f"   ✅ Arquivo {env_file} encontrado")
        with open(env_file, 'r') as f:
            content = f.read()
            if "GROQ_API_KEY" in content:
                print("   ✅ GROQ_API_KEY configurada")
            else:
                print("   ⚠️ GROQ_API_KEY não encontrada")
    else:
        print(f"   ⚠️ Arquivo {env_file} não encontrado")
    
    # Testa estrutura de diretórios
    required_dirs = ["results", "experiments", "reports"]
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"   ✅ Diretório {dir_name}/ encontrado")
        else:
            os.makedirs(dir_name, exist_ok=True)
            print(f"   🔧 Diretório {dir_name}/ criado")
    
    # Testa permissões de escrita
    test_file = "test_write.tmp"
    try:
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        print("   ✅ Permissões de escrita OK")
    except Exception as e:
        print(f"   ❌ Erro de permissões: {e}")
        return False
    
    return True

# [Previous test functions remain the same until run_validation_suite]

def run_validation_suite():
    """Executa suite completa de validação"""
    print("=" * 60)
    print("🔬 SUITE DE VALIDAÇÃO - AUTONOWRITE")
    print("=" * 60)
    print(f"Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Imports e Dependências", test_imports),
        ("Configuração do Ambiente", test_environment),
    ]
    
    results = {}
    
    # Teste 1: Imports
    result = test_imports()
    if isinstance(result, tuple):
        success, available_providers = result
        results["imports"] = success
    else:
        results["imports"] = result
        if not result:
            print("\n❌ Falha crítica nos imports. Abortando testes.")
            return results
    
    # Teste 2: Ambiente
    results["environment"] = test_environment()
    if not results["environment"]:
        print("\n⚠️ Problemas no ambiente, mas continuando...")
    
    # Sumário final
    print("\n" + "=" * 60)
    print("📊 SUMÁRIO DA VALIDAÇÃO")
    print("=" * 60)
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    for test_name, passed_status in results.items():
        status = "✅ PASSOU" if passed_status else "❌ FALHOU"
        print(f"{test_name:25} {status}")
    
    print("-" * 40)
    print(f"Total: {passed}/{total} testes passaram ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Sistema pronto para uso")
    elif passed >= total * 0.8:
        print("\n⚠️ MAIORIA DOS TESTES PASSOU")
        print("✅ Sistema utilizável com limitações")
    else:
        print("\n❌ MUITOS TESTES FALHARAM")
        print("🔧 Sistema precisa de correções antes do uso")
    
    return results

if __name__ == "__main__":
    try:
        results = run_validation_suite()
        print(f"\n⏰ Validação concluída em: {datetime.now().strftime('%H:%M:%S')}")
    except KeyboardInterrupt:
        print("\n\n⚠️ Validação interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro fatal na validação: {e}")
        traceback.print_exc()
