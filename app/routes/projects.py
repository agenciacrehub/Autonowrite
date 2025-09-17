from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_file
from flask_login import login_required, current_user
from app import db
from app.models.project import Project
from app.models.execution import Execution, ExecutionStatus
from app.forms.project import ProjectForm, ProjectSettingsForm
from datetime import datetime, timedelta
import os
import json
from io import BytesIO
from zipfile import ZipFile

bp = Blueprint('projects', __name__)

@bp.route('/list')
@login_required
def list_projects():
    """Lista todos os projetos do usuário"""
    # Filtros
    status = request.args.get('status')
    search = request.args.get('search', '')
    
    query = Project.query.filter_by(user_id=current_user.id)
    
    if status and status != 'all':
        query = query.filter_by(status=status)
    
    if search:
        search = f"%{search}%"
        query = query.filter(Project.title.ilike(search) | Project.description.ilike(search))
    
    # Ordenação
    sort = request.args.get('sort', 'updated')
    order = request.args.get('order', 'desc')
    
    if sort == 'title':
        query = query.order_by(Project.title.asc() if order == 'asc' else Project.title.desc())
    elif sort == 'created':
        query = query.order_by(Project.created_at.asc() if order == 'asc' else Project.created_at.desc())
    else:  # updated
        query = query.order_by(Project.updated_at.asc() if order == 'asc' else Project.updated_at.desc())
    
    # Paginação
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    projects = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('projects/list.html', 
                         projects=projects,
                         status=status,
                         search=search,
                         sort=sort,
                         order=order)

@bp.route('/projects/<int:project_id>')
@login_required
def view_project(project_id):
    """Visualiza um projeto específico"""
    project = Project.query.get_or_404(project_id)
    
    # Verifica se o usuário tem permissão
    if project.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    # Obtém as execuções mais recentes
    recent_executions = Execution.query.filter_by(project_id=project_id)\
                                     .order_by(Execution.started_at.desc())\
                                     .limit(5).all()
    
    # Check if prompt is completed and parse content
    prompt_completed = False
    content_data = {}
    if project.content:
        try:
            if isinstance(project.content, str):
                content_data = json.loads(project.content)
            else:
                content_data = project.content
            
            if isinstance(content_data, dict):
                prompt_completed = content_data.get('prompt_completed', False)
        except Exception as e:
            current_app.logger.error(f"Error parsing project content: {str(e)}")
            content_data = {}
            prompt_completed = False
    
    return render_template('projects/view.html', 
                         project=project,
                         content_data=content_data,
                         recent_executions=recent_executions,
                         prompt_completed=prompt_completed)

@bp.route('/projects/new', methods=['GET', 'POST'])
@login_required
def new_project():
    """Cria um novo projeto"""
    form = ProjectForm()
    
    if form.validate_on_submit():
        project = Project(
            title=form.title.data,
            description=form.description.data,
            status='draft',
            user_id=current_user.id,
            settings={
                'language': form.language.data,
                'visibility': form.visibility.data
            }
        )
        
        db.session.add(project)
        db.session.commit()
        
        flash('Projeto criado com sucesso! Agora configure os detalhes no assistente.', 'success')
        return redirect(url_for('wizard.new_project', project_id=project.id))
    
    return render_template('projects/edit.html', 
                         title='Novo Projeto',
                         form=form)


