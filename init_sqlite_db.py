import os
from app import create_app, db
from config_development import config
from app.models import User, Project, Execution, ExecutionLog, ExecutionStatus, ExecutionLogLevel

def init_database():
    # Remove existing SQLite database if it exists
    db_path = 'app.db'
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Create app with development config
    app = create_app(config)
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        try:
            # Check if admin user already exists
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                # Create admin user
                admin = User(
                    username='admin',
                    email='admin@example.com',
                    is_admin=True
                )
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                print("Created admin user")
            else:
                print("Admin user already exists")
            
            # Create a sample project
            project = Project.query.filter_by(title='Sample Project').first()
            if not project:
                project = Project(
                    title='Sample Project',
                    description='This is a sample project',
                    user_id=admin.id,
                    status='draft'
                )
                db.session.add(project)
                db.session.commit()
                print("Created sample project")
            else:
                print("Sample project already exists")
                
        except Exception as e:
            db.session.rollback()
            print(f"Error initializing database: {e}")
            raise
        
        print("\nSQLite database initialized successfully!")
        print(f"Database file: {os.path.abspath(db_path)}")
        print("Admin user created with username: admin, password: admin123")
        print("Sample project created with ID: 1\n")

if __name__ == '__main__':
    init_database()
