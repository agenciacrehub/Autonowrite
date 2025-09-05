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

def test_llm_providers(available_providers):
    """Testa conectividade com providers LLM"""
    print("\n🤖 Testando providers LLM...")
    
    # Importa o código principal
    try:
        sys.path.append('.')
        from main import LLMProvider
        print("   ✅ Classe LLMProvider importada com sucesso")
    except ImportError as e:
        print(f"   ❌ Erro ao importar LLMProvider: {e}")
        print("   💡 Verifique se o arquivo main.py está no diretório atual")
        return False
    
    working_providers = []
    
    for provider in available_providers:
        try:
            print(f"   🔍 Testando provider: {provider}")
            llm = LLMProvider(provider)
            
            # Teste simples
            response = llm.generate("Teste: responda apenas 'OK'", max_tokens=50)
            
            if response and len(response) > 0:
                print(f"   ✅ {provider} funcionando (resposta: {len(response)} chars)")
                working_providers.append(provider)
            else:
                print(f"   ⚠️ {provider} retornou resposta vazia")
                
        except Exception as e:
            print(f"   ❌ {provider} falhou: {str(e)[:100]}...")
    
    if not working_providers:
        print("   ❌ Nenhum provider funcionando!")
        return False
    
    return True, working_providers

def test_system_integration(working_providers):
    """Testa integração completa do sistema"""
    print("\n🔗 Testando integração do sistema...")
    
    try:
        from main import AutonoWriteSystem, LLMProvider
        
        # Usa o primeiro provider funcionando
        provider = working_providers[0]
        print(f"   🔧 Usando provider: {provider}")
        
        llm = LLMProvider(provider)
        system = AutonoWriteSystem(llm)
        
        print("   ✅ Sistema AutonoWrite inicializado")
        
        # Teste rápido com 1 iteração
        print("   🧪 Executando teste rápido...")
        test_topic = "Teste de funcionamento do sistema"
        
        result = system.generate_content(test_topic, max_iterations=1)
        
        # Valida resultado
        required_keys = [
            'topic', 'final_content', 'final_score', 
            'iterations_used', 'execution_time_seconds'
        ]
        
        for key in required_keys:
            if key not in result:
                print(f"   ❌ Chave '{key}' ausente no resultado")
                return False
            print(f"   ✅ {key}: {str(result[key])[:50]}...")
        
        print(f"   📊 Resultado do teste:")
        print(f"      - Score: {result['final_score']:.1f}/10")
        print(f"      - Tempo: {result['execution_time_seconds']:.1f}s")
        print(f"      - LLM calls: {result['llm_calls']}")
        
        return True, result
        
    except Exception as e:
        print(f"   ❌ Erro na integração: {e}")
        traceback.print_exc()
        return False

def test_experiment_framework():
    """Testa framework de experimentos"""
    print("\n🧪 Testando framework de experimentos...")
    
    try:
        from main import ExperimentRunner, AutonoWriteSystem, LLMProvider
        
        # Sistema mínimo
        llm = LLMProvider("simulation")
        system = AutonoWriteSystem(llm)
        runner = ExperimentRunner(system)
        
        print("   ✅ ExperimentRunner inicializado")
        
        # Teste mini-experimento
        test_topics = ["Tópico A", "Tópico B"]
        iterations_list = [1, 2]
        
        print("   🏃 Executando mini-experimento...")
        experiment_result = runner.run_comparative_experiment(test_topics, iterations_list)
        
        # Valida estrutura do experimento
        required_keys = ['experiment_id', 'topics', 'configurations', 'summary']
        for key in required_keys:
            if key not in experiment_result:
                print(f"   ❌ Chave '{key}' ausente no experimento")
                return False
        
        print("   ✅ Experimento executado com sucesso")
        print(f"   📊 Configurações testadas: {len(experiment_result['configurations'])}")
        print(f"   📈 Melhoria de qualidade: {experiment_result['summary']['quality_improvement_percent']}%")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro no framework de experimentos: {e}")
        return False

