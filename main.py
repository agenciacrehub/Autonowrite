#!/usr/bin/env python3
"""
AutonoWrite - Sistema Multiagente para Geração de Conteúdo
Versão integrada para TCC com recursos gratuitos
"""

import os
import json
import time
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("⚠️  Groq não instalado. Use: pip install groq")

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

try:
    from dotenv import load_dotenv
    load_dotenv()
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False


class LLMProvider:
    """Provider base para diferentes modelos LLM"""
    
    def __init__(self, provider_type: str = "simulation"):
        self.call_count = 0
        self.provider_type = provider_type
        self.client = None
        
        if provider_type == "auto":
            self._setup_auto()
        elif provider_type == "groq":
            self._setup_groq()
        elif provider_type == "ollama":
            self._setup_ollama()
        elif provider_type == "simulation":
            self._setup_simulation()
    
    def _setup_auto(self):
        """Setup automático inteligente baseado em ambiente e disponibilidade.

        Ordem de seleção:
        1. LLM_PROVIDER, se definido (groq/ollama/simulation)
        2. GROQ_API_KEY presente e groq instalado -> groq
        3. Ollama disponível -> ollama
        4. Caso contrário -> simulation
        """
        provider_env = os.getenv("LLM_PROVIDER", "").strip().lower()
        if provider_env in {"groq", "ollama", "simulation"}:
            print(f"🔧 LLM_PROVIDER definido: {provider_env}")
            try:
                if provider_env == "groq":
                    self._setup_groq()
                    return
                if provider_env == "ollama":
                    self._setup_ollama()
                    return
                # simulation
                self._setup_simulation()
                return
            except Exception as e:
                print(f"⚠️  Falha ao inicializar provider '{provider_env}': {e}. Tentando fallback...")
        
        # Detecção automática
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key and GROQ_AVAILABLE:
            try:
                self._setup_groq()
                return
            except Exception as e:
                print(f"⚠️  Falha Groq: {e}")
        
        if OLLAMA_AVAILABLE:
            try:
                self._setup_ollama()
                return
            except Exception as e:
                print(f"⚠️  Falha Ollama: {e}")
        
        print("🎭 Usando simulação por não haver provider real disponível")
        self._setup_simulation()
    
    def _setup_groq(self):
        """Configura Groq API"""
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY não encontrada. Configure no .env")
        
        self.client = Groq(api_key=api_key)
        self.provider_type = "groq"
        self.model_name = "llama-3.3-70b-versatile"
        print("🚀 Usando Groq API (llama-3.3-70b-versatile)")
    
    def _setup_ollama(self):
        """Configura Ollama local"""
        self.provider_type = "ollama"
        self.model_name = "gemma:2b"  # Modelo mais leve para sistemas com menos memória
        print(f"🏠 Usando Ollama local ({self.model_name})")
        print("ℹ️  Baixando o modelo pela primeira vez, pode demorar alguns minutos...")
        try:
            import ollama
            ollama.pull(self.model_name)  # Garante que o modelo está baixado
        except Exception as e:
            print(f"⚠️  Erro ao baixar o modelo: {e}")
            raise
    
    def _setup_simulation(self):
        """Configura simulação para desenvolvimento"""
        self.provider_type = "simulation"
        self.model_name = "simulado"
        print("🎭 Usando simulação (para desenvolvimento)")
        print("ℹ️  Modo de simulação ativado - usando respostas pré-definidas")
    
    def generate(self, prompt: str, max_tokens: int = 1500) -> str:
        """Gera resposta usando o provider configurado"""
        self.call_count += 1
        
        if self.provider_type == "groq":
            return self._generate_groq(prompt, max_tokens)
        elif self.provider_type == "ollama":
            return self._generate_ollama(prompt, max_tokens)
        else:
            return self._generate_simulation(prompt)
    
    def _generate_groq(self, prompt: str, max_tokens: int) -> str:
        """Geração via Groq"""
        try:
            completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model_name,
                max_tokens=max_tokens,
                temperature=0.7
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Erro Groq: {str(e)}"
    
    def _generate_ollama(self, prompt: str, max_tokens: int) -> str:
        """Geração via Ollama"""
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[{'role': 'user', 'content': prompt}]
            )
            return response['message']['content']
        except Exception as e:
            return f"Erro Ollama: {str(e)}"
    
    def _simulate_llm_response(self, prompt: str, max_tokens: int) -> str:
        """Simula uma resposta do LLM para desenvolvimento"""
        # Simula diferentes tipos de respostas baseado no conteúdo do prompt
        if "planejamento" in prompt.lower() or "plano" in prompt.lower():
            return """
            Plano para o tópico:
            1. Introdução ao conceito
            2. Explicação detalhada
            3. Exemplos práticos
            4. Conclusão
            """
        elif "pesquisa" in prompt.lower():
            return """
            Pesquisa sobre o tópico:
            - Fonte 1: Artigo científico relevante
            - Fonte 2: Dados estatísticos atualizados
            - Fonte 3: Estudos de caso
            """
        elif "avaliação" in prompt.lower() or "crítica" in prompt.lower():
            return """
            Avaliação crítica:
            - Pontos fortes: Clareza, organização
            - Pontos fracos: Poderia ter mais exemplos
            - Pontuação: 8.5/10
            """
        elif "crítico" in prompt.lower() or "editor" in prompt.lower():
            return self._simulate_critic()
        else:
            return f"Simulação - Resposta para: {prompt[:100]}..."
    
    def _simulate_planner(self) -> str:
        return """
## Plano Estruturado

### 1. Introdução
- Contextualização do tema
- Relevância e importância atual
- Objetivos do artigo

### 2. Fundamentação Teórica  
- Conceitos fundamentais
- Estado da arte
- Revisão da literatura

### 3. Análise Crítica
- Vantagens e limitações
- Casos de uso práticos
- Comparações com alternativas

### 4. Discussão e Implicações
- Impactos na área
- Desafios identificados
- Oportunidades futuras

### 5. Conclusão
- Síntese dos pontos principais
- Contribuições do trabalho
- Sugestões para pesquisas futuras

**Palavras-chave**: sistema multiagente, inteligência artificial, automação
"""
    
    def _simulate_researcher(self) -> str:
        return """
## Relatório de Pesquisa

### Fontes Identificadas:
1. "Multiagent Systems: Algorithmic, Game-Theoretic, and Logical Foundations" (2008)
2. "Large Language Models: A Survey" - ArXiv 2024  
3. "CrewAI Framework Documentation" - Documentação oficial 2024
4. "Prompt Engineering for Large Language Models" - ACM 2024

### Dados Relevantes:
- Sistemas multiagente mostram 40-60% de melhoria em tarefas complexas
- LLMs apresentam taxa de alucinação de 15-25% em tarefas factuais
- Ciclos de crítica reduzem alucinações em até 70%
- CrewAI framework adotado por 500+ empresas em 2024

### Informações Técnicas:
- Arquitetura baseada em agentes especializados
- Uso de engenharia de prompt para orquestração
- Implementação de ciclos de feedback e refinamento
- Métricas de avaliação: ROUGE, BLEU, avaliação humana
"""
    
    def _simulate_writer(self, topic_hint: str = "") -> str:
        # Generate content based on the topic hint
        if "buraco" in topic_hint.lower() and "negro" in topic_hint.lower():
            return self._simulate_black_holes_content()
        elif "buraco" in topic_hint.lower() and "branco" in topic_hint.lower():
            return self._simulate_white_holes_content()
        else:
            return self._simulate_default_content()
    
    def _simulate_black_holes_content(self) -> str:
        return """
# Buracos Negros: Fenômenos Extremos do Universo

## Introdução

Os buracos negros representam alguns dos objetos mais fascinantes e extremos do universo conhecido. Essas regiões do espaço-tempo onde a gravidade é tão intensa que nem mesmo a luz pode escapar, desafiam nossa compreensão da física e continuam a revelar segredos fundamentais sobre a natureza do cosmos.

## Fundamentação Teórica

### Origem e Formação

Os buracos negros se formam quando uma estrela massiva (pelo menos 20-25 vezes a massa do Sol) chega ao fim de sua vida. Durante o colapso gravitacional, a matéria é comprimida em um ponto de densidade infinita chamado singularidade, cercado pelo horizonte de eventos - a fronteira além da qual nada pode escapar.

### Propriedades Fundamentais

Um buraco negro é caracterizado por apenas três propriedades:
- **Massa**: Determina o tamanho do horizonte de eventos
- **Carga elétrica**: Geralmente neutra devido à neutralização
- **Momento angular**: Rotação do buraco negro (spin)

### Tipos de Buracos Negros

1. **Buracos Negros Estelares**: Formados pelo colapso de estrelas massivas (3-20 massas solares)
2. **Buracos Negros Intermediários**: Massa entre 100-100.000 massas solares
3. **Buracos Negros Supermassivos**: Milhões a bilhões de massas solares, encontrados no centro das galáxias

## Descobertas e Evidências Observacionais

### Detecção por Ondas Gravitacionais

Em 2015, o LIGO detectou pela primeira vez ondas gravitacionais produzidas pela fusão de dois buracos negros, confirmando previsões da relatividade geral de Einstein e abrindo uma nova era na astronomia.

### Primeira Imagem de um Buraco Negro

Em 2019, o Event Horizon Telescope capturou a primeira imagem direta de um buraco negro - o M87* na galáxia M87, revelando a sombra do horizonte de eventos cercada por matéria superaquecida.

### Sagittarius A*

Em 2022, foi divulgada a imagem do buraco negro supermassivo no centro da nossa galáxia, Sagittarius A*, com massa equivalente a 4 milhões de sóis.

## Fenômenos Associados

### Radiação Hawking

Stephen Hawking previu que buracos negros emitem radiação devido a efeitos quânticos próximos ao horizonte de eventos, levando à sua eventual evaporação. Quanto menor o buraco negro, mais rápida é a evaporação.

### Discos de Acreção

Matéria que cai em direção ao buraco negro forma um disco de acreção superaquecido, emitindo radiação intensa em várias frequências, tornando os buracos negros alguns dos objetos mais brilhantes do universo.

### Jets Relativísticos

Buracos negros em rotação podem acelerar partículas a velocidades próximas à da luz, criando jatos que se estendem por milhares de anos-luz.

## Implicações Cosmológicas

### Papel na Evolução Galáctica

Buracos negros supermassivos influenciam a formação e evolução das galáxias, regulando a formação estelar através de feedback energético.

### Paradoxos e Questões Fundamentais

- **Paradoxo da Informação**: O que acontece com a informação que cai em um buraco negro?
- **Singularidades**: Pontos onde as leis da física conhecidas falham
- **Conexão com a Mecânica Quântica**: Interface entre relatividade geral e física quântica

## Pesquisas Atuais e Futuras

### Próximas Missões

- **Event Horizon Telescope**: Expansão da rede para imagens mais detalhadas
- **LISA**: Detector espacial de ondas gravitacionais
- **Telescópio James Webb**: Observações no infravermelho de buracos negros primordiais

### Questões em Aberto

1. Como se formaram os primeiros buracos negros supermassivos?
2. Qual é a natureza exata das singularidades?
3. Como resolver o paradoxo da informação?
4. Existem buracos negros primordiais formados no universo primitivo?

## Conclusão

Os buracos negros continuam a ser laboratórios naturais únicos para testar nossa compreensão da física fundamental. Desde a confirmação de sua existência até as recentes imagens diretas, esses objetos extremos revelam aspectos profundos sobre a natureza do espaço, tempo e gravidade.

As descobertas futuras prometem não apenas expandir nosso conhecimento sobre buracos negros, mas também revolucionar nossa compreensão do universo como um todo, potencialmente levando a novas teorias que unifiquem a relatividade geral com a mecânica quântica.

**Referências**: Einstein (1915), Schwarzschild (1916), Hawking (1974), LIGO Scientific Collaboration (2015), Event Horizon Telescope Collaboration (2019, 2022)
"""

    def _simulate_white_holes_content(self) -> str:
        return """
# Buracos Brancos: O Reverso Teórico dos Buracos Negros

## Introdução

Os buracos brancos representam uma das mais fascinantes e controversas previsões teóricas da relatividade geral. Enquanto os buracos negros absorvem tudo que se aproxima, os buracos brancos são conceitualmente o oposto: regiões do espaço-tempo que expelem matéria e energia, sem permitir que nada entre.

## Fundamentação Teórica

### Origem Matemática

Os buracos brancos emergem naturalmente das equações de Einstein quando consideramos a reversibilidade temporal das soluções. A métrica de Schwarzschild, que descreve buracos negros, possui uma solução "espelhada" que corresponde aos buracos brancos.

### Propriedades Fundamentais

Um buraco branco teórico possui:
- **Horizonte de eventos**: Fronteira que permite apenas saída, nunca entrada
- **Singularidade**: Ponto de densidade infinita no centro
- **Reversão temporal**: Comportamento oposto ao buraco negro

### Relação com Buracos Negros

Na teoria, buracos brancos e negros podem estar conectados através de "pontes Einstein-Rosen" (buracos de minhoca), formando estruturas chamadas de buracos negros eternos.

## Desafios Teóricos

### Violação da Segunda Lei da Termodinâmica

Buracos brancos parecem violar o princípio de que a entropia deve sempre aumentar, pois expelem matéria organizada sem causa aparente.

### Instabilidade Gravitacional

Análises teóricas sugerem que buracos brancos seriam extremamente instáveis. Qualquer perturbação mínima causaria seu colapso imediato em um buraco negro.

### Problema da Causalidade

A existência de buracos brancos levanta questões sobre causalidade e determinismo, pois eventos futuros (expulsão de matéria) não teriam causa no passado.

## Possíveis Manifestações Observacionais

### Big Bang como Buraco Branco

Alguns cosmólogos especulam que o Big Bang poderia ter sido um buraco branco primordial, expelindo toda a matéria e energia do universo observável.

### Gamma-Ray Bursts

Explosões de raios gama extremamente energéticas foram propostas como possíveis assinaturas de buracos brancos, embora explicações convencionais sejam mais aceitas.

### Quasares e Objetos Ativos

Alguns fenômenos astrofísicos extremos foram hipoteticamente atribuídos a buracos brancos, mas evidências observacionais são inexistentes.

## Modelos Alternativos

### Estrelas de Planck

Alguns teóricos propõem que o que interpretamos como buracos negros poderiam ser "estrelas de Planck" - objetos que se comportam como buracos brancos em escalas quânticas.

### Cosmologia Cíclica

Em modelos de universo cíclico, buracos brancos poderiam ser o mecanismo pelo qual um universo colapsado "ressurge" como um novo Big Bang.

### Gravidade Quântica em Loop

Esta teoria sugere que singularidades de buracos negros poderiam "saltar" para buracos brancos através de efeitos quânticos.

## Evidências e Limitações

### Ausência de Observações

Até o momento, não há evidências observacionais convincentes da existência de buracos brancos no universo atual.

### Argumentos Contra a Existência

1. **Instabilidade**: Modelos mostram que buracos brancos colapsariam instantaneamente
2. **Termodinâmica**: Violação aparente de leis fundamentais
3. **Formação**: Nenhum mecanismo conhecido poderia criar buracos brancos

### Limitações dos Modelos

As soluções matemáticas que preveem buracos brancos assumem condições idealizadas que provavelmente não existem na natureza.

## Implicações Filosóficas e Cosmológicas

### Natureza do Tempo

Buracos brancos desafiam nossa compreensão da direção do tempo e da causalidade, sugerindo que o tempo pode não ser tão linear quanto percebemos.

### Origem do Universo

Se o Big Bang foi um buraco branco, isso poderia explicar por que o universo começou em um estado de baixa entropia.

### Multiverso

Buracos brancos poderiam ser portais entre diferentes regiões do espaço-tempo ou até mesmo universos paralelos.

## Pesquisas Atuais

### Simulações Numéricas

Físicos usam supercomputadores para modelar a evolução de buracos brancos em condições realistas, geralmente confirmando sua instabilidade.

### Teorias Quânticas da Gravidade

Pesquisadores investigam se efeitos quânticos poderiam estabilizar buracos brancos ou criar condições para sua formação.

### Cosmologia Observacional

Astrônomos buscam assinaturas observacionais que poderiam distinguir fenômenos de buracos brancos de explicações convencionais.

## Conclusão

Embora buracos brancos sejam previsões matemáticas elegantes da relatividade geral, sua existência física permanece altamente questionável. Os desafios teóricos - instabilidade, violação termodinâmica e problemas causais - sugerem que são mais curiosidades matemáticas do que realidades físicas.

No entanto, o estudo de buracos brancos continua valioso para nossa compreensão da relatividade geral, cosmologia e natureza fundamental do espaço-tempo. Eles servem como "experimentos mentais" que testam os limites de nossas teorias físicas e podem eventualmente levar a descobertas sobre a natureza do universo.

A busca por buracos brancos, mesmo que infrutífera, aprofunda nossa compreensão dos buracos negros reais e dos fenômenos extremos que governam o cosmos.

**Referências**: Novikov (1964), Hawking & Ellis (1973), Penrose (2004), Rovelli & Vidotto (2014)
"""

    def _simulate_default_content(self) -> str:
        return """
# Sistemas Multiagente para Geração Automatizada de Conteúdo

## Introdução

A evolução da inteligência artificial tem proporcionado avanços significativos na automação de tarefas cognitivas complexas. Entre essas inovações, os sistemas multiagente emergem como uma abordagem promissora para superar limitações dos modelos monolíticos tradicionais, especialmente no contexto de geração de conteúdo.

## Fundamentação Teórica

Os sistemas multiagente (MAS) representam uma arquitetura distribuída onde múltiplos agentes autônomos colaboram para resolver problemas complexos. No contexto de geração de texto, essa abordagem permite a especialização de diferentes componentes: planejamento, pesquisa, redação e revisão.

A filosofia "dividir para conquistar" permite decompor a tarefa de escrita em subtarefas menores e mais gerenciáveis, cada uma executada por um agente especializado com objetivos e competências específicas.

## Análise Crítica

A principal vantagem dos sistemas multiagente reside na capacidade de emular processos humanos de produção editorial. Um escritor profissional naturalmente alterna entre fases de pesquisa, estruturação, redação e revisão. O AutonoWrite replica esse processo através de agentes especializados.

### Vantagens Identificadas:
- Redução significativa de alucinações através do ciclo crítico
- Melhoria iterativa da qualidade do conteúdo
- Especialização permite maior profundidade técnica
- Flexibilidade para diferentes tipos de conteúdo

### Limitações Observadas:
- Maior custo computacional devido a múltiplas iterações
- Dependência da qualidade dos prompts de cada agente
- Complexidade de orquestração entre componentes

## Conclusão

O sistema AutonoWrite demonstra o potencial dos sistemas multiagente para superar limitações dos modelos monolíticos. Através da especialização e colaboração entre agentes, é possível produzir conteúdo de maior qualidade, factualidade e coerência.

Os resultados preliminares indicam que a abordagem multiagente representa um avanço significativo na automação de tarefas de conhecimento, com aplicações promissoras em contextos acadêmicos, jornalísticos e corporativos.
"""
    
    def _simulate_critic(self) -> str:
        return """
## Avaliação Crítica do Conteúdo

### Pontuação Geral: 7.8/10

### Critérios Detalhados:

**Estrutura e Organização: 8.5/10**
✅ Estrutura lógica clara com introdução, desenvolvimento e conclusão
✅ Transições adequadas entre seções  
⚠️ Algumas seções poderiam ser mais equilibradas

**Profundidade Técnica: 7.0/10**
✅ Conceitos fundamentais bem explicados
✅ Terminologia técnica apropriada
⚠️ Poderia incluir mais exemplos práticos na seção de análise

**Clareza e Legibilidade: 8.5/10**
✅ Linguagem clara e acessível
✅ Fluxo narrativo coerente
✅ Parágrafos bem construídos

**Verificabilidade das Fontes: 6.5/10** 
⚠️ Menciona conceitos sem citações específicas
⚠️ Faltam referências diretas a estudos mencionados
⚠️ Necessário incluir mais dados quantitativos

**Coerência Argumentativa: 8.0/10**
✅ Argumentos consistentes ao longo do texto
✅ Conclusões coerentes com o desenvolvimento
⚠️ Poderia fortalecer contrapontos

### Recomendações Específicas:
1. Adicionar citações diretas para os dados quantitativos mencionados
2. Incluir exemplo prático de implementação na seção 3
3. Expandir discussão sobre limitações éticas
4. Verificar se todos os termos técnicos estão adequadamente definidos

**Status: APROVADO COM REVISÕES MENORES**"""
        
    def _generate_simulation(self, prompt: str) -> str:
        """Gera uma resposta simulada baseada no papel do agente"""
        # Simula diferentes tipos de respostas baseado no papel do agente
        if "planejador" in prompt.lower() or "plano" in prompt.lower():
            return self._simulate_planner()
        elif "pesquisador" in prompt.lower() or "pesquisa" in prompt.lower():
            return self._simulate_researcher()
        elif "redator" in prompt.lower() or "escrever" in prompt.lower():
            return self._simulate_writer(prompt)  # Pass prompt to detect topic
        elif "crítico" in prompt.lower() or "avaliar" in prompt.lower():
            return self._simulate_critic()
        else:
            # Resposta genérica para outros casos
            return self._simulate_llm_response(prompt, max_tokens=1000)


