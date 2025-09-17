"""
Background tasks for AI content generation using the multi-agent system
"""
import os
import sys
import json
from datetime import datetime
from typing import Dict, Any

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app import db, create_app
from app.models.project import Project
from app.models.execution import Execution, ExecutionStatus
from celery import Celery

# Initialize Celery
celery = Celery('autonowrite')

@celery.task(bind=True)
def start_content_generation(self, execution_id: int, project_id: int):
    """
    Background task to generate content using the multi-agent AI system
    """
    app = create_app()
    
    with app.app_context():
        try:
            # Get execution and project
            execution = Execution.query.get(execution_id)
            project = Project.query.get(project_id)
            
            if not execution or not project:
                raise ValueError("Execution or project not found")
            
            # Update execution status
            execution.status = ExecutionStatus.RUNNING
            execution.add_log("Iniciando geração de conteúdo com sistema multiagente", "INFO")
            db.session.commit()
            
            # Parse project content to get wizard data
            if isinstance(project.content, str):
                wizard_data = json.loads(project.content)
            else:
                wizard_data = project.content
            
            # Initialize the AI system
            from main import LLMProvider, AutonoWriteSystem
            
            # Choose provider based on environment and availability
            provider_env = os.getenv("LLM_PROVIDER", "auto").strip().lower()
            try:
                chosen = provider_env if provider_env in {"groq", "ollama", "simulation", "auto"} else "auto"
                llm_provider = LLMProvider(provider_type=chosen)
                execution.add_log(f"Provider selecionado: {llm_provider.provider_type}", "INFO")
            except Exception as e:
                llm_provider = LLMProvider(provider_type="simulation")
                execution.add_log(f"Falha ao inicializar provider '{provider_env}', usando simulação: {e}", "WARNING")
            
            ai_system = AutonoWriteSystem(llm_provider)
            
            # Build topic from wizard data
            topic = _build_topic_from_wizard_data(wizard_data)
            execution.add_log(f"Tópico construído: {topic}", "INFO")
            
            # Update progress
            execution.update_progress(0.1)
            db.session.commit()
            
            # Generate content using multi-agent system
            execution.add_log("Iniciando pipeline multiagente", "INFO")
            result = ai_system.generate_content(
                topic=topic,
                max_iterations=3
            )
            
            # Update progress
            execution.update_progress(0.8)
            db.session.commit()
            
            # Process and save results
            content_result = _process_generation_result(result, wizard_data)
            
            # Save generated content to project
            project.content.update({
                'generated_content': content_result,
                'generation_completed': True,
                'generation_timestamp': datetime.now().isoformat()
            })
            
            # Complete execution
            execution.status = ExecutionStatus.COMPLETED
            execution.update_progress(1.0)
            execution.result = content_result
            execution.add_log("Geração de conteúdo concluída com sucesso", "INFO")
            
            db.session.commit()
            
            return {
                'status': 'success',
                'execution_id': execution_id,
                'content_length': len(content_result.get('final_content', '')),
                'final_score': content_result.get('final_score', 0),
                'iterations_used': content_result.get('iterations_used', 0)
            }
            
        except Exception as e:
            # Handle errors
            with app.app_context():
                execution = Execution.query.get(execution_id)
                if execution:
                    execution.status = ExecutionStatus.FAILED
                    execution.add_log(f"Erro na geração: {str(e)}", "ERROR")
                    db.session.commit()
            
            raise self.retry(exc=e, countdown=60, max_retries=3)

def _build_topic_from_wizard_data(wizard_data: Dict[str, Any]) -> str:
    """
    Build a comprehensive topic description from wizard data
    """
    # Extract key information
    title = wizard_data.get('project_title', 'Projeto sem título')
    domain = wizard_data.get('knowledge_domain', '')
    audience = wizard_data.get('target_audience', '')
    purpose = wizard_data.get('main_purpose', '')
    technical_level = wizard_data.get('technical_level', '')
    
    # Build comprehensive topic
    topic_parts = [title]
    
    if domain:
        topic_parts.append(f"no domínio de {domain}")
    
    if audience:
        topic_parts.append(f"para {audience}")
    
    if technical_level:
        level_map = {
            'iniciante': 'nível iniciante',
            'intermediario': 'nível intermediário', 
            'avancado': 'nível avançado',
            'academico': 'nível acadêmico'
        }
        topic_parts.append(f"em {level_map.get(technical_level, technical_level)}")
    
    if purpose:
        topic_parts.append(f"com o objetivo de: {purpose}")
    
    return " ".join(topic_parts)

