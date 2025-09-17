#!/usr/bin/env python3
"""Initialize the PostgreSQL database for AutonoWrite."""
import os
import sys
import subprocess
from pathlib import Path

def run_psql_command(command: str, use_sudo: bool = False):
    """Run a PostgreSQL command using psql."""
    try:
        cmd = ['sudo', '-u', 'postgres', 'psql', '-c', command]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"Error executing command: {result.stderr}", file=sys.stderr)
            return False
        return True
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return False

def main():
    """Initialize the database and user."""
    print("🚀 Initializing AutonoWrite database...")
    
    # Check if psql is available
    try:
        subprocess.run(['which', 'psql'], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("❌ PostgreSQL client (psql) is not installed or not in PATH")
        sys.exit(1)
    
    # Create database and user
    print("🔧 Creating database and user...")
    
    # First try without sudo
    use_sudo = False
    commands = [
        "CREATE USER autonowrite_user WITH PASSWORD 'autonowrite_pass';",
        "ALTER USER autonowrite_user CREATEDB;",
        "CREATE DATABASE autonowrite_db OWNER autonowrite_user;"
    ]
    
    # Try without sudo first
    success = True
    for cmd in commands:
        if not run_psql_command(cmd, use_sudo=False):
            print("⚠️  Trying with sudo...")
            use_sudo = True
            break
    
    # If first attempt failed, try with sudo
    if use_sudo:
        for cmd in commands:
            if not run_psql_command(cmd, use_sudo=True):
                print(f"❌ Failed to execute command: {cmd}")
                success = False
    
    if not success:
        print("\n⚠️  Automatic database setup failed. Please create the database and user manually:")
        print("""
Run these commands as PostgreSQL superuser:

CREATE USER autonowrite_user WITH PASSWORD 'autonowrite_pass';
ALTER USER autonowrite_user CREATEDB;
CREATE DATABASE autonowrite_db OWNER autonowrite_user;

Or run this script with sudo:
sudo -u postgres psql -c "CREATE USER autonowrite_user WITH PASSWORD 'autonowrite_pass';"
sudo -u postgres psql -c "ALTER USER autonowrite_user CREATEDB;"
sudo -u postgres psql -c "CREATE DATABASE autonowrite_db OWNER autonowrite_user;"
        """)
        sys.exit(1)
    
    print("✅ Database and user created successfully")
    
    # Install required Python packages
    print("📦 Installing required Python packages...")
    try:
        subprocess.run([
            sys.executable, '-m', 'pip', 'install',
            'sqlalchemy', 'psycopg2-binary', 'alembic', 'python-dotenv'
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install packages: {e}")
        sys.exit(1)
    
    # Initialize Alembic
    print("🔧 Initializing Alembic for database migrations...")
    try:
        subprocess.run(['alembic', 'init', 'src/database/migrations'], check=True)
        
        # Update alembic.ini
        alembic_ini = Path('alembic.ini')
        if alembic_ini.exists():
            content = alembic_ini.read_text()
            content = content.replace(
                'sqlalchemy.url = driver://user:pass@localhost/dbname',
                'sqlalchemy.url = postgresql+psycopg2://autonowrite_user:autonowrite_pass@localhost/autonowrite_db'
            )
            alembic_ini.write_text(content)
        
        # Update env.py for migrations
        env_py = Path('src/database/migrations/env.py')
        if env_py.exists():
            content = env_py.read_text()
            content = content.replace(
                "from logging.config import fileConfig",
                """import os
import sys
from logging.config import fileConfig

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))"""
            )
            content = content.replace(
                'target_metadata = None',
                """from database.models import Base

target_metadata = Base.metadata"""
            )
            env_py.write_text(content)
        
        print("✅ Alembic initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Alembic: {e}")
        sys.exit(1)
    
    print("\n🎉 Database setup completed successfully!")
    print("Next steps:")
    print("1. Run 'alembic revision --autogenerate -m 'Initial migration'")
    print("2. Run 'alembic upgrade head' to apply migrations")

if __name__ == "__main__":
    main()