class AgentRole(Enum):
    PLANNER = "planejador"
    RESEARCHER = "pesquisador"
    WRITER = "redator"
    CRITIC = "crítico"


@dataclass
class TaskResult:
    agent_role: AgentRole
    content: str
    metadata: Dict
    timestamp: datetime
    success: bool = True


class Agent:
    """Agente especializado do sistema"""
    
    def __init__(self, role: AgentRole, llm_provider: LLMProvider):
        self.role = role
        self.llm = llm_provider
        self.memory = []
    
    def execute_task(self, task: str, context: Optional[str] = None) -> TaskResult:
        """Executa tarefa específica do agente"""
        
        prompt = self._build_prompt(task, context)
        response = self.llm.generate(prompt)
        
        result = TaskResult(
            agent_role=self.role,
            content=response,
            metadata={
                "prompt_length": len(prompt),
                "response_length": len(response),
                "context_provided": context is not None
            },
            timestamp=datetime.now()
        )
        
        self.memory.append(result)
        return result
    
    def _build_prompt(self, task: str, context: Optional[str] = None) -> str:
        """Constrói prompt específico para cada agente"""
        
        prompts = {
            AgentRole.PLANNER: f"""
Você é um PLANEJADOR ESTRATÉGICO especialista em estruturação de conteúdo acadêmico e técnico.

TAREFA: {task}

Crie um plano detalhado e bem estruturado para abordar este tópico. Inclua:
- Seções principais e subseções
- Pontos-chave a serem abordados
- Sequência lógica de desenvolvimento
- Palavras-chave relevantes

Formate como um outline claro e hierárquico.
""",
            
            AgentRole.RESEARCHER: f"""
Você é um PESQUISADOR ACADÊMICO meticuloso e experiente.

TAREFA: {task}
PLANO DE REFERÊNCIA: {context or 'Não fornecido'}

Conduza uma pesquisa abrangente sobre o tópico. Forneça:
- Fontes confiáveis e atuais (artigos, estudos, documentação)
- Dados quantitativos relevantes
- Informações técnicas precisas
- Citações e referências quando apropriado

Organize as informações de forma clara e estruturada.
""",
            
            AgentRole.WRITER: f"""
Você é um REDATOR PROFISSIONAL com expertise em conteúdo técnico e acadêmico.

TAREFA: {task}
CONTEXTO DISPONÍVEL: {context or 'Não fornecido'}

Escreva um texto completo, bem estruturado e envolvente. Garanta:
- Linguagem clara e apropriada para o público-alvo
- Estrutura lógica seguindo o plano fornecido
- Uso adequado das informações de pesquisa
- Transições suaves entre seções
- Conclusão que sintetiza os pontos principais

Produza um texto coerente e de alta qualidade.
""",
            
            AgentRole.CRITIC: f"""
Você é um CRÍTICO RIGOROSO e avaliador de qualidade editorial.

TEXTO PARA AVALIAÇÃO: {task}

Avalie o texto com base nos seguintes critérios:
1. **Estrutura e Organização** (0-10)
2. **Profundidade Técnica** (0-10)  
3. **Clareza e Legibilidade** (0-10)
4. **Verificabilidade das Fontes** (0-10)
5. **Coerência Argumentativa** (0-10)

Para cada critério:
- Forneça uma pontuação
- Identifique pontos fortes
- Aponte áreas para melhoria
- Ofereça sugestões específicas

Conclua com:
- **Pontuação Geral** (média ponderada)
- **Status**: APROVADO, APROVADO COM REVISÕES, ou REQUER REVISÃO MAIOR
- **Recomendações prioritárias** para melhoria

Seja construtivo mas rigoroso na avaliação.
"""
        }
        
        return prompts[self.role]