@bp.route('/projects/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    """Edita um projeto existente"""
    project = Project.query.get_or_404(project_id)
    
    # Verifica se o usuário tem permissão
    if project.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    form = ProjectForm(obj=project)
    
    if form.validate_on_submit():
        project.title = form.title.data
        project.description = form.description.data
        project.status = form.status.data
        project.updated_at = datetime.utcnow()
        
        # Atualiza as configurações
        if not project.settings:
            project.settings = {}
        
        project.settings.update({
            'language': form.language.data,
            'visibility': form.visibility.data
        })
        
        db.session.commit()
        
        flash('Projeto atualizado com sucesso!', 'success')
        return redirect(url_for('projects.view_project', project_id=project.id))
    
    # Preenche o formulário com os dados atuais
    form.status.data = project.status
    
    if project.settings:
        form.language.data = project.settings.get('language', 'pt-BR')
        form.visibility.data = project.settings.get('visibility', 'private')
    
    return render_template('projects/edit.html', 
                         title='Editar Projeto',
                         form=form,
                         project=project)

@bp.route('/projects/<int:project_id>/settings', methods=['GET', 'POST'])
@login_required
def project_settings(project_id):
    """Configurações avançadas do projeto"""
    project = Project.query.get_or_404(project_id)
    
    # Verifica se o usuário tem permissão
    if project.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    # Handle reset settings
    if request.method == 'POST' and 'reset_settings' in request.form:
        # Reset to default settings
        project.settings = {
            'advanced': {
                'auto_save': True,
                'notifications': True,
                'export_format': 'markdown',
                'api_access': False
            }
        }
        project.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Configurações redefinidas para os valores padrão!', 'success')
        return redirect(url_for('projects.project_settings', project_id=project.id))
    
    form = ProjectSettingsForm(obj=project)
    
    if form.validate_on_submit():
        # Atualiza as configurações
        if not project.settings:
            project.settings = {}
        
        project.settings.update({
            'advanced': {
                'auto_save': form.auto_save.data,
                'notifications': form.notifications.data,
                'export_format': form.export_format.data,
                'api_access': form.api_access.data
            }
        })
        
        project.updated_at = datetime.utcnow()
        db.session.commit()
        
        flash('Configurações atualizadas com sucesso!', 'success')
        return redirect(url_for('projects.project_settings', project_id=project.id))
    
    # Preenche o formulário com os dados atuais
    if project.settings and 'advanced' in project.settings:
        form.auto_save.data = project.settings['advanced'].get('auto_save', True)
        form.notifications.data = project.settings['advanced'].get('notifications', True)
        form.export_format.data = project.settings['advanced'].get('export_format', 'markdown')
        form.api_access.data = project.settings['advanced'].get('api_access', False)
    
    return render_template('projects/settings.html', 
                         title='Configurações do Projeto',
                         form=form,
                         project=project)

@bp.route('/projects/<int:project_id>/delete', methods=['POST'])
@login_required
def delete_project(project_id):
    """Exclui um projeto"""
    project = Project.query.get_or_404(project_id)
    
    # Verifica se o usuário tem permissão
    if project.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    # Remove todas as execuções e logs associados
    executions = Execution.query.filter_by(project_id=project_id).all()
    for execution in executions:
        db.session.delete(execution)
    
    # Remove o projeto
    db.session.delete(project)
    db.session.commit()
    
    flash('Projeto excluído com sucesso!', 'success')
    return redirect(url_for('projects.list_projects'))

@bp.route('/projects/<int:project_id>/export')
@login_required
def export_project(project_id):
    """Exporta um projeto para um arquivo ZIP"""
    project = Project.query.get_or_404(project_id)
    
    # Verifica se o usuário tem permissão
    if project.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    # Cria um arquivo ZIP em memória
    memory_file = BytesIO()
    
    with ZipFile(memory_file, 'w') as zf:
        # Adiciona os metadados do projeto
        project_data = {
            'title': project.title,
            'description': project.description,
            'status': project.status,
            'created_at': project.created_at.isoformat(),
            'updated_at': project.updated_at.isoformat(),
            'settings': project.settings,
            'content': project.content
        }
        
        zf.writestr('project.json', json.dumps(project_data, indent=2, default=str))
        
        # Adiciona os logs de execução
        executions = Execution.query.filter_by(project_id=project_id).all()
        for i, execution in enumerate(executions):
            execution_data = {
                'id': execution.id,
                'status': execution.status.value,
                'started_at': execution.started_at.isoformat() if execution.started_at else None,
                'completed_at': execution.completed_at.isoformat() if execution.completed_at else None,
                'progress': execution.progress,
                'metadata': execution.metadata_,
                'logs': [{
                    'timestamp': log.timestamp.isoformat(),
                    'level': log.level.value,
                    'message': log.message
                } for log in execution.logs]
            }
            
            zf.writestr(f'executions/execution_{i+1}.json', json.dumps(execution_data, indent=2, default=str))
    
    memory_file.seek(0)
    
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name=f'project_{project.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.zip'
    )

