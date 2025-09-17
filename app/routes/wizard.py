from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_required, current_user
from app.forms.wizard import *
from app.models.project import Project
from app import db
import json
from datetime import datetime

bp = Blueprint('wizard', __name__)

def get_form_class(step):
    """Return the appropriate form class for the current step"""
    form_classes = {
        1: WizardStep1Form,
        2: WizardStep2Form,
        3: WizardStep3Form,
        4: WizardStep4Form,
        5: WizardStep5Form,
        6: WizardReviewForm
    }
    return form_classes.get(step, WizardStep1Form)

def save_project(draft=False, project_id=None):
    """Save project to database and clear session"""
    try:
        wizard_data = session.get('wizard_data', {})
        
        # Mark prompt as completed if not saving as draft
        if not draft:
            wizard_data['prompt_completed'] = True
        
        if project_id:
            # Update existing project
            project = Project.query.get_or_404(project_id)
            project.content = json.dumps(wizard_data)
            project.is_draft = draft
            project.status = 'draft' if draft else 'pending'
            project.updated_at = datetime.utcnow()
        else:
            # Create new project
            project = Project(
                user_id=current_user.id,
                title=wizard_data.get('project_title', 'Novo Projeto'),
                content=json.dumps(wizard_data),
                is_draft=draft,
                status='draft' if draft else 'pending'
            )
            db.session.add(project)
        
        db.session.commit()
        
        # Clear session data
        if 'wizard_data' in session:
            del session['wizard_data']
        if 'current_project_id' in session:
            del session['current_project_id']
            
        flash('Projeto salvo com sucesso!', 'success')
        return redirect(url_for('projects.view_project', project_id=project.id))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error saving project: {str(e)}")
        flash('Ocorreu um erro ao salvar o projeto. Por favor, tente novamente.', 'error')
        if project_id:
            return redirect(url_for('wizard.new_project', project_id=project_id, step=1))
        else:
            return redirect(url_for('projects.projects'))

@bp.route('/new', methods=['GET', 'POST'])
@bp.route('/new/<int:project_id>', methods=['GET', 'POST'])
@login_required
def new_project(project_id=None):
    """Single-page wizard for project creation"""
    # Check if we have a project_id or need to create one
    project = None
    prompt_completed = False
    
    if project_id:
        # Load existing project
        project = Project.query.get_or_404(project_id)
        if project.user_id != current_user.id:
            flash('Acesso negado a este projeto.', 'error')
            return redirect(url_for('main.dashboard'))
        
        # Check if prompt is completed
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
        
        # Load project data into session
        session['wizard_data'] = content_data
        session['current_project_id'] = project_id
    else:
        # Redirect to project creation first
        flash('Primeiro você precisa criar um projeto.', 'info')
        return redirect(url_for('projects.new_project'))
    
    # Initialize session data
    if 'wizard_data' not in session:
        session['wizard_data'] = {}
    
    # Create a combined form with all steps
    from app.forms.wizard import CombinedWizardForm
    form = CombinedWizardForm()
    
    # Populate form with existing data
    wizard_data = session.get('wizard_data', {})
    for field_name in form._fields:
        if field_name in wizard_data and hasattr(form, field_name):
            getattr(form, field_name).data = wizard_data[field_name]
        
    # Handle form submission
    if request.method == 'POST':
        if form.validate_on_submit():
            # Save form data to session
            form_data = {}
            for field_name in form._fields:
                if field_name not in ['csrf_token'] and hasattr(form, field_name):
                    field = getattr(form, field_name)
                    if hasattr(field, 'data'):
                        form_data[field_name] = field.data
            
            # Check if prompt should be marked as completed
            if 'prompt_completed' in request.form or 'submit' in request.form:
                form_data['prompt_completed'] = True
            
            # Update session
            session['wizard_data'] = {**session.get('wizard_data', {}), **form_data}
            session.modified = True
            
            # Save to project
            if project:
                try:
                    project.content = form_data
                    project.updated_at = datetime.now()
                    db.session.commit()
                    
                    if form_data.get('prompt_completed'):
                        flash('Projeto finalizado com sucesso!', 'success')
                        return redirect(url_for('projects.view_project', project_id=project.id))
                    else:
                        flash('Rascunho salvo com sucesso!', 'success')
                        return redirect(url_for('wizard.new_project', project_id=project.id))
                        
                except Exception as e:
                    db.session.rollback()
                    current_app.logger.error(f"Error saving project: {str(e)}")
                    flash('Erro ao salvar o projeto. Tente novamente.', 'error')
        else:
            flash('Por favor, corrija os erros no formulário antes de continuar.', 'error')
    
    # Render the single-page wizard
    return render_template('wizard/single_page.html', 
                         form=form, 
                         project=project,
                         project_id=project_id,
                         prompt_completed=prompt_completed)
