import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def extract_ddl_from_database():
    """
    Extract DDL from the DVD Rental PostgreSQL database
    """
    # Database connection parameters
    db_url = "postgresql://postgres:admin@localhost/dvdrental"
    
    try:
        # Connect to database
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        ddl_statements = []
        ddl_statements.append("-- DVD Rental Database DDL")
        ddl_statements.append("-- Generated from PostgreSQL database")
        ddl_statements.append("-- Date: " + str(__import__('datetime').datetime.now()))
        ddl_statements.append("")
        
        # Get all tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        
        for (table_name,) in tables:
            ddl_statements.append(f"-- Table: {table_name}")
            ddl_statements.append(f"CREATE TABLE {table_name} (")
            
            # Get column information
            cursor.execute("""
                SELECT 
                    column_name,
                    data_type,
                    character_maximum_length,
                    is_nullable,
                    column_default
                FROM information_schema.columns 
                WHERE table_name = %s 
                AND table_schema = 'public'
                ORDER BY ordinal_position;
            """, (table_name,))
            
            columns = cursor.fetchall()
            column_definitions = []
            
            for col in columns:
                col_name, data_type, max_length, is_nullable, default = col
                
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
                    # Handle custom types
                    cursor.execute("""
                        SELECT udt_name FROM information_schema.columns 
                        WHERE table_name = %s AND column_name = %s
                    """, (table_name, col_name))
                    udt_result = cursor.fetchone()
                    if udt_result:
                        col_def += udt_result[0].upper()
                    else:
                        col_def += data_type.upper()
                else:
                    col_def += data_type.upper()
                
                # Handle nullability
                if is_nullable == 'NO':
                    col_def += " NOT NULL"
                
                # Handle default values
                if default:
                    if 'nextval' in default:
                        col_def += " SERIAL"
                    else:
                        col_def += f" DEFAULT {default}"
                
                column_definitions.append(col_def)
            
            ddl_statements.append(",\n".join(column_definitions))
            ddl_statements.append(");")
            ddl_statements.append("")
        
        # Get primary keys
        ddl_statements.append("-- Primary Keys")
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
            ddl_statements.append(f"ALTER TABLE {table_name} ADD PRIMARY KEY ({columns});")
        
        ddl_statements.append("")
        
        # Get foreign keys
        ddl_statements.append("-- Foreign Keys")
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
            ddl_statements.append(f"ALTER TABLE {table_name} ADD CONSTRAINT {constraint_name} FOREIGN KEY ({column_name}) REFERENCES {foreign_table}({foreign_column});")
        
        ddl_statements.append("")
        
        # Get indexes
        ddl_statements.append("-- Indexes")
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
            ddl_statements.append(f"{index_def};")
        
        cursor.close()
        conn.close()
        
        return "\n".join(ddl_statements)
        
    except Exception as e:
        return f"Error extracting DDL: {str(e)}"

if __name__ == "__main__":
    ddl = extract_ddl_from_database()
    
    # Save to file
    with open("dvd_rental_ddl.sql", "w") as f:
        f.write(ddl)
    
    print("DDL extracted and saved to dvd_rental_ddl.sql")
    print("\nFirst few lines:")
    print(ddl[:500] + "...")