@bp.route('/projects/import', methods=['GET', 'POST'])
@login_required
def import_project():
    """Importa um projeto a partir de um arquivo ZIP"""
    if request.method == 'POST':
        if 'project_file' not in request.files:
            flash('Nenhum arquivo enviado', 'error')
            return redirect(request.url)
        
        file = request.files['project_file']
        
        if file.filename == '':
            flash('Nenhum arquivo selecionado', 'error')
            return redirect(request.url)
        
        if file and file.filename.endswith('.zip'):
            try:
                # Lê o arquivo ZIP
                with ZipFile(file) as zf:
                    # Verifica se o arquivo project.json existe
                    if 'project.json' not in zf.namelist():
                        flash('Arquivo de projeto inválido', 'error')
                        return redirect(request.url)
                    
                    # Lê os dados do projeto
                    with zf.open('project.json') as f:
                        project_data = json.loads(f.read().decode('utf-8'))
                
                # Cria um novo projeto
                project = Project(
                    title=f"{project_data['title']} (Importado)",
                    description=project_data.get('description', ''),
                    status='draft',
                    user_id=current_user.id,
                    settings=project_data.get('settings', {}),
                    content=project_data.get('content', {})
                )
                
                db.session.add(project)
                db.session.commit()
                
                flash('Projeto importado com sucesso!', 'success')
                return redirect(url_for('projects.view_project', project_id=project.id))
                
            except Exception as e:
                db.session.rollback()
                flash(f'Erro ao importar projeto: {str(e)}', 'error')
                return redirect(request.url)
        else:
            flash('Formato de arquivo inválido. Use um arquivo ZIP.', 'error')
            return redirect(request.url)
    
    return render_template('projects/import.html', title='Importar Projeto')

@bp.route('/api/projects/<int:project_id>/stats')
@login_required
def project_stats(project_id):
    """Retorna estatísticas do projeto"""
    project = Project.query.get_or_404(project_id)
    
    # Verifica se o usuário tem permissão
    if project.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    # Conta as execuções por status
    executions = db.session.query(
        Execution.status,
        db.func.count(Execution.id).label('count')
    ).filter_by(project_id=project_id).group_by(Execution.status).all()
    
    # Calcula o tempo médio de execução
    avg_duration = db.session.query(
        db.func.avg(
            db.func.extract('epoch', Execution.completed_at - Execution.started_at)
        )
    ).filter(
        Execution.project_id == project_id,
        Execution.status == 'completed',
        Execution.completed_at.isnot(None),
        Execution.started_at.isnot(None)
    ).scalar() or 0
    
    # Últimas execuções
    recent_executions = Execution.query.filter_by(project_id=project_id)\
                                     .order_by(Execution.started_at.desc())\
                                     .limit(5).all()
    
    return jsonify({
        'project_id': project_id,
        'executions': {
            'total': sum(e.count for e in executions),
            'by_status': {e.status.value: e.count for e in executions}
        },
        'average_duration': round(float(avg_duration), 2),
        'last_updated': project.updated_at.isoformat(),
        'recent_executions': [{
            'id': e.id,
            'status': e.status.value,
            'started_at': e.started_at.isoformat(),
            'duration': (e.completed_at - e.started_at).total_seconds() if e.completed_at and e.started_at else None
        } for e in recent_executions]
    })
