#!/usr/bin/env python3
"""
Test script for the execution system using SQLite directly
"""
import os
import sys
import json
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.project import Project
from app.models.user import User
from app.models.execution import Execution, ExecutionStatus

def test_execution_system():
    """Test the execution system with a sample project"""
    
    # Force SQLite configuration by setting environment variable
    import os
    os.environ['DATABASE_URL'] = 'sqlite:///app.db'
    
    # Create app with SQLite configuration
    app = create_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    with app.app_context():
        try:
            # Check existing projects
            projects = Project.query.all()
            print(f"Found {len(projects)} projects in database")
            
            # Find a project with completed prompt or create one
            test_project = None
            for project in projects:
                if project.content:
                    try:
                        if isinstance(project.content, str):
                            content_data = json.loads(project.content)
                        else:
                            content_data = project.content
                        
                        if content_data.get('prompt_completed', False):
                            test_project = project
                            print(f"Found project with completed prompt: {project.title}")
                            break
                    except Exception as e:
                        print(f"Error parsing project {project.id} content: {e}")
            
            # If no project with completed prompt, create one
            if not test_project:
                print("Creating test project with completed prompt...")
                
                # Get first user or create one
                user = User.query.first()
                if not user:
                    print("No users found. Please create a user first.")
                    return False
                
                # Create test project
                test_project = Project(
                    title="Test AI Content Generation",
                    description="Test project for execution system",
                    user_id=user.id,
                    content={
                        "project_title": "Test AI Content Generation",
                        "knowledge_domain": "Technology",
                        "target_audience": "Developers",
                        "content_type": "Article",
                        "tone": "Professional",
                        "length": "Medium",
                        "key_topics": ["AI", "Content Generation", "Automation"],
                        "prompt_completed": True
                    }
                )
                db.session.add(test_project)
                db.session.commit()
                print(f"Created test project: {test_project.title}")
            
            # Test execution creation
            print(f"\nTesting execution for project: {test_project.title}")
            
            # Check for existing active execution
            active_execution = test_project.get_active_execution()
            if active_execution:
                print(f"Found active execution: {active_execution.id}")
                return True
            
            # Create new execution
            print("Creating new execution...")
            execution = test_project.create_execution(
                user_id=test_project.user_id,
                metadata={'test': True, 'created_by': 'test_script'}
            )
            
            print(f"Created execution {execution.id} with status: {execution.status}")
            
            # Test the content generation task
            print("Testing content generation task...")
            from app.tasks.content_generation import start_content_generation_sync
            
            result = start_content_generation_sync(execution.id, test_project.id)
            print(f"Content generation result: {result.get('status', 'unknown')}")
            
            if result.get('status') == 'success':
                print("✅ Execution system test PASSED")
                
                # Check the generated content
                db.session.refresh(test_project)
                if test_project.content and 'generated_content' in test_project.content:
                    print("✅ Content was generated and saved to project")
                else:
                    print("⚠️  Content generation completed but no content found in project")
                
                return True
            else:
                print(f"❌ Execution system test FAILED: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = test_execution_system()
    sys.exit(0 if success else 1)
