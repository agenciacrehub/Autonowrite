# Database Setup for AutonoWrite

This guide will help you set up the PostgreSQL database for AutonoWrite.

## Prerequisites

1. PostgreSQL 13 or higher installed
2. Python 3.8 or higher
3. `psql` command line tool
4. PostgreSQL superuser access (usually the 'postgres' user)

## Setup Instructions

### 1. Run the Database Initialization Script

```bash
# Make the script executable
chmod +x scripts/init_db.py

# Run the initialization script
python3 scripts/init_db.py
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Create and Apply Database Migrations

```bash
# Navigate to the project root
cd /path/to/autonowrite-mvp

# Create an initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### 4. Verify the Setup

You can verify the setup by running:

```bash
psql -U autonowrite_user -d autonowrite_db -c "\dt"
```

You should see the following tables:
- projects
- structured_inputs
- agent_executions
- quality_evaluations
- research_data

## Environment Variables

Create a `.env` file in the project root with the following variables:

```
DATABASE_URL=postgresql+psycopg2://autonowrite_user:autonowrite_pass@localhost/autonowrite_db
```

## Database Schema

### Projects
- `id`: Primary key
- `user_id`: Foreign key to users table (for future use)
- `title`: Project title
- `status`: Project status (draft, in_progress, completed, failed)
- `created_at`: Timestamp of creation
- `updated_at`: Timestamp of last update

### Structured Inputs
- `id`: Primary key
- `project_id`: Foreign key to projects table
- `domain`: Knowledge domain
- `target_audience`: Target audience
- `objectives`: JSON field for project objectives
- `scope`: JSON field for project scope
- `sources_preference`: JSON field for source preferences
- `style_requirements`: JSON field for style requirements

### Agent Executions
- `id`: Primary key
- `project_id`: Foreign key to projects table
- `agent_type`: Type of agent (planner, researcher, writer, critic)
- `iteration`: Iteration number
- `input_prompt`: Input given to the agent
- `output_content`: Output from the agent
- `execution_time`: Time taken for execution (in seconds)
- `tokens_used`: Number of tokens used
- `created_at`: Timestamp of creation

### Quality Evaluations
- `id`: Primary key
- `project_id`: Foreign key to projects table
- `iteration`: Iteration number
- `score`: Overall quality score (0.0-10.0)
- `criteria_breakdown`: JSON field with detailed scores
- `approved`: Boolean indicating if the content was approved
- `feedback`: Optional feedback text
- `created_at`: Timestamp of creation

### Research Data
- `id`: Primary key
- `project_id`: Foreign key to projects table
- `search_query`: The search query used
- `sources_found`: JSON array of sources with metadata
- `relevance_score`: Relevance score (0.0-1.0)
- `content_summary`: Summary of the research content
- `created_at`: Timestamp of creation