class AutonoWriteSystem:
    """Sistema principal AutonoWrite"""
    
    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider
        self.agents = {
            AgentRole.PLANNER: Agent(AgentRole.PLANNER, llm_provider),
            AgentRole.RESEARCHER: Agent(AgentRole.RESEARCHER, llm_provider),
            AgentRole.WRITER: Agent(AgentRole.WRITER, llm_provider),
            AgentRole.CRITIC: Agent(AgentRole.CRITIC, llm_provider)
        }
        self.max_iterations = 3
        self.min_quality_score = 8.0
        self.execution_log = []
    
    def generate_content(self, topic: str, max_iterations: Optional[int] = None) -> Dict:
        """Pipeline principal de geração"""
        
        if max_iterations:
            self.max_iterations = max_iterations
        
        print(f"\n🚀 AutonoWrite iniciando para: {topic}")
        print(f"📊 Configuração: {self.max_iterations} iterações máximas")
        print(f"🤖 Provider: {self.llm.provider_type} ({self.llm.model_name})")
        
        start_time = datetime.now()
        
        # Fase 1: Planejamento
        print(f"\n📋 Fase 1: Planejamento...")
        plan_result = self.agents[AgentRole.PLANNER].execute_task(
            f"Criar plano estruturado para artigo sobre: {topic}"
        )
        
        # Fase 2: Pesquisa  
        print(f"\n🔍 Fase 2: Pesquisa...")
        research_result = self.agents[AgentRole.RESEARCHER].execute_task(
            f"Pesquisar informações detalhadas sobre: {topic}",
            context=plan_result.content
        )
        
        # Fase 3: Redação com ciclo crítico
        print(f"\n✍️ Fase 3: Redação e Refinamento...")
        
        current_draft = None
        iteration = 1
        final_approved = False
        critic_history = []
        
        while iteration <= self.max_iterations and not final_approved:
            print(f"\n   📝 Iteração {iteration}/{self.max_iterations}")
            
            # Redação/revisão
            if current_draft is None:
                # Primeira redação
                context = f"PLANO:\n{plan_result.content}\n\nPESQUISA:\n{research_result.content}"
                task = f"Escrever artigo completo sobre: {topic}"
            else:
                # Revisão baseada em feedback
                context = f"FEEDBACK ANTERIOR:\n{critic_history[-1]['content']}"
                task = f"Revisar e melhorar este texto:\n\n{current_draft}"
            
            write_result = self.agents[AgentRole.WRITER].execute_task(task, context)
            current_draft = write_result.content
            
            # Avaliação crítica
            print(f"   🔍 Avaliação crítica...")
            critic_result = self.agents[AgentRole.CRITIC].execute_task(current_draft)
            
            # Extrai score da avaliação
            score = self._extract_score(critic_result.content)
            
            critic_history.append({
                'iteration': iteration,
                'content': critic_result.content,
                'score': score
            })
            
            print(f"   📊 Score obtido: {score:.1f}/10")
            
            # Verifica aprovação
            if "APROVADO" in critic_result.content and "REQUER REVISÃO MAIOR" not in critic_result.content:
                if score >= self.min_quality_score:
                    final_approved = True
                    print(f"   ✅ Texto aprovado na iteração {iteration}!")
                else:
                    print(f"   ⚠️ Score baixo ({score:.1f}) - continuando...")
            else:
                print(f"   🔄 Requer revisão - continuando...")
            
            iteration += 1
        
        end_time = datetime.now()
        
        # Resultado final
        result = {
            "topic": topic,
            "final_content": current_draft,
            "plan": plan_result.content,
            "research": research_result.content,
            "critic_history": critic_history,
            "final_score": critic_history[-1]['score'],
            "iterations_used": iteration - 1,
            "max_iterations": self.max_iterations,
            "approved": final_approved,
            "llm_calls": self.llm.call_count,
            "execution_time_seconds": (end_time - start_time).total_seconds(),
            "provider_info": {
                "type": self.llm.provider_type,
                "model": self.llm.model_name
            },
            "timestamp": datetime.now().isoformat()
        }
        
        self.execution_log.append(result)
        return result
    
    def _extract_score(self, critic_content: str) -> float:
        """Extrai score numérico da avaliação crítica"""
        import re
        
        # Procura por padrões como "7.8/10", "Pontuação: 8.5"
        patterns = [
            r'Pontuação Geral[:\s]+(\d+\.?\d*)[/\s]?10',
            r'Score[:\s]+(\d+\.?\d*)[/\s]?10',
            r'(\d+\.?\d*)/10'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, critic_content, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except:
                    continue
        
        # Fallback: procura por "APROVADO" vs "REQUER REVISÃO"
        if "APROVADO" in critic_content.upper() and "REQUER REVISÃO" not in critic_content.upper():
            return 8.5
        elif "APROVADO COM REVISÕES" in critic_content.upper():
            return 7.0
        else:
            return 6.0
    
    def save_result(self, result: Dict, filename: Optional[str] = None) -> str:
        """Salva resultado em arquivo JSON"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"autonowrite_{timestamp}.json"
        
        os.makedirs("results", exist_ok=True)
        filepath = os.path.join("results", filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Resultado salvo em: {filepath}")
        return filepath


class ExperimentRunner:
    """Execução de experimentos para TCC"""
    
    def __init__(self, system: AutonoWriteSystem):
        self.system = system
    
    def run_comparative_experiment(self, topics: List[str], iterations_list: List[int] = [1, 2, 3]) -> Dict:
        """Executa experimento comparativo"""
        
        experiment_id = f"exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        results = {
            "experiment_id": experiment_id,
            "topics": topics,
            "configurations": [],
            "start_time": datetime.now().isoformat()
        }
        
        print(f"\n🧪 Experimento Comparativo: {experiment_id}")
        print(f"📋 Tópicos: {len(topics)} | Configurações: {iterations_list}")
        
        for max_iter in iterations_list:
            print(f"\n--- Configuração: {max_iter} iteração(ões) ---")
            
            config_results = []
            total_calls_before = self.system.llm.call_count
            
            for i, topic in enumerate(topics, 1):
                print(f"\n🔬 Teste {i}/{len(topics)}: {topic[:50]}...")
                
                calls_before = self.system.llm.call_count
                result = self.system.generate_content(topic, max_iter)
                calls_used = self.system.llm.call_count - calls_before
                
                test_result = {
                    "topic": topic,
                    "final_score": result["final_score"],
                    "iterations_used": result["iterations_used"],
                    "execution_time": result["execution_time_seconds"],
                    "llm_calls": calls_used,
                    "approved": result["approved"],
                    "content_length": len(result["final_content"])
                }
                
                config_results.append(test_result)
                print(f"   ✅ Score: {result['final_score']:.1f} | Tempo: {result['execution_time_seconds']:.1f}s")
            
            # Estatísticas da configuração
            avg_score = sum(r["final_score"] for r in config_results) / len(config_results)
            avg_time = sum(r["execution_time"] for r in config_results) / len(config_results)
            total_calls = self.system.llm.call_count - total_calls_before
            
            config_summary = {
                "max_iterations": max_iter,
                "results": config_results,
                "statistics": {
                    "avg_score": round(avg_score, 2),
                    "avg_time": round(avg_time, 2),
                    "total_llm_calls": total_calls,
                    "approval_rate": sum(1 for r in config_results if r["approved"]) / len(config_results)
                }
            }
            
            results["configurations"].append(config_summary)
            print(f"📊 Resumo: Score médio {avg_score:.1f} | Tempo médio {avg_time:.1f}s | Aprovação {config_summary['statistics']['approval_rate']:.1%}")
        
        results["end_time"] = datetime.now().isoformat()
        results["summary"] = self._generate_summary(results)
        
        # Salva experimento
        self.save_experiment(results)
        return results
    
    def _generate_summary(self, results: Dict) -> Dict:
        """Gera sumário estatístico"""
        configs = results["configurations"]
        
        best_quality = max(configs, key=lambda x: x["statistics"]["avg_score"])
        fastest = min(configs, key=lambda x: x["statistics"]["avg_time"])
        most_efficient = max(configs, key=lambda x: x["statistics"]["avg_score"] / x["statistics"]["avg_time"])
        
        scores = [c["statistics"]["avg_score"] for c in configs]
        quality_improvement = ((max(scores) - min(scores)) / min(scores)) * 100
        
        return {
            "best_quality_config": {
                "iterations": best_quality["max_iterations"],
                "avg_score": best_quality["statistics"]["avg_score"],
                "avg_time": best_quality["statistics"]["avg_time"]
            },
            "fastest_config": {
                "iterations": fastest["max_iterations"],
                "avg_score": fastest["statistics"]["avg_score"],
                "avg_time": fastest["statistics"]["avg_time"]
            },
            "most_efficient_config": {
                "iterations": most_efficient["max_iterations"],
                "avg_score": most_efficient["statistics"]["avg_score"],
                "avg_time": most_efficient["statistics"]["avg_time"],
                "efficiency_ratio": most_efficient["statistics"]["avg_score"] / most_efficient["statistics"]["avg_time"]
            },
            "quality_improvement_percent": round(quality_improvement, 1),
            "total_llm_calls": sum(c["statistics"]["total_llm_calls"] for c in configs),
            "recommendations": self._generate_recommendations(configs)
        }
    
    def _generate_recommendations(self, configs: List[Dict]) -> List[str]:
        """Gera recomendações baseadas nos resultados"""
        recommendations = []
        
        scores = [(c["max_iterations"], c["statistics"]["avg_score"]) for c in configs]
        scores.sort()
        
        # Analisa se há melhoria significativa
        if len(scores) > 1:
            improvement_1_to_2 = scores[1][1] - scores[0][1] if len(scores) > 1 else 0
            improvement_2_to_3 = scores[2][1] - scores[1][1] if len(scores) > 2 else 0
            
            if improvement_1_to_2 > 0.5:
                recommendations.append("Iteração adicional produz melhoria significativa na qualidade")
            
            if len(scores) > 2 and improvement_2_to_3 < improvement_1_to_2 * 0.5:
                recommendations.append("Retornos decrescentes observados após 2 iterações")
            
            best_score_config = max(configs, key=lambda x: x["statistics"]["avg_score"])
            if best_score_config["statistics"]["avg_score"] >= 8.0:
                recommendations.append(f"Configuração de {best_score_config['max_iterations']} iterações atinge qualidade excelente")
        
        # Analisa eficiência
        fastest = min(configs, key=lambda x: x["statistics"]["avg_time"])
        if fastest["statistics"]["avg_score"] >= 7.0:
            recommendations.append(f"Para uso rápido: {fastest['max_iterations']} iteração(ões) oferece boa qualidade em {fastest['statistics']['avg_time']:.1f}s")
        
        return recommendations
    
    def save_experiment(self, experiment: Dict, filename: str = None):
        """Salva experimento"""
        if filename is None:
            filename = f"experiment_{experiment['experiment_id']}.json"
        
        os.makedirs("experiments", exist_ok=True)
        filepath = os.path.join("experiments", filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(experiment, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Experimento salvo: {filepath}")
        return filepath
    
    def generate_tcc_report(self, experiment: Dict) -> str:
        """Gera relatório para TCC"""
        summary = experiment["summary"]
        
        report = f"""# Relatório Experimental - AutonoWrite

## Configuração do Experimento
- **ID**: {experiment['experiment_id']}
- **Tópicos Testados**: {len(experiment['topics'])}
- **Configurações**: {[c['max_iterations'] for c in experiment['configurations']]} iterações
- **Total de Testes**: {sum(len(c['results']) for c in experiment['configurations'])}

## Resultados Principais

### Melhor Qualidade
- **Configuração**: {summary['best_quality_config']['iterations']} iteração(ões)
- **Score Médio**: {summary['best_quality_config']['avg_score']}/10
- **Tempo Médio**: {summary['best_quality_config']['avg_time']:.1f}s

### Mais Rápida
- **Configuração**: {summary['fastest_config']['iterations']} iteração(ões)
- **Score Médio**: {summary['fastest_config']['avg_score']}/10
- **Tempo Médio**: {summary['fastest_config']['avg_time']:.1f}s

### Mais Eficiente (Qualidade/Tempo)
- **Configuração**: {summary['most_efficient_config']['iterations']} iteração(ões)
- **Razão Eficiência**: {summary['most_efficient_config']['efficiency_ratio']:.2f}

## Análises Estatísticas

### Melhoria de Qualidade
- **Melhoria Total**: {summary['quality_improvement_percent']}%
- **Chamadas LLM Totais**: {summary['total_llm_calls']}

## Resultados Detalhados por Configuração
"""
        
        for config in experiment['configurations']:
            stats = config['statistics']
            report += f"""
### {config['max_iterations']} Iteração(ões)
- **Score Médio**: {stats['avg_score']}/10
- **Tempo Médio**: {stats['avg_time']:.1f}s
- **Taxa de Aprovação**: {stats['approval_rate']:.1%}
- **Chamadas LLM**: {stats['total_llm_calls']}

**Tópicos Testados**: {len(config['results'])}
"""
            
            for result in config['results']:
                report += f"- {result['topic'][:60]}... (Score: {result['final_score']:.1f})\n"
        
        report += f"""
## Recomendações

{chr(10).join(f"- {rec}" for rec in summary['recommendations'])}

## Conclusões para o TCC

1. **Validação do Conceito**: O sistema multiagente com ciclo crítico demonstra melhoria mensurável de qualidade
2. **Eficácia das Iterações**: Iterações adicionais produzem melhorias até um ponto ótimo
3. **Aplicabilidade Prática**: Sistema viável para produção de conteúdo automatizado de qualidade

---
*Relatório gerado automaticamente em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        return report


def main():
    """Função principal - interface de linha de comando"""
    
    print("=" * 60)
    print("🤖 AutonoWrite - Sistema Multiagente para Geração de Conteúdo")
    print("=" * 60)
    
    # Configuração do LLM
    print("\n🔧 Configurando sistema...")
    try:
        llm = LLMProvider("auto")
        system = AutonoWriteSystem(llm)
        print("✅ Sistema configurado com sucesso!")
    except Exception as e:
        print(f"❌ Erro na configuração: {e}")
        print("💡 Dica: Configure GROQ_API_KEY no arquivo .env ou use simulação")
        return
    
    # Menu principal
    while True:
        print("\n" + "=" * 40)
        print("MENU PRINCIPAL")
        print("=" * 40)
        print("1. 📝 Gerar conteúdo único")
        print("2. 🧪 Executar experimento comparativo")
        print("3. 📊 Ver histórico de execuções") 
        print("4. ⚙️ Configurações")
        print("5. 🚪 Sair")
        
        choice = input("\nEscolha uma opção (1-5): ").strip()
        
        if choice == "1":
            generate_single_content(system)
        elif choice == "2":
            run_experiment_menu(system)
        elif choice == "3":
            show_history(system)
        elif choice == "4":
            show_config_menu(system)
        elif choice == "5":
            print("\n👋 Obrigado por usar o AutonoWrite!")
            break
        else:
            print("❌ Opção inválida. Tente novamente.")


def generate_single_content(system: AutonoWriteSystem):
    """Gera conteúdo único"""
    print("\n📝 GERAÇÃO DE CONTEÚDO ÚNICO")
    print("-" * 30)
    
    # Input do tópico
    topic = input("Digite o tópico: ").strip()
    if not topic:
        print("❌ Tópico não pode estar vazio")
        return
    
    # Configuração de iterações
    max_iter = input(f"Máximo de iterações (atual: {system.max_iterations}): ").strip()
    if max_iter.isdigit():
        max_iter = int(max_iter)
    else:
        max_iter = system.max_iterations
    
    # Execução
    try:
        result = system.generate_content(topic, max_iter)
        
        # Resultados
        print("\n" + "=" * 50)
        print("📊 RESULTADOS")
        print("=" * 50)
        print(f"Tópico: {result['topic']}")
        print(f"Score Final: {result['final_score']:.1f}/10")
        print(f"Iterações: {result['iterations_used']}/{result['max_iterations']}")
        print(f"Status: {'✅ APROVADO' if result['approved'] else '⚠️ NÃO APROVADO'}")
        print(f"Tempo: {result['execution_time_seconds']:.1f}s")
        print(f"Chamadas LLM: {result['llm_calls']}")
        
        # Salvar resultado
        save = input("\nSalvar resultado? (s/N): ").strip().lower()
        if save in ['s', 'sim', 'y', 'yes']:
            filepath = system.save_result(result)
            
            # Mostrar conteúdo
            show_content = input("Mostrar conteúdo gerado? (s/N): ").strip().lower()
            if show_content in ['s', 'sim', 'y', 'yes']:
                print("\n" + "=" * 50)
                print("📄 CONTEÚDO GERADO")
                print("=" * 50)
                print(result['final_content'])
                print("=" * 50)
    
    except Exception as e:
        print(f"❌ Erro durante execução: {e}")


def run_experiment_menu(system: AutonoWriteSystem):
    """Menu de experimentos"""
    print("\n🧪 EXPERIMENTOS COMPARATIVOS")
    print("-" * 30)
    
    # Tópicos predefinidos para TCC
    default_topics = [
        "Sistemas Multiagente em Inteligência Artificial",
        "Engenharia de Prompt para Modelos de Linguagem",
        "Ciclos de Crítica e Refinamento em IA Generativa",
        "Framework CrewAI para Automação de Tarefas",
        "Avaliação de Qualidade em Geração Automática de Texto"
    ]
    
    print("Opções:")
    print("1. Usar tópicos padrão (recomendado para TCC)")
    print("2. Definir tópicos customizados")
    
    choice = input("Escolha (1-2): ").strip()
    
    if choice == "1":
        topics = default_topics
        print(f"✅ Usando {len(topics)} tópicos padrão")
    elif choice == "2":
        topics = []
        print("Digite os tópicos (Enter vazio para finalizar):")
        while True:
            topic = input(f"Tópico {len(topics)+1}: ").strip()
            if not topic:
                break
            topics.append(topic)
        
        if not topics:
            print("❌ Nenhum tópico definido")
            return
    else:
        print("❌ Opção inválida")
        return
    
    # Configurações do experimento
    iterations_input = input("Configurações de iterações (ex: 1,2,3): ").strip()
    if iterations_input:
        try:
            iterations_list = [int(x.strip()) for x in iterations_input.split(',')]
        except:
            iterations_list = [1, 2, 3]
    else:
        iterations_list = [1, 2, 3]
    
    print(f"🔧 Configurações:")
    print(f"   - Tópicos: {len(topics)}")
    print(f"   - Iterações: {iterations_list}")
    print(f"   - Total de testes: {len(topics) * len(iterations_list)}")
    
    confirm = input("\nExecutar experimento? (s/N): ").strip().lower()
    if confirm not in ['s', 'sim', 'y', 'yes']:
        return
    
    # Execução do experimento
    try:
        runner = ExperimentRunner(system)
        result = runner.run_comparative_experiment(topics, iterations_list)
        
        # Gerar e salvar relatório
        report = runner.generate_tcc_report(result)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"relatorio_tcc_{timestamp}.md"
        
        os.makedirs("reports", exist_ok=True)
        report_path = os.path.join("reports", report_file)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n📊 Experimento concluído!")
        print(f"📄 Relatório salvo: {report_path}")
        
        # Mostrar sumário
        summary = result["summary"]
        print(f"\n🎯 RESUMO EXECUTIVO:")
        print(f"   - Melhor qualidade: {summary['best_quality_config']['iterations']} iter (Score: {summary['best_quality_config']['avg_score']:.1f})")
        print(f"   - Mais rápido: {summary['fastest_config']['iterations']} iter ({summary['fastest_config']['avg_time']:.1f}s)")
        print(f"   - Melhoria total: {summary['quality_improvement_percent']}%")
        
    except Exception as e:
        print(f"❌ Erro no experimento: {e}")


def show_history(system: AutonoWriteSystem):
    """Mostra histórico de execuções"""
    if not system.execution_log:
        print("\n📋 Nenhuma execução no histórico atual")
        return
    
    print(f"\n📋 HISTÓRICO ({len(system.execution_log)} execuções)")
    print("-" * 50)
    
    for i, result in enumerate(system.execution_log, 1):
        print(f"{i}. {result['topic'][:40]}...")
        print(f"   Score: {result['final_score']:.1f} | Iter: {result['iterations_used']} | Tempo: {result['execution_time_seconds']:.1f}s")
        print()


def show_config_menu(system: AutonoWriteSystem):
    """Menu de configurações"""
    print(f"\n⚙️ CONFIGURAÇÕES ATUAIS")
    print("-" * 30)
    print(f"Provider: {system.llm.provider_type}")
    print(f"Modelo: {system.llm.model_name}")
    print(f"Max Iterações: {system.max_iterations}")
    print(f"Score Mínimo: {system.min_quality_score}")
    print(f"Chamadas LLM: {system.llm.call_count}")
    
    print(f"\nOpções:")
    print(f"1. Alterar máximo de iterações")
    print(f"2. Alterar score mínimo")
    print(f"3. Resetar contador de chamadas")
    print(f"4. Voltar")
    
    choice = input("Escolha (1-4): ").strip()
    
    if choice == "1":
        new_max = input(f"Novo máximo de iterações (atual: {system.max_iterations}): ").strip()
        if new_max.isdigit() and int(new_max) > 0:
            system.max_iterations = int(new_max)
            print(f"✅ Máximo de iterações alterado para {system.max_iterations}")
        else:
            print("❌ Valor inválido")
    
    elif choice == "2":
        new_score = input(f"Novo score mínimo (atual: {system.min_quality_score}): ").strip()
        try:
            score = float(new_score)
            if 0 <= score <= 10:
                system.min_quality_score = score
                print(f"✅ Score mínimo alterado para {system.min_quality_score}")
            else:
                print("❌ Score deve estar entre 0 e 10")
        except:
            print("❌ Valor inválido")
    
    elif choice == "3":
        system.llm.call_count = 0
        print("✅ Contador resetado")


if __name__ == "__main__":
    main()