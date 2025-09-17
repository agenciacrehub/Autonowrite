#!/usr/bin/env python3
"""
Debug script to test execution system with proper database configuration
"""
import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Force SQLite database
os.environ['DATABASE_URL'] = 'sqlite:///app.db'

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Create a minimal Flask app with SQLite
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'debug-key'

db = SQLAlchemy(app)

# Import models after db is configured
from app.models.project import Project
from app.models.execution import Execution, ExecutionStatus
from app.models.user import User

def test_execution_system():
    """Test the execution system with proper database configuration"""
    
    with app.app_context():
        try:
            # Check database connection
            print("Testing database connection...")
            projects = Project.query.all()
            print(f"✅ Database connection successful. Found {len(projects)} projects.")
            
            # List all projects and their executions
            for project in projects:
                print(f"\nProject {project.id}: {project.title}")
                print(f"  User ID: {project.user_id}")
                print(f"  Status: {project.status}")
                
                if project.content:
                    prompt_completed = project.content.get('prompt_completed', False)
                    print(f"  Prompt completed: {prompt_completed}")
                    
                    if project.content.get('generated_content'):
                        print(f"  Has generated content: ✅")
                    else:
                        print(f"  Has generated content: ❌")
                else:
                    print(f"  Content: None")
                
                # Check executions
                executions = Execution.query.filter_by(project_id=project.id).all()
                print(f"  Executions: {len(executions)}")
                
                for exec in executions:
                    print(f"    - Execution {exec.id}: {exec.status.value} (started: {exec.started_at})")
                    if exec.status == ExecutionStatus.COMPLETED:
                        print(f"      Completed: {exec.completed_at}")
                        print(f"      Progress: {exec.progress}")
            
            # Test execution creation for a project with completed prompt
            test_project = None
            for project in projects:
                if project.content and project.content.get('prompt_completed', False):
                    test_project = project
                    break
            
            if test_project:
                print(f"\n🧪 Testing execution creation for project: {test_project.title}")
                
                # Check for existing active execution
                active_execution = test_project.get_active_execution()
                if active_execution:
                    print(f"  Found active execution: {active_execution.id}")
                else:
                    print(f"  No active execution found")
                
                # Test the execution route logic
                print(f"  Project prompt completed: {test_project.content.get('prompt_completed', False)}")
                print(f"  Ready for execution: ✅")
                
            else:
                print(f"\n❌ No projects with completed prompts found for testing")
            
            return True
            
        except Exception as e:
            print(f"❌ Database test failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = test_execution_system()
    sys.exit(0 if success else 1)