def _process_generation_result(ai_result: Dict[str, Any], wizard_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process the AI generation result and format for storage
    """
    return {
        'final_content': ai_result.get('final_content', ''),
        'plan': ai_result.get('plan', ''),
        'research': ai_result.get('research', ''),
        'final_score': ai_result.get('final_score', 0),
        'iterations_used': ai_result.get('iterations_used', 0),
        'approved': ai_result.get('approved', False),
        'llm_calls': ai_result.get('llm_calls', 0),
        'execution_time_seconds': ai_result.get('execution_time_seconds', 0),
        'provider_info': ai_result.get('provider_info', {}),
        'critic_history': ai_result.get('critic_history', []),
        'wizard_config': {
            'content_type': wizard_data.get('content_type', ''),
            'writing_style': wizard_data.get('writing_style', ''),
            'tone': wizard_data.get('tone', ''),
            'estimated_length': wizard_data.get('estimated_length', ''),
            'output_format': wizard_data.get('output_format', 'markdown')
        },
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'system_version': '1.0',
            'agent_system': 'AutonoWrite MultiAgent'
        }
    }

def start_content_generation_sync(execution_id: int, project_id: int):
    """
    Synchronous version of content generation for immediate execution
    """
    try:
        # Get execution and project
        from app import db
        from app.models.project import Project
        from app.models.execution import Execution, ExecutionStatus
        
        execution = Execution.query.get(execution_id)
        project = Project.query.get(project_id)
        
        if not execution or not project:
            return {'status': 'error', 'error': 'Execution or project not found'}
        
        # Update execution status
        execution.status = ExecutionStatus.RUNNING
        execution.add_log("Iniciando geração de conteúdo com sistema multiagente", "INFO")
        db.session.commit()
        
        # Parse project content to get wizard data
        if isinstance(project.content, str):
            wizard_data = json.loads(project.content)
        else:
            wizard_data = project.content
        
        # Initialize the AI system
        from main import LLMProvider, AutonoWriteSystem
        
        # Choose provider based on environment and availability
        provider_env = os.getenv("LLM_PROVIDER", "auto").strip().lower()
        try:
            chosen = provider_env if provider_env in {"groq", "ollama", "simulation", "auto"} else "auto"
            llm_provider = LLMProvider(provider_type=chosen)
            execution.add_log(f"Provider selecionado: {llm_provider.provider_type}", "INFO")
        except Exception as e:
            llm_provider = LLMProvider(provider_type="simulation")
            execution.add_log(f"Falha ao inicializar provider '{provider_env}', usando simulação: {e}", "WARNING")
        
        ai_system = AutonoWriteSystem(llm_provider)
        
        # Build topic from wizard data
        topic = _build_topic_from_wizard_data(wizard_data)
        execution.add_log(f"Tópico construído: {topic}", "INFO")
        
        # Update progress
        execution.update_progress(0.1)
        db.session.commit()
        
        # Generate content using multi-agent system
        execution.add_log("Iniciando pipeline multiagente", "INFO")
        result = ai_system.generate_content(
            topic=topic,
            max_iterations=3
        )
        
        # Update progress
        execution.update_progress(0.8)
        db.session.commit()
        
        # Process and save results
        content_result = _process_generation_result(result, wizard_data)
        
        # Save generated content to project
        if not isinstance(project.content, dict):
            project.content = {}
        
        project.content.update({
            'generated_content': content_result,
            'generation_completed': True,
            'generation_timestamp': datetime.now().isoformat()
        })
        
        # Mark the project content as modified for SQLAlchemy
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(project, 'content')
        
        # Complete execution
        execution.status = ExecutionStatus.COMPLETED
        execution.update_progress(1.0)
        execution.result = content_result
        execution.add_log("Geração de conteúdo concluída com sucesso", "INFO")
        
        db.session.commit()
        
        return {
            'status': 'success',
            'execution_id': execution_id,
            'content_length': len(content_result.get('final_content', '')),
            'final_score': content_result.get('final_score', 0),
            'iterations_used': content_result.get('iterations_used', 0)
        }
        
    except Exception as e:
        # Handle errors
        try:
            execution = Execution.query.get(execution_id)
            if execution:
                execution.status = ExecutionStatus.FAILED
                execution.add_log(f"Erro na geração: {str(e)}", "ERROR")
                db.session.commit()
        except:
            pass
        
        return {'status': 'error', 'error': str(e)}

@celery.task
def cleanup_old_executions():
    """
    Cleanup task to remove old execution logs
    """
    app = create_app()
    
    with app.app_context():
        # Implementation for cleanup
        pass
