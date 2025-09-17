from functools import wraps
from flask import jsonify, request, abort
from flask_login import current_user
from app.models.project import Project
from app.models.execution import Execution

def project_required(f):
    """Decorator to ensure the project exists and user has access"""
    @wraps(f)
    def decorated_function(project_id, *args, **kwargs):
        project = Project.query.get_or_404(project_id)
        
        # Check if user has access to the project
        if project.user_id != current_user.id and not current_user.is_admin:
            abort(403)  # Forbidden
            
        return f(project=project, *args, **kwargs)
    return decorated_function

def execution_required(f):
    """Decorator to ensure the execution exists and user has access"""
    @wraps(f)
    def decorated_function(execution_id, *args, **kwargs):
        execution = Execution.query.get_or_404(execution_id)
        
        # Check if user has access to the execution
        if execution.user_id != current_user.id and not current_user.is_admin:
            abort(403)  # Forbidden
            
        return f(execution=execution, *args, **kwargs)
    return decorated_function

def json_required(f):
    """Decorator to ensure the request has valid JSON"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return jsonify({
                'status': 'error',
                'message': 'Content-Type must be application/json'
            }), 400
            
        try:
            request.get_json()
        except Exception:
            return jsonify({
                'status': 'error',
                'message': 'Invalid JSON data'
            }), 400
            
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to ensure the user is an admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function
