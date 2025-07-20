import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def extract_complete_database():
    """
    Extract complete DDL and DML from the DVD Rental PostgreSQL database
    """
    # Database connection parameters
    db_url = "postgresql://postgres:admin@localhost/dvdrental"
    
    try:
        # Connect to database
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        sql_statements = []
        sql_statements.append("-- DVD Rental Database - Complete Recreation Script")
        sql_statements.append("-- Generated from PostgreSQL database")
        sql_statements.append("-- Date: " + str(__import__('datetime').datetime.now()))
        sql_statements.append("-- This script creates tables and inserts all data")
        sql_statements.append("")
        sql_statements.append("-- Create database (run this separately if needed)")
        sql_statements.append("-- CREATE DATABASE dvdrental;")
        sql_statements.append("-- \\c dvdrental;")
        sql_statements.append("")
        
        # Create custom types first
        sql_statements.append("-- Create custom types")
        sql_statements.append("CREATE TYPE mpaa_rating AS ENUM ('G','PG','PG-13','R','NC-17');")
        sql_statements.append("")
        
        # Get all tables in dependency order (parents before children)
        table_order = [
            'country', 'city', 'address', 'category', 'language', 'actor',
            'customer', 'staff', 'store', 'film', 'film_actor', 'film_category',
            'inventory', 'rental', 'payment'
        ]
        
        # Create tables
        sql_statements.append("-- ===============================")
        sql_statements.append("-- CREATE TABLES")
        sql_statements.append("-- ===============================")
        sql_statements.append("")
        
        for table_name in table_order:
            sql_statements.append(f"-- Table: {table_name}")
            sql_statements.append(f"CREATE TABLE {table_name} (")
            
            # Get column information
            cursor.execute("""
                SELECT 
                    column_name,
                    data_type,
                    character_maximum_length,
                    is_nullable,
                    column_default,
                    COALESCE(udt_name, data_type) as udt_name
                FROM information_schema.columns 
                WHERE table_name = %s 
                AND table_schema = 'public'
                ORDER BY ordinal_position;
            """, (table_name,))
            
            columns = cursor.fetchall()
            column_definitions = []
            
            for col in columns:
                if len(col) == 6:
                    col_name, data_type, max_length, is_nullable, default, udt_name = col
                else:
                    # Handle case where udt_name might be missing
                    col_name, data_type, max_length, is_nullable, default = col[:5]
                    udt_name = data_type
                
                # Build column definition
                col_def = f"    {col_name} "
                
                if data_type == 'character varying':
                    if max_length:
                        col_def += f"VARCHAR({max_length})"
                    else:
                        col_def += "VARCHAR"
                elif data_type == 'character':
                    col_def += f"CHAR({max_length})"
                elif data_type == 'timestamp without time zone':
                    col_def += "TIMESTAMP"
                elif data_type == 'timestamp with time zone':
                    col_def += "TIMESTAMPTZ"
                elif data_type == 'USER-DEFINED':
                    if udt_name == 'mpaa_rating':
                        col_def += "mpaa_rating"
                    elif udt_name == 'tsvector':
                        col_def += "TSVECTOR"
                    elif '_' in udt_name:  # Array types
                        col_def += f"{udt_name.replace('_', '').upper()}[]"
                    else:
                        col_def += udt_name.upper()
                elif data_type == 'ARRAY':
                    col_def += "TEXT[]"
                else:
                    col_def += data_type.upper()
                
                # Handle nullability
                if is_nullable == 'NO':
                    col_def += " NOT NULL"
                
                # Handle default values (but not SERIAL ones in CREATE)
                if default and 'nextval' not in str(default):
                    col_def += f" DEFAULT {default}"
                
                column_definitions.append(col_def)
            
            sql_statements.append(",\n".join(column_definitions))
            sql_statements.append(");")
            sql_statements.append("")
        
        # Add primary keys
        sql_statements.append("-- ===============================")
        sql_statements.append("-- PRIMARY KEYS")
        sql_statements.append("-- ===============================")
        sql_statements.append("")
        
        cursor.execute("""
            SELECT 
                tc.table_name, 
                string_agg(kcu.column_name, ', ' ORDER BY kcu.ordinal_position) as columns
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu 
                ON tc.constraint_name = kcu.constraint_name 
                AND tc.table_schema = kcu.table_schema
            WHERE tc.constraint_type = 'PRIMARY KEY' 
            AND tc.table_schema = 'public'
            GROUP BY tc.table_name
            ORDER BY tc.table_name;
        """)
        
        primary_keys = cursor.fetchall()
        for table_name, columns in primary_keys:
            sql_statements.append(f"ALTER TABLE {table_name} ADD PRIMARY KEY ({columns});")
        
        sql_statements.append("")
        
        # Add sequences for SERIAL columns
        sql_statements.append("-- ===============================")
        sql_statements.append("-- SEQUENCES")
        sql_statements.append("-- ===============================")
        sql_statements.append("")
        
        for table_name in table_order:
            cursor.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = %s 
                AND table_schema = 'public'
                AND column_default LIKE 'nextval%'
                ORDER BY ordinal_position;
            """, (table_name,))
            
            serial_columns = cursor.fetchall()
            for (col_name,) in serial_columns:
                seq_name = f"{table_name}_{col_name}_seq"
                sql_statements.append(f"CREATE SEQUENCE {seq_name};")
                sql_statements.append(f"ALTER TABLE {table_name} ALTER COLUMN {col_name} SET DEFAULT nextval('{seq_name}');")
                sql_statements.append(f"ALTER SEQUENCE {seq_name} OWNED BY {table_name}.{col_name};")
        
        sql_statements.append("")
        
        # Insert data
        sql_statements.append("-- ===============================")
        sql_statements.append("-- INSERT DATA")
        sql_statements.append("-- ===============================")
        sql_statements.append("")
        
        for table_name in table_order:
            # Get column names
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = %s 
                AND table_schema = 'public'
                ORDER BY ordinal_position;
            """, (table_name,))
            
            columns = [row[0] for row in cursor.fetchall()]
            column_list = ", ".join(columns)
            
            # Get data
            cursor.execute(f'SELECT * FROM {table_name} ORDER BY 1;')
            rows = cursor.fetchall()
            
            if rows:
                sql_statements.append(f"-- Data for table: {table_name}")
                
                # Split large tables into smaller batches
                batch_size = 100
                for i in range(0, len(rows), batch_size):
                    batch = rows[i:i+batch_size]
                    
                    sql_statements.append(f"INSERT INTO {table_name} ({column_list}) VALUES")
                    
                    value_strings = []
                    for row in batch:
                        # Convert values to SQL format
                        formatted_values = []
                        for val in row:
                            if val is None:
                                formatted_values.append("NULL")
                            elif isinstance(val, str):
                                # Escape single quotes
                                escaped_val = val.replace("'", "''")
                                formatted_values.append(f"'{escaped_val}'")
                            elif isinstance(val, (int, float)):
                                formatted_values.append(str(val))
                            elif isinstance(val, bool):
                                formatted_values.append("TRUE" if val else "FALSE")
                            elif hasattr(val, 'isoformat'):  # datetime objects
                                formatted_values.append(f"'{val.isoformat()}'")
                            elif isinstance(val, list):  # Arrays
                                array_str = "{" + ",".join([f'"{item}"' if isinstance(item, str) else str(item) for item in val]) + "}"
                                formatted_values.append(f"'{array_str}'")
                            else:
                                formatted_values.append(f"'{str(val)}'")
                        
                        value_strings.append(f"    ({', '.join(formatted_values)})")
                    
                    sql_statements.append(",\n".join(value_strings) + ";")
                    sql_statements.append("")
        
        # Add foreign keys
        sql_statements.append("-- ===============================")
        sql_statements.append("-- FOREIGN KEYS")
        sql_statements.append("-- ===============================")
        sql_statements.append("")
        
        cursor.execute("""
            SELECT 
                tc.table_name,
                tc.constraint_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu 
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage ccu 
                ON ccu.constraint_name = tc.constraint_name
                AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_schema = 'public'
            ORDER BY tc.table_name, tc.constraint_name;
        """)
        
        foreign_keys = cursor.fetchall()
        for table_name, constraint_name, column_name, foreign_table, foreign_column in foreign_keys:
            sql_statements.append(f"ALTER TABLE {table_name} ADD CONSTRAINT {constraint_name} FOREIGN KEY ({column_name}) REFERENCES {foreign_table}({foreign_column});")
        
        sql_statements.append("")
        
        # Add indexes
        sql_statements.append("-- ===============================")
        sql_statements.append("-- INDEXES")
        sql_statements.append("-- ===============================")
        sql_statements.append("")
        
        cursor.execute("""
            SELECT 
                schemaname,
                tablename,
                indexname,
                indexdef
            FROM pg_indexes 
            WHERE schemaname = 'public'
            AND indexname NOT LIKE '%_pkey'
            ORDER BY tablename, indexname;
        """)
        
        indexes = cursor.fetchall()
        for schema, table, index_name, index_def in indexes:
            sql_statements.append(f"{index_def};")
        
        sql_statements.append("")
        
        # Update sequences to current values
        sql_statements.append("-- ===============================")
        sql_statements.append("-- UPDATE SEQUENCES")
        sql_statements.append("-- ===============================")
        sql_statements.append("")
        
        for table_name in table_order:
            cursor.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = %s 
                AND table_schema = 'public'
                AND column_default LIKE 'nextval%'
                ORDER BY ordinal_position;
            """, (table_name,))
            
            serial_columns = cursor.fetchall()
            for (col_name,) in serial_columns:
                seq_name = f"{table_name}_{col_name}_seq"
                sql_statements.append(f"SELECT setval('{seq_name}', (SELECT MAX({col_name}) FROM {table_name}));")
        
        sql_statements.append("")
        sql_statements.append("-- Database recreation complete!")
        
        cursor.close()
        conn.close()
        
        return "\n".join(sql_statements)
        
    except Exception as e:
        return f"Error extracting complete database: {str(e)}"

if __name__ == "__main__":
    print("Extracting complete database with data...")
    complete_sql = extract_complete_database()
    
    # Save to file
    with open("dvd_rental_complete.sql", "w", encoding='utf-8') as f:
        f.write(complete_sql)
    
    print("Complete database script saved to dvd_rental_complete.sql")
    print("\nThis file contains:")
    print("- CREATE TABLE statements")
    print("- INSERT statements with all data")
    print("- PRIMARY KEY constraints")
    print("- FOREIGN KEY constraints")
    print("- INDEXES")
    print("- SEQUENCE updates")
    print("\nYou can run this script to recreate the entire database!")
