import psycopg2
from config import Config

def drop_database():
    # Get database URL from config
    db_url = Config.SQLALCHEMY_DATABASE_URI
    
    # Parse database URL
    from sqlalchemy.engine import make_url
    url = make_url(db_url)
    
    # Connect to PostgreSQL server (without specifying a database)
    conn = psycopg2.connect(
        host=url.host or 'localhost',
        port=url.port or 5432,
        user=url.username or 'postgres',
        password=url.password or '',
        dbname='postgres'  # Connect to default database
    )
    conn.autocommit = True
    
    # Drop the database
    db_name = url.database
    with conn.cursor() as cur:
        # Terminate all connections to the database
        cur.execute("""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = %s
            AND pid <> pg_backend_pid();
        """, (db_name,))
        
        # Drop the database with CASCADE
        cur.execute(f'DROP DATABASE IF EXISTS \"{db_name}\" WITH (FORCE)')
    
    conn.close()
    print(f"Dropped database: {db_name}")

if __name__ == '__main__':
    drop_database()
