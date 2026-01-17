# db/raw_sql_utils.py

from db.database_connection import engine
from sqlalchemy import text

class PostgreSQLDBUtils:
    
    @staticmethod
    def list_tables_postgresql():
        with engine.connect() as connection:
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
            """))
            return [row[0] for row in result]
    
if __name__ == "__main__":
    tables = PostgreSQLDBUtils.list_tables_postgresql()
    print("Tables in the PostgreSQL database:")
    for table in tables:
        print(table)