"""
Módulo para definição de inputs estruturados para o sistema AutonoWrite.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any

class TechnicalLevel(str, Enum):
    BEGINNER = "iniciante"
    INTERMEDIATE = "intermediário"
    ADVANCED = "avançado"
    ACADEMIC = "acadêmico"

class WritingTone(str, Enum):
    FORMAL = "formal"
    INFORMAL = "informal"
    ACADEMIC = "acadêmico"
    TECHNICAL = "técnico"
    PERSUASIVE = "persuasivo"

@dataclass
class ContextInput:
    """Contexto e domínio do conteúdo a ser gerado"""
    knowledge_domain: str
    target_audience: str
    technical_level: TechnicalLevel
    background_info: Optional[str] = None
    key_concepts: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)

@dataclass
class ObjectiveInput:
    """Objetivos específicos do conteúdo"""
    main_purpose: str
    key_questions: List[str] = field(default_factory=list)
    expected_outcomes: List[str] = field(default_factory=list)
    success_metrics: List[str] = field(default_factory=list)

@dataclass
class ScopeInput:
    """Escopo e limitações do conteúdo"""
    must_include: List[str] = field(default_factory=list)
    must_exclude: List[str] = field(default_factory=list)
    word_count_target: Optional[int] = None
    depth_level: int = 2  # 1-5, sendo 5 o mais aprofundado
    time_period: Optional[str] = None

@dataclass
class SourceInput:
    """Fontes e evidências para embasar o conteúdo"""
    preferred_sources: List[str] = field(default_factory=list)
    time_period: Optional[str] = None
    key_authors: List[str] = field(default_factory=list)
    required_citations: bool = True
    min_sources: int = 3

@dataclass
class StyleInput:
    """Estilo e formatação do conteúdo"""
    writing_tone: WritingTone = WritingTone.ACADEMIC
    required_sections: List[str] = field(default_factory=list)
    formatting_guidelines: Dict[str, Any] = field(default_factory=dict)
    language: str = "pt-BR"
    examples: List[str] = field(default_factory=list)

@dataclass
class ContentRequest:
    """Estrutura principal para solicitação de conteúdo"""
    context: ContextInput
    objectives: ObjectiveInput
    scope: ScopeInput
    sources: SourceInput
    style: StyleInput
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def validate(self) -> bool:
        """Valida se a solicitação contém informações suficientes"""
        if not self.context.knowledge_domain:
            raise ValueError("Domínio de conhecimento é obrigatório")
        if not self.objectives.main_purpose:
            raise ValueError("Propósito principal é obrigatório")
        if not self.sources.preferred_sources and self.sources.required_citations:
            raise ValueError("Fontes são obrigatórias quando citações são necessárias")
        return True

    def to_dict(self) -> Dict[str, Any]:
        """Converte o objeto para dicionário"""
        return {
            "context": {
                "knowledge_domain": self.context.knowledge_domain,
                "target_audience": self.context.target_audience,
                "technical_level": self.context.technical_level.value,
                "background_info": self.context.background_info,
                "key_concepts": self.context.key_concepts,
                "assumptions": self.context.assumptions
            },
            "objectives": {
                "main_purpose": self.objectives.main_purpose,
                "key_questions": self.objectives.key_questions,
                "expected_outcomes": self.objectives.expected_outcomes,
                "success_metrics": self.objectives.success_metrics
            },
            "scope": {
                "must_include": self.scope.must_include,
                "must_exclude": self.scope.must_exclude,
                "word_count_target": self.scope.word_count_target,
                "depth_level": self.scope.depth_level,
                "time_period": self.scope.time_period
            },
            "sources": {
                "preferred_sources": self.sources.preferred_sources,
                "time_period": self.sources.time_period,
                "key_authors": self.sources.key_authors,
                "required_citations": self.sources.required_citations,
                "min_sources": self.sources.min_sources
            },
            "style": {
                "writing_tone": self.style.writing_tone.value,
                "required_sections": self.style.required_sections,
                "formatting_guidelines": self.style.formatting_guidelines,
                "language": self.style.language,
                "examples": self.style.examples
            },
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContentRequest':
        """Cria um ContentRequest a partir de um dicionário"""
        return cls(
            context=ContextInput(
                knowledge_domain=data["context"]["knowledge_domain"],
                target_audience=data["context"]["target_audience"],
                technical_level=TechnicalLevel(data["context"]["technical_level"]),
                background_info=data["context"].get("background_info"),
                key_concepts=data["context"].get("key_concepts", []),
                assumptions=data["context"].get("assumptions", [])
            ),
            objectives=ObjectiveInput(
                main_purpose=data["objectives"]["main_purpose"],
                key_questions=data["objectives"].get("key_questions", []),
                expected_outcomes=data["objectives"].get("expected_outcomes", []),
                success_metrics=data["objectives"].get("success_metrics", [])
            ),
            scope=ScopeInput(
                must_include=data["scope"].get("must_include", []),
                must_exclude=data["scope"].get("must_exclude", []),
                word_count_target=data["scope"].get("word_count_target"),
                depth_level=data["scope"].get("depth_level", 2),
                time_period=data["scope"].get("time_period")
            ),
            sources=SourceInput(
                preferred_sources=data["sources"].get("preferred_sources", []),
                time_period=data["sources"].get("time_period"),
                key_authors=data["sources"].get("key_authors", []),
                required_citations=data["sources"].get("required_citations", True),
                min_sources=data["sources"].get("min_sources", 3)
            ),
            style=StyleInput(
                writing_tone=WritingTone(data["style"].get("writing_tone", "acadêmico")),
                required_sections=data["style"].get("required_sections", []),
                formatting_guidelines=data["style"].get("formatting_guidelines", {}),
                language=data["style"].get("language", "pt-BR"),
                examples=data["style"].get("examples", [])
            ),
            metadata=data.get("metadata", {})
        )
