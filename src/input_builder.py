"""
Módulo para construção de inputs estruturados via linha de comando.
"""
from typing import Dict, Any, List, Optional
from enum import Enum
from .structured_inputs import (
    ContentRequest, ContextInput, ObjectiveInput, 
    ScopeInput, SourceInput, StyleInput,
    TechnicalLevel, WritingTone
)

class InputBuilder:
    """Classe para auxiliar na construção de inputs estruturados."""
    
    @classmethod
    def build_content_request(cls) -> ContentRequest:
        """Constrói uma solicitação de conteúdo completa."""
        print("\n=== CONSTRUTOR DE CONTEÚDO ESTRUTURADO ===\n")
        
        # Contexto
        print("1. CONTEXTO E DOMÍNIO")
        context = ContextInput(
            knowledge_domain=input("  - Área de conhecimento: ").strip(),
            target_audience=input("  - Público-alvo: ").strip(),
            technical_level=TechnicalLevel.ACADEMIC,
            key_concepts=cls._multi_input("  - Conceitos-chave (um por linha, vazio para terminar):")
        )
        
        # Objetivos
        print("\n2. OBJETIVOS")
        objectives = ObjectiveInput(
            main_purpose=input("  - Propósito principal: ").strip(),
            key_questions=cls._multi_input("  - Perguntas-chave (uma por linha, vazio para terminar):")
        )
        
        # Escopo
        print("\n3. ESCOPO")
        scope = ScopeInput(
            must_include=cls._multi_input("  - Deve incluir (um por linha, vazio para terminar):"),
            must_exclude=cls._multi_input("  - Deve excluir (um por linha, vazio para terminar):")
        )
        
        # Fontes
        print("\n4. FONTES")
        sources = SourceInput(
            preferred_sources=cls._multi_input("  - Fontes preferenciais (uma por linha, vazio para terminar):"),
            key_authors=cls._multi_input("  - Autores de referência (um por linha, vazio para terminar):")
        )
        
        # Estilo
        print("\n5. ESTILO")
        style = StyleInput(
            writing_tone=WritingTone.ACADEMIC,
            language="pt-BR"
        )
        
        return ContentRequest(
            context=context,
            objectives=objectives,
            scope=scope,
            sources=sources,
            style=style,
            metadata={"created_at": "auto"}
        )
    
    @staticmethod
    def _multi_input(prompt: str) -> List[str]:
        """Solicita múltiplas entradas até linha em branco."""
        print(prompt)
        items = []
        while True:
            item = input("  > ").strip()
            if not item:
                break
            items.append(item)
        return items
