from datetime import datetime
from app import db
from .execution import Execution, ExecutionStatus

# Use JSON for SQLite compatibility
from sqlalchemy import JSON as JSONType

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='draft')  # draft, pending, in_progress, completed, archived
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    executions = db.relationship('Execution', back_populates='project', 
                               order_by='desc(Execution.started_at)',
                               cascade='all, delete-orphan')
    
    # JSON fields for flexible schema
    settings = db.Column(JSONType, default=dict)  # Stores all wizard settings
    content = db.Column(JSONType, default=dict)   # Stores generated content
    
    def __repr__(self):
        return f'<Project {self.title}>'
    
    def to_dict(self):
        """Convert project to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user_id': self.user_id,
            'settings': self.settings,
            'content': self.content
        }
    
    def update_status(self, new_status):
        """Update project status with validation"""
        valid_statuses = ['draft', 'pending', 'in_progress', 'completed', 'archived']
        if new_status in valid_statuses:
            self.status = new_status
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def get_progress(self):
        """Calculate project completion percentage"""
        if self.status == 'completed':
            return 100
        
        # Check for active execution
        active_execution = self.get_active_execution()
        if active_execution and active_execution.progress is not None:
            return int(active_execution.progress * 100)
        
        # Fallback to simple progress calculation based on status
        progress_map = {
            'draft': 25,
            'pending': 50,
            'in_progress': 75,
            'archived': 0
        }
        return progress_map.get(self.status, 0)
    
    def get_active_execution(self):
        """Get the most recent active execution"""
        return Execution.query.filter_by(
            project_id=self.id,
            status=ExecutionStatus.RUNNING
        ).order_by(Execution.started_at.desc()).first()
    
    def get_last_execution(self):
        """Get the most recent execution"""
        return Execution.query.filter_by(
            project_id=self.id
        ).order_by(Execution.started_at.desc()).first()
    
    def create_execution(self, user_id, metadata=None):
        """Create a new execution for this project"""
        execution = Execution(
            project_id=self.id,
            user_id=user_id,
            metadata_=metadata or {}
        )
        db.session.add(execution)
        
        # Update project status
        self.status = 'in_progress'
        
        db.session.commit()
        return execution
