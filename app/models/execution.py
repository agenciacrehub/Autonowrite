from datetime import datetime
from enum import Enum
from app import db
from sqlalchemy import JSON as JSONType

class ExecutionStatus(Enum):
    PENDING = 'pending'
    RUNNING = 'running'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'

class ExecutionLogLevel(Enum):
    INFO = 'info'
    WARNING = 'warning'
    ERROR = 'error'
    DEBUG = 'debug'

class Execution(db.Model):
    __tablename__ = 'executions'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.Enum(ExecutionStatus), default=ExecutionStatus.PENDING, nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    progress = db.Column(db.Float, default=0.0)  # 0.0 to 1.0
    metadata_ = db.Column('metadata', JSONType)  # Additional execution metadata
    
    # Relationships
    project = db.relationship('Project', back_populates='executions')
    user = db.relationship('User')
    logs = db.relationship('ExecutionLog', back_populates='execution', 
                          order_by='ExecutionLog.timestamp', 
                          cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        super(Execution, self).__init__(**kwargs)
        self.metadata_ = self.metadata_ or {}
    
    def update_progress(self, progress, commit=True):
        """Update execution progress (0.0 to 1.0)"""
        self.progress = max(0.0, min(1.0, float(progress)))
        if commit:
            db.session.commit()
    
    def add_log(self, message, level=ExecutionLogLevel.INFO, commit=True):
        """Add a log entry for this execution"""
        log = ExecutionLog(
            execution_id=self.id,
            message=message,
            level=level
        )
        db.session.add(log)
        if commit:
            db.session.commit()
        return log
    
    def start(self):
        """Mark execution as started"""
        self.status = ExecutionStatus.RUNNING
        self.started_at = datetime.utcnow()
        self.add_log("Execution started")
        db.session.commit()
    
    def complete(self, result=None):
        """Mark execution as completed"""
        self.status = ExecutionStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.progress = 1.0
        if result is not None:
            self.metadata_ = {**self.metadata_, 'result': result}
        self.add_log("Execution completed successfully")
        db.session.commit()
    
    def fail(self, error):
        """Mark execution as failed"""
        self.status = ExecutionStatus.FAILED
        self.completed_at = datetime.utcnow()
        self.metadata_ = {**self.metadata_, 'error': str(error)}
        self.add_log(f"Execution failed: {error}", ExecutionLogLevel.ERROR)
        db.session.commit()
    
    def cancel(self):
        """Cancel the execution"""
        if self.status in [ExecutionStatus.PENDING, ExecutionStatus.RUNNING]:
            self.status = ExecutionStatus.CANCELLED
            self.completed_at = datetime.utcnow()
            self.add_log("Execution was cancelled", ExecutionLogLevel.WARNING)
            db.session.commit()
    
    def get_elapsed_time(self):
        """Get formatted elapsed time since execution started"""
        if not self.started_at:
            return '00:00:00'
            
        from datetime import datetime
        end_time = self.completed_at or datetime.utcnow()
        delta = end_time - self.started_at
        
        # Format as HH:MM:SS
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def get_duration(self):
        """Get total execution duration in seconds"""
        if not self.started_at:
            return 0
            
        end_time = self.completed_at or datetime.utcnow()
        return int((end_time - self.started_at).total_seconds())
    
    def to_dict(self, include_logs=True):
        """Convert execution to dictionary for JSON serialization"""
        result = {
            'id': self.id,
            'project_id': self.project_id,
            'status': self.status.value,
            'progress': self.progress,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'elapsed_time': self.get_elapsed_time(),
            'duration': self.get_duration(),
            'metadata': self.metadata_ or {},
            'project': {
                'id': self.project.id,
                'title': self.project.title,
                'status': self.project.status
            },
            'user': {
                'id': self.user.id,
                'username': self.user.username
            }
        }
        
        if include_logs:
            result['logs'] = [log.to_dict() for log in self.logs]
            
        return result

class ExecutionLog(db.Model):
    __tablename__ = 'execution_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    execution_id = db.Column(db.Integer, db.ForeignKey('executions.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    level = db.Column(db.Enum(ExecutionLogLevel), nullable=False)
    message = db.Column(db.Text, nullable=False)
    
    # Relationships
    execution = db.relationship('Execution', back_populates='logs')
    
    def to_dict(self):
        """Convert log entry to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'execution_id': self.execution_id,
            'timestamp': self.timestamp.isoformat(),
            'level': self.level.value,
            'message': self.message
        }
