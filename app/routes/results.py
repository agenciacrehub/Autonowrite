from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash, make_response
from flask_login import login_required, current_user
from app import db
from app.models.project import Project
from app.models.execution import Execution, ExecutionStatus
import json
from datetime import datetime

bp = Blueprint('results', __name__)

@bp.route('/<int:project_id>/results')
@login_required
def view_results(project_id):
    """View results for a specific project"""
    project = Project.query.get_or_404(project_id)
    
    # Ensure the current user owns the project
    if project.user_id != current_user.id and not current_user.is_admin:
        flash('Você não tem permissão para acessar este projeto.', 'danger')
        return redirect(url_for('main.index'))
    
    # Check if project has generated content
    if not project.content or not project.content.get('generated_content'):
        flash('Nenhum resultado disponível para este projeto.', 'info')
        return redirect(url_for('projects.view_project', project_id=project_id))
    
    # Get the latest completed execution
    execution = Execution.query.filter_by(
        project_id=project_id,
        status=ExecutionStatus.COMPLETED
    ).order_by(Execution.completed_at.desc()).first()
    
    # Get all executions for the project
    executions = Execution.query.filter_by(project_id=project_id).order_by(Execution.started_at.desc()).all()
    
    return render_template('results/view.html',
                         project=project,
                         execution=execution,
                         executions=executions)

@bp.route('/<int:project_id>/results/export')
@login_required
def export_results(project_id):
    """Export results in various formats"""
    project = Project.query.get_or_404(project_id)
    
    # Ensure the current user owns the project
    if project.user_id != current_user.id and not current_user.is_admin:
        flash('Você não tem permissão para exportar este projeto.', 'danger')
        return redirect(url_for('main.index'))
    
    # Check if project has generated content
    if not project.content or not project.content.get('generated_content'):
        flash('Nenhum resultado disponível para exportação.', 'warning')
        return redirect(url_for('projects.view_project', project_id=project_id))
    
    format_type = request.args.get('format', 'json')
    generated_content = project.content.get('generated_content', {})
    
    # Get the latest completed execution for metadata
    execution = Execution.query.filter_by(
        project_id=project_id,
        status=ExecutionStatus.COMPLETED
    ).order_by(Execution.completed_at.desc()).first()
    
    # Prepare data for export
    export_data = {
        'project': {
            'id': project.id,
            'title': project.title,
            'description': project.description,
            'created_at': project.created_at.isoformat() if project.created_at else None,
            'updated_at': project.updated_at.isoformat() if project.updated_at else None,
            'settings': project.content
        },
        'execution': {
            'id': execution.id if execution else None,
            'started_at': execution.started_at.isoformat() if execution and execution.started_at else None,
            'completed_at': execution.completed_at.isoformat() if execution and execution.completed_at else None,
            'status': execution.status.value if execution else None,
        } if execution else None,
        'generated_content': generated_content,
        'generation_timestamp': project.content.get('generation_timestamp'),
        'final_score': generated_content.get('final_score', 0),
        'iterations_used': generated_content.get('iterations_used', 0)
    }
    
    # Handle different export formats
    if format_type == 'json':
        response = make_response(json.dumps(export_data, indent=2, ensure_ascii=False))
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename=results_{project.id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        return response
        
    elif format_type == 'markdown':
        # Generate markdown content
        final_content = generated_content.get('final_content', '')
        
        markdown_content = f"""# {project.title}

## Informações do Projeto
- **ID**: {project.id}
- **Criado em**: {project.created_at.strftime('%d/%m/%Y %H:%M') if project.created_at else 'N/A'}
- **Domínio**: {project.content.get('knowledge_domain', 'Não especificado')}
- **Público-alvo**: {project.content.get('target_audience', 'Não especificado')}
- **Tipo de Conteúdo**: {project.content.get('content_type', 'Não especificado')}

## Resultados da Geração
- **Score Final**: {generated_content.get('final_score', 0):.1f}/10
- **Iterações Utilizadas**: {generated_content.get('iterations_used', 0)}
- **Gerado em**: {project.content.get('generation_timestamp', 'N/A')}

## Conteúdo Gerado

{final_content}

---
*Gerado pelo AutonoWrite - Sistema de Geração de Conteúdo com IA*
"""
        
        response = make_response(markdown_content)
        response.headers['Content-Type'] = 'text/markdown; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename=content_{project.id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
        return response
        
    elif format_type == 'txt':
        # Generate plain text content
        final_content = generated_content.get('final_content', '')
        
        # Strip HTML tags for plain text
        import re
        clean_content = re.sub('<[^<]+?>', '', final_content)
        clean_content = re.sub(r'\n\s*\n', '\n\n', clean_content)
        
        text_content = f"""{project.title}

Informações do Projeto:
- ID: {project.id}
- Criado em: {project.created_at.strftime('%d/%m/%Y %H:%M') if project.created_at else 'N/A'}
- Domínio: {project.content.get('knowledge_domain', 'Não especificado')}
- Público-alvo: {project.content.get('target_audience', 'Não especificado')}
- Tipo de Conteúdo: {project.content.get('content_type', 'Não especificado')}

Resultados da Geração:
- Score Final: {generated_content.get('final_score', 0):.1f}/10
- Iterações Utilizadas: {generated_content.get('iterations_used', 0)}
- Gerado em: {project.content.get('generation_timestamp', 'N/A')}

Conteúdo Gerado:

{clean_content}

---
Gerado pelo AutonoWrite - Sistema de Geração de Conteúdo com IA
"""
        
        response = make_response(text_content)
        response.headers['Content-Type'] = 'text/plain; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename=content_{project.id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        return response
        
    else:
        flash('Formato de exportação não suportado.', 'error')
        return redirect(url_for('results.view_results', project_id=project_id))