def test_file_operations():
    """Testa operações de arquivo"""
    print("\n💾 Testando operações de arquivo...")
    
    try:
        from main import AutonoWriteSystem, LLMProvider
        import json
        
        llm = LLMProvider("simulation")
        system = AutonoWriteSystem(llm)
        
        # Gera resultado de teste
        result = system.generate_content("Teste de salvamento", max_iterations=1)
        
        # Testa salvamento
        filepath = system.save_result(result, "test_result.json")
        
        if os.path.exists(filepath):
            print("   ✅ Arquivo salvo com sucesso")
            
            # Testa leitura
            with open(filepath, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
            
            if loaded_data['topic'] == result['topic']:
                print("   ✅ Arquivo carregado corretamente")
            else:
                print("   ❌ Dados corrompidos no arquivo")
                return False
            
            # Limpa arquivo de teste
            os.remove(filepath)
            print("   🧹 Arquivo de teste removido")
            
        else:
            print("   ❌ Arquivo não foi salvo")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro nas operações de arquivo: {e}")
        return False

def run_validation_suite():
    """Executa suite completa de validação"""
    print("=" * 60)
    print("🔬 SUITE DE VALIDAÇÃO - AUTONOWRITE")
    print("=" * 60)
    print(f"Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Imports e Dependências", test_imports),
        ("Configuração do Ambiente", test_environment),
        ("Conectividade LLM", None),  # Será chamado com parâmetro
        ("Integração do Sistema", None),  # Será chamado com parâmetro
        ("Framework de Experimentos", test_experiment_framework),
        ("Operações de Arquivo", test_file_operations)
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
    
    # Teste 3: Providers LLM
    if 'available_providers' in locals():
        llm_result = test_llm_providers(available_providers)
        if isinstance(llm_result, tuple):
            results["llm_providers"], working_providers = llm_result
        else:
            results["llm_providers"] = llm_result
            working_providers = ["simulation"]
    else:
        results["llm_providers"] = False
        working_providers = ["simulation"]
    
    # Teste 4: Integração do Sistema
    if working_providers:
        integration_result = test_system_integration(working_providers)
        if isinstance(integration_result, tuple):
            results["system_integration"], test_result = integration_result
        else:
            results["system_integration"] = integration_result
    else:
        results["system_integration"] = False
    
    # Teste 5: Framework de Experimentos
    results["experiments"] = test_experiment_framework()
    
    # Teste 6: Operações de Arquivo
    results["file_operations"] = test_file_operations()
    
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
        print("\n📋 Próximos passos:")
        print("1. Execute: python main.py")
        print("2. Teste geração de conteúdo único")
        print("3. Execute experimento comparativo")
    elif passed >= total * 0.8:
        print("\n⚠️ MAIORIA DOS TESTES PASSOU")
        print("✅ Sistema utilizável com limitações")
        print("🔧 Revise os testes que falharam acima")
    else:
        print("\n❌ MUITOS TESTES FALHARAM")
        print("🔧 Sistema precisa de correções antes do uso")
        print("💡 Revise o guia de setup e dependências")
    
    return results

def generate_validation_report(results):
    """Gera relatório de validação"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_content = f"""# Relatório de Validação - AutonoWrite

**Data**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Sistema**: {os.name} - Python {sys.version.split()[0]}

## Resultados dos Testes

"""
    
    for test_name, result in results.items():
        status = "PASSOU" if result else "FALHOU"
        report_content += f"- **{test_name}**: {status}\n"
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    report_content += f"""
## Sumário
- **Testes Executados**: {total}
- **Testes Aprovados**: {passed}
- **Taxa de Sucesso**: {passed/total*100:.1f}%

## Status do Sistema
"""
    
    if passed == total:
        report_content += "✅ **Sistema APROVADO** - Pronto para uso em produção\n"
    elif passed >= total * 0.8:
        report_content += "⚠️ **Sistema FUNCIONAL** - Utilizável com limitações\n"
    else:
        report_content += "❌ **Sistema NÃO APROVADO** - Requer correções\n"
    
    # Salvar relatório
    os.makedirs("reports", exist_ok=True)
    report_file = f"reports/validation_report_{timestamp}.md"
    
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        print(f"\n📄 Relatório salvo em: {report_file}")
    except Exception as e:
        print(f"⚠️ Não foi possível salvar relatório: {e}")

if __name__ == "__main__":
    try:
        results = run_validation_suite()
        generate_validation_report(results)
        
        print(f"\n⏰ Validação concluída em: {datetime.now().strftime('%H:%M:%S')}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Validação interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro fatal na validação: {e}")
        traceback.print_exc()