import os
from app import create_app, db
from app.models import User, Project, Execution, ExecutionLog, ExecutionStatus, ExecutionLogLevel

def init_db():
    # Ensure we're using SQLite for this initialization
    os.environ['DATABASE_URL'] = 'sqlite:///' + os.path.abspath('app.db')
    
    app = create_app()
    with app.app_context():
        # Disable foreign key constraints for SQLite
        if 'sqlite' in str(db.engine.url):
            db.engine.execute('PRAGMA foreign_keys=OFF')
        
        # Drop all tables
        db.drop_all()
        
        # Re-enable foreign key constraints
        if 'sqlite' in str(db.engine.url):
            db.engine.execute('PRAGMA foreign_keys=ON')
        
        # Create all tables
        db.create_all()
        
        # Create admin user
        admin = User(
            username='admin',
            email='admin@example.com',
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Create a sample project
        project = Project(
            title='Sample Project',
            description='This is a sample project',
            user_id=1,
            status='draft'
        )
        db.session.add(project)
        
        # Commit the changes
        db.session.commit()
        
        print("\nDatabase initialized successfully!")
        print("SQLite database file created at:", os.path.abspath('app.db'))
        print("Admin user created with username: admin, password: admin123")
        print("Sample project created with ID: 1\n")

if __name__ == '__main__':
    init_db()
