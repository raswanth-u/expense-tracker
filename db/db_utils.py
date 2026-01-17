# db/db_utils.py

from db.database_connection import inspector

def list_tables():
    return inspector.get_table_names()

def list_columns(table_name: str):
    return inspector.get_columns(table_name)

def get_primary_key(table_name: str):
    pk = inspector.get_pk_constraint(table_name)
    return pk.get('constrained_columns', [])

def get_foreign_keys(table_name: str):
    return inspector.get_foreign_keys(table_name)

def get_indexes(table_name: str):
    return inspector.get_indexes(table_name)

def get_unique_constraints(table_name: str):
    return inspector.get_unique_constraints(table_name)

def list_schemas():
    return inspector.get_schema_names()

def get_table_info(table_name: str):
    return {
        "columns": list_columns(table_name),
        "primary_key": get_primary_key(table_name),
        "foreign_keys": get_foreign_keys(table_name),
        "indexes": get_indexes(table_name),
        "unique_constraints": get_unique_constraints(table_name),
    }

def get_schema_tables(schema_name: str):
    return inspector.get_table_names(schema=schema_name)

if __name__ == "__main__":
    tables = list_tables()
    print("Tables in the database:")
    for table in tables:
        print(table)
        
    cols = list_columns("actor")
    print("\nColumns in 'actor' table:")
    for column in cols:
        print(column['name'])
        
    pk = get_primary_key("actor")
    print("\nPrimary Key of 'actor' table:", pk)
    
    fks = get_foreign_keys("film_actor")
    print("\nForeign Keys in 'film_actor' table:")
    for fk in fks:
        print(fk)
        
    indexes = get_indexes("actor")
    print("\nIndexes in 'actor' table:")
    for index in indexes:
        print(index)
        
    uniques = get_unique_constraints("actor")
    print("\nUnique Constraints in 'actor' table:")
    for unique in uniques:
        print(unique)
        
    schemas = list_schemas()
    print("\nSchemas in the database:")
    for schema in schemas:
        print(schema)
        
    table_info = get_table_info("actor")
    print("\nTable Info for 'actor':", table_info)
    
    schema_tables = get_schema_tables("public")
    print("\nTables in 'public' schema:")
    for table in schema_tables:
        print(table)
        
    