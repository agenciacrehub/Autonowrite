"""Database models for AutonoWrite."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from .connection import Base

class Project(Base):
    """Project model for content generation."""
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)  # For future user authentication
    title = Column(String(255), nullable=False)
    status = Column(String(50), default='draft')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    structured_inputs = relationship("StructuredInput", back_populates="project", uselist=False)
    agent_executions = relationship("AgentExecution", back_populates="project")
    quality_evaluations = relationship("QualityEvaluation", back_populates="project")
    research_data = relationship("ResearchData", back_populates="project")

class StructuredInput(Base):
    """Structured input data for content generation."""
    __tablename__ = 'structured_inputs'
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    
    # Context
    domain = Column(String(255), nullable=False)
    target_audience = Column(String(255), nullable=False)
    
    # Objectives
    objectives = Column(JSON, nullable=False)
    
    # Scope
    scope = Column(JSON, nullable=False)
    
    # Sources
    sources_preference = Column(JSON, nullable=False)
    
    # Style
    style_requirements = Column(JSON, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="structured_inputs")

class AgentExecution(Base):
    """Log of agent executions."""
    __tablename__ = 'agent_executions'
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    agent_type = Column(String(50), nullable=False)  # planner, researcher, writer, critic
    iteration = Column(Integer, default=1)
    input_prompt = Column(Text, nullable=False)
    output_content = Column(Text, nullable=False)
    execution_time = Column(Float)  # in seconds
    tokens_used = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="agent_executions")

class QualityEvaluation(Base):
    """Quality evaluation of generated content."""
    __tablename__ = 'quality_evaluations'
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    iteration = Column(Integer, nullable=False)
    score = Column(Float, nullable=False)  # 0.0 to 10.0
    criteria_breakdown = Column(JSON)  # Detailed scores for different criteria
    approved = Column(Boolean, default=False)
    feedback = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="quality_evaluations")

class ResearchData(Base):
    """Research data collected during content generation."""
    __tablename__ = 'research_data'
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    search_query = Column(String(512), nullable=False)
    sources_found = Column(JSON)  # List of sources with metadata
    relevance_score = Column(Float)  # 0.0 to 1.0
    content_summary = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="research_data")
