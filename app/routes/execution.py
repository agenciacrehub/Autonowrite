from flask import Blueprint, render_template, jsonify, request, current_app, abort, make_response
from flask_login import login_required, current_user
from app import db
from app.models.project import Project
from app.models.execution import Execution, ExecutionStatus, ExecutionLogLevel
from app.utils.decorators import project_required, execution_required
import json
from datetime import datetime

bp = Blueprint('execution', __name__)

@bp.route('/project/<int:project_id>/execute', methods=['POST'])
@login_required
@project_required
def execute_project(project):
    """Start a new execution for a project"""
    # Check if there's already an active execution
    active_execution = project.get_active_execution()
    if active_execution:
        return jsonify({
            'status': 'error',
            'message': 'Já existe uma execução em andamento para este projeto',
            'execution_id': active_execution.id
        }), 400
    
    try:
        # Create a new execution
        execution = project.create_execution(current_user.id, {
            'user_agent': request.headers.get('User-Agent'),
            'ip_address': request.remote_addr
        })
        
        # Check if project has completed prompt
        if not project.content:
            return jsonify({
                'status': 'error',
                'message': 'Projeto deve ter o prompt concluído antes da execução'
            }), 400
            
        # Parse project content to check completion
        try:
            if isinstance(project.content, str):
                content_data = json.loads(project.content)
            else:
                content_data = project.content
                
            if not content_data.get('prompt_completed', False):
                return jsonify({
                    'status': 'error',
                    'message': 'O prompt do projeto deve ser finalizado antes de iniciar a execução'
                }), 400
        except Exception as e:
            current_app.logger.error(f"Error parsing project content: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': 'Erro ao validar dados do projeto'
            }), 400
        
        # Start background AI generation task
        # For now, simulate the task without Celery
        from app.tasks.content_generation import start_content_generation_sync
        task_result = start_content_generation_sync(execution.id, project.id)
        
        # Update execution with task result
        if task_result.get('status') == 'success':
            execution.metadata_['generation_completed'] = True
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'message': 'Execução concluída com sucesso',
                'execution_id': execution.id,
                'result': task_result
            })
        else:
            execution.status = ExecutionStatus.FAILED
            execution.add_log(f"Erro na geração: {task_result.get('error', 'Erro desconhecido')}", "ERROR")
            db.session.commit()
            
            return jsonify({
                'status': 'error',
                'message': 'Erro na execução da geração de conteúdo',
                'execution_id': execution.id
            }), 500
        
    except Exception as e:
        current_app.logger.error(f'Error starting execution: {str(e)}')
        return jsonify({
            'status': 'error',
            'message': 'Erro ao iniciar a execução'
        }), 500

@bp.route('/execution/<int:execution_id>')
@login_required
@execution_required
def get_execution(execution):
    """Get execution details"""
    return jsonify(execution.to_dict())

@bp.route('/execution/<int:execution_id>/status')
@login_required
@execution_required
def get_execution_status(execution):
    """Get execution status"""
    return jsonify({
        'id': execution.id,
        'status': execution.status.value,
        'progress': execution.progress,
        'started_at': execution.started_at.isoformat() if execution.started_at else None,
        'completed_at': execution.completed_at.isoformat() if execution.completed_at else None
    })

@bp.route('/execution/<int:execution_id>/logs')
@login_required
@execution_required
def get_execution_logs(execution):
    """Get execution logs"""
    logs = [log.to_dict() for log in execution.logs]
    return jsonify(logs)

@bp.route('/execution/<int:execution_id>/cancel', methods=['POST'])
@login_required
@execution_required
def cancel_execution(execution):
    """Cancel an execution"""
    if execution.status not in [ExecutionStatus.PENDING, ExecutionStatus.RUNNING]:
        return jsonify({
            'status': 'error',
            'message': 'A execução não pode ser cancelada no estado atual'
        }), 400
    
    try:
        execution.cancel()
        return jsonify({
            'status': 'success',
            'message': 'Execução cancelada com sucesso'
        })
    except Exception as e:
        current_app.logger.error(f'Error cancelling execution: {str(e)}')
        return jsonify({
            'status': 'error',
            'message': 'Erro ao cancelar a execução'
        }), 500

@bp.route('/project/<int:project_id>/dashboard')
@login_required
@project_required
def execution_dashboard(project):
    """Render the execution dashboard"""
    # Get the most recent execution
    execution = project.get_last_execution()
    
    return render_template('execution/dashboard.html', 
                         project=project, 
                         execution=execution,
                         ExecutionStatus=ExecutionStatus)

@bp.route('/project/<int:project_id>/executions')
@login_required
@project_required
def project_executions(project):
    """List all executions for a project"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    executions = Execution.query.filter_by(project_id=project.id)\
                              .order_by(Execution.started_at.desc())\
                              .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('execution/list.html',
                         project=project,
                         executions=executions,
                         ExecutionStatus=ExecutionStatus)

@bp.route('/<int:execution_id>/status')
@login_required
def execution_status(execution_id):
    """Get execution status as JSON"""
    execution = Execution.query.get_or_404(execution_id)
    
    return jsonify({
        'id': execution.id,
        'status': execution.status.value,
        'progress': execution.progress or 0.0,
        'started_at': execution.started_at.isoformat() if execution.started_at else None,
        'completed_at': execution.completed_at.isoformat() if execution.completed_at else None
    })

@bp.route('/<int:execution_id>/logs')
@login_required
def execution_logs(execution_id):
    """Get execution logs as JSON"""
    execution = Execution.query.get_or_404(execution_id)
    after_id = request.args.get('after', 0, type=int)
    
    logs = [log for log in execution.logs if log.id > after_id]
    
    return jsonify([{
        'id': log.id,
        'timestamp': log.timestamp.isoformat(),
        'level': log.level.value,
        'message': log.message
    } for log in logs])

@bp.route('/<int:execution_id>/logs/download')
@login_required
def download_logs(execution_id):
    """Download execution logs as text file"""
    execution = Execution.query.get_or_404(execution_id)
    
    logs_text = []
    for log in execution.logs:
        timestamp = log.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        logs_text.append(f"[{timestamp}] {log.level.value}: {log.message}")
    
    response = make_response('\n'.join(logs_text))
    response.headers['Content-Type'] = 'text/plain'
    response.headers['Content-Disposition'] = f'attachment; filename=execution_{execution_id}_logs.txt'
    
    return response

# Helper function to update execution progress
def update_execution_progress(execution_id, progress, message=None):
    """Update execution progress (to be called from background tasks)"""
    with current_app.app_context():
        try:
            execution = Execution.query.get(execution_id)
            if not execution:
                current_app.logger.error(f'Execution {execution_id} not found')
                return False
                
            execution.update_progress(progress)
            if message:
                execution.add_log(message)
                
            db.session.commit()
            return True
            
        except Exception as e:
            current_app.logger.error(f'Error updating execution progress: {str(e)}')
            db.session.rollback()
            return False
