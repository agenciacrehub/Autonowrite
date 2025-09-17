"""Logging system for agent activities."""
import time
from datetime import datetime
from typing import Dict, Any, Optional
from . import repositories
from .connection import get_db
from contextlib import contextmanager

class AgentLogger:
    """Logger for agent activities."""
    
    def __init__(self, project_id: int):
        """Initialize logger for a specific project."""
        self.project_id = project_id
        self.start_time = None
        self.db = next(get_db())
    
    def start_timer(self):
        """Start the execution timer."""
        self.start_time = time.time()
    
    def log_execution(
        self,
        agent_type: str,
        input_prompt: str,
        output_content: str,
        tokens_used: int,
        iteration: int = 1
    ) -> int:
        """Log an agent execution.
        
        Args:
            agent_type: Type of agent (planner, researcher, writer, critic)
            input_prompt: The input prompt given to the agent
            output_content: The output content from the agent
            tokens_used: Number of tokens used in the operation
            iteration: Iteration number (default: 1)
            
        Returns:
            int: The ID of the created execution log
        """
        execution_time = time.time() - self.start_time if self.start_time else 0
        
        execution = repositories.AgentExecutionRepository.log_execution(
            db=self.db,
            project_id=self.project_id,
            agent_type=agent_type,
            input_prompt=input_prompt,
            output_content=output_content,
            execution_time=execution_time,
            tokens_used=tokens_used,
            iteration=iteration
        )
        
        # Reset timer
        self.start_timer()
        return execution.id
    
    def log_evaluation(
        self,
        iteration: int,
        score: float,
        criteria_breakdown: Dict[str, float],
        approved: bool,
        feedback: Optional[str] = None
    ) -> int:
        """Log a quality evaluation.
        
        Args:
            iteration: The iteration number
            score: Overall quality score (0.0-10.0)
            criteria_breakdown: Detailed scores for different criteria
            approved: Whether the content was approved
            feedback: Optional feedback text
            
        Returns:
            int: The ID of the created evaluation
        """
        evaluation = repositories.QualityEvaluationRepository.add_evaluation(
            db=self.db,
            project_id=self.project_id,
            iteration=iteration,
            score=score,
            criteria_breakdown=criteria_breakdown,
            approved=approved,
            feedback=feedback
        )
        return evaluation.id
    
    def log_research(
        self,
        search_query: str,
        sources_found: List[Dict[str, Any]],
        relevance_score: Optional[float] = None,
        content_summary: Optional[str] = None
    ) -> int:
        """Log research data.
        
        Args:
            search_query: The search query used
            sources_found: List of sources found with metadata
            relevance_score: Relevance score (0.0-1.0)
            content_summary: Summary of the research content
            
        Returns:
            int: The ID of the created research data entry
        """
        research = repositories.ResearchDataRepository.add_research_data(
            db=self.db,
            project_id=self.project_id,
            search_query=search_query,
            sources_found=sources_found,
            relevance_score=relevance_score,
            content_summary=content_summary
        )
        return research.id
    
    def update_project_status(self, status: str):
        """Update the project status."""
        project = repositories.ProjectRepository.get_project(self.db, self.project_id)
        if project:
            project.status = status
            self.db.commit()
            self.db.refresh(project)

@contextmanager
def log_execution(project_id: int, agent_type: str, iteration: int = 1):
    """Context manager for logging agent executions.
    
    Example:
        with log_execution(project_id=1, agent_type='researcher') as logger:
            # Your agent code here
            result = some_agent.run(prompt)
            logger.log_execution(
                agent_type='researcher',
                input_prompt=prompt,
                output_content=result,
                tokens_used=count_tokens(result)
            )
    """
    logger = AgentLogger(project_id)
    logger.start_timer()
    try:
        yield logger
    except Exception as e:
        # Log the error
        logger.log_execution(
            agent_type=agent_type,
            input_prompt="",
            output_content=f"Error: {str(e)}",
            tokens_used=0,
            iteration=iteration
        )
        raise
