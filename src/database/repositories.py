"""Database repository for CRUD operations."""
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from . import models
from datetime import datetime

class ProjectRepository:
    """Repository for project operations."""
    
    @staticmethod
    def create_project(db: Session, title: str, user_id: Optional[int] = None) -> models.Project:
        """Create a new project."""
        db_project = models.Project(
            title=title,
            user_id=user_id,
            status='draft'
        )
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        return db_project

    @staticmethod
    def get_project(db: Session, project_id: int) -> Optional[models.Project]:
        """Get a project by ID."""
        return db.query(models.Project).filter(models.Project.id == project_id).first()

class StructuredInputRepository:
    """Repository for structured input operations."""
    
    @staticmethod
    def create_structured_input(
        db: Session, 
        project_id: int, 
        domain: str, 
        target_audience: str,
        objectives: Dict[str, Any],
        scope: Dict[str, Any],
        sources_preference: Dict[str, Any],
        style_requirements: Dict[str, Any]
    ) -> models.StructuredInput:
        """Create a new structured input."""
        db_input = models.StructuredInput(
            project_id=project_id,
            domain=domain,
            target_audience=target_audience,
            objectives=objectives,
            scope=scope,
            sources_preference=sources_preference,
            style_requirements=style_requirements
        )
        db.add(db_input)
        db.commit()
        db.refresh(db_input)
        return db_input

class AgentExecutionRepository:
    """Repository for agent execution logging."""
    
    @staticmethod
    def log_execution(
        db: Session,
        project_id: int,
        agent_type: str,
        input_prompt: str,
        output_content: str,
        execution_time: float,
        tokens_used: int,
        iteration: int = 1
    ) -> models.AgentExecution:
        """Log an agent execution."""
        execution = models.AgentExecution(
            project_id=project_id,
            agent_type=agent_type,
            iteration=iteration,
            input_prompt=input_prompt,
            output_content=output_content,
            execution_time=execution_time,
            tokens_used=tokens_used
        )
        db.add(execution)
        db.commit()
        db.refresh(execution)
        return execution

class QualityEvaluationRepository:
    """Repository for quality evaluations."""
    
    @staticmethod
    def add_evaluation(
        db: Session,
        project_id: int,
        iteration: int,
        score: float,
        criteria_breakdown: Dict[str, float],
        approved: bool,
        feedback: Optional[str] = None
    ) -> models.QualityEvaluation:
        """Add a quality evaluation."""
        evaluation = models.QualityEvaluation(
            project_id=project_id,
            iteration=iteration,
            score=score,
            criteria_breakdown=criteria_breakdown,
            approved=approved,
            feedback=feedback
        )
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)
        return evaluation

class ResearchDataRepository:
    """Repository for research data."""
    
    @staticmethod
    def add_research_data(
        db: Session,
        project_id: int,
        search_query: str,
        sources_found: List[Dict[str, Any]],
        relevance_score: Optional[float] = None,
        content_summary: Optional[str] = None
    ) -> models.ResearchData:
        """Add research data."""
        research_data = models.ResearchData(
            project_id=project_id,
            search_query=search_query,
            sources_found=sources_found,
            relevance_score=relevance_score,
            content_summary=content_summary
        )
        db.add(research_data)
        db.commit()
        db.refresh(research_data)
        return research_data
