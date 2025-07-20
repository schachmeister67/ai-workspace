import os
import subprocess
import sys
from dotenv import load_dotenv

load_dotenv()

def create_database_dump():
    """
    Create a complete SQL dump of the DVD Rental database using pg_dump
    """
    
    # Database connection parameters from .env
    host = "localhost"
    port = "5432"
    username = "postgres"
    password = "admin"
    database = "dvdrental"
    
    try:
        print("Creating complete database dump using pg_dump...")
        
        # Set environment variable for password
        env = os.environ.copy()
        env['PGPASSWORD'] = password
        
        # Run pg_dump command
        cmd = [
            'pg_dump',
            '-h', host,
            '-p', port,
            '-U', username,
            '-d', database,
            '--no-owner',
            '--no-privileges',
            '--clean',
            '--create',
            '--if-exists'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        
        if result.returncode == 0:
            # Save to file
            with open("dvd_rental_complete_dump.sql", "w", encoding='utf-8') as f:
                f.write(result.stdout)
            
            print("✅ Complete database dump saved to 'dvd_rental_complete_dump.sql'")
            print("\nThis file contains:")
            print("- DROP and CREATE DATABASE statements")
            print("- All custom types and functions")
            print("- All table definitions")
            print("- All constraints and indexes")
            print("- All data INSERT statements")
            print("- Proper dependency order")
            print("\n📋 To recreate the database:")
            print("1. Make sure PostgreSQL is running")
            print("2. Run: psql -U postgres -f dvd_rental_complete_dump.sql")
            print("3. The database will be fully recreated!")
            
            return True
        else:
            print(f"❌ Error running pg_dump: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ pg_dump not found. Please make sure PostgreSQL is installed and pg_dump is in your PATH.")
        print("\nAlternative: Try the manual extraction method...")
        return create_manual_dump()
    except Exception as e:
        print(f"❌ Error creating dump: {str(e)}")
        return False

def create_manual_dump():
    """
    Fallback method to create dump manually if pg_dump is not available
    """
    import psycopg2
    
    print("\nFalling back to manual extraction...")
    
    try:
        # Connect to database
        conn = psycopg2.connect("postgresql://postgres:admin@localhost/dvdrental")
        cursor = conn.cursor()
        
        sql_statements = []
        sql_statements.append("-- DVD Rental Database - Manual Recreation Script")
        sql_statements.append("-- Generated manually from PostgreSQL database")
        sql_statements.append("")
        sql_statements.append("-- Drop database if exists and create new one")
        sql_statements.append("DROP DATABASE IF EXISTS dvdrental;")
        sql_statements.append("CREATE DATABASE dvdrental;")
        sql_statements.append("\\c dvdrental;")
        sql_statements.append("")
        
        # Create custom enum type
        sql_statements.append("-- Custom types")
        sql_statements.append("CREATE TYPE mpaa_rating AS ENUM ('G','PG','PG-13','R','NC-17');")
        sql_statements.append("")
        
        # Get all tables
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        
        all_tables = [row[0] for row in cursor.fetchall()]
        
        # Tables in proper dependency order
        ordered_tables = ['country', 'city', 'address', 'category', 'language', 'actor', 'customer', 'staff', 'store', 'film', 'film_actor', 'film_category', 'inventory', 'rental', 'payment']
        
        # Add any missing tables
        for table in all_tables:
            if table not in ordered_tables:
                ordered_tables.append(table)
        
        # Create tables first
        sql_statements.append("-- CREATE TABLES")
        for table_name in ordered_tables:
            if table_name not in all_tables:
                continue
                
            # Get CREATE TABLE statement using a simpler approach
            cursor.execute(f"""
                SELECT 
                    'CREATE TABLE ' || table_name || ' (' ||
                    string_agg(
                        column_name || ' ' || 
                        CASE 
                            WHEN data_type = 'character varying' THEN 
                                CASE WHEN character_maximum_length IS NOT NULL 
                                     THEN 'VARCHAR(' || character_maximum_length || ')'
                                     ELSE 'VARCHAR' END
                            WHEN data_type = 'character' THEN 'CHAR(' || character_maximum_length || ')'
                            WHEN data_type = 'integer' THEN 'INTEGER'
                            WHEN data_type = 'smallint' THEN 'SMALLINT'
                            WHEN data_type = 'bigint' THEN 'BIGINT'
                            WHEN data_type = 'numeric' THEN 'NUMERIC'
                            WHEN data_type = 'boolean' THEN 'BOOLEAN'
                            WHEN data_type = 'date' THEN 'DATE'
                            WHEN data_type = 'timestamp without time zone' THEN 'TIMESTAMP'
                            WHEN data_type = 'text' THEN 'TEXT'
                            WHEN data_type = 'bytea' THEN 'BYTEA'
                            WHEN data_type = 'tsvector' THEN 'TSVECTOR'
                            WHEN data_type = 'USER-DEFINED' THEN 
                                CASE WHEN udt_name = 'mpaa_rating' THEN 'mpaa_rating'
                                     WHEN udt_name LIKE '_%' THEN SUBSTRING(udt_name FROM 2) || '[]'
                                     ELSE UPPER(udt_name) END
                            ELSE UPPER(data_type)
                        END ||
                        CASE WHEN is_nullable = 'NO' THEN ' NOT NULL' ELSE '' END ||
                        CASE WHEN column_default IS NOT NULL AND column_default NOT LIKE 'nextval%' 
                             THEN ' DEFAULT ' || column_default ELSE '' END
                        , ', ' ORDER BY ordinal_position
                    ) || ');'
                FROM information_schema.columns 
                WHERE table_name = '{table_name}' 
                AND table_schema = 'public'
                GROUP BY table_name;
            """)
            
            result = cursor.fetchone()
            if result:
                sql_statements.append(result[0])
                sql_statements.append("")
        
        # Add sequences
        sql_statements.append("-- SEQUENCES")
        for table_name in ordered_tables:
            if table_name not in all_tables:
                continue
                
            cursor.execute(f"""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = '{table_name}' 
                AND column_default LIKE 'nextval%'
            """)
            
            for (col,) in cursor.fetchall():
                seq_name = f"{table_name}_{col}_seq"
                sql_statements.append(f"CREATE SEQUENCE {seq_name};")
                sql_statements.append(f"ALTER TABLE {table_name} ALTER COLUMN {col} SET DEFAULT nextval('{seq_name}');")
        
        sql_statements.append("")
        
        # Add primary keys
        sql_statements.append("-- PRIMARY KEYS")
        cursor.execute("""
            SELECT 
                'ALTER TABLE ' || tc.table_name || ' ADD PRIMARY KEY (' || 
                string_agg(kcu.column_name, ', ' ORDER BY kcu.ordinal_position) || ');'
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu 
                ON tc.constraint_name = kcu.constraint_name 
                AND tc.table_schema = kcu.table_schema
            WHERE tc.constraint_type = 'PRIMARY KEY' 
            AND tc.table_schema = 'public'
            GROUP BY tc.table_name;
        """)
        
        for (pk_statement,) in cursor.fetchall():
            sql_statements.append(pk_statement)
        
        sql_statements.append("")
        
        # Insert data for each table
        sql_statements.append("-- INSERT DATA")
        for table_name in ordered_tables:
            if table_name not in all_tables:
                continue
                
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                
                if count > 0:
                    sql_statements.append(f"-- Data for {table_name} ({count} rows)")
                    
                    # Get column names
                    cursor.execute(f"""
                        SELECT column_name FROM information_schema.columns 
                        WHERE table_name = '{table_name}' AND table_schema = 'public'
                        ORDER BY ordinal_position
                    """)
                    columns = [row[0] for row in cursor.fetchall()]
                    
                    # Get all data
                    cursor.execute(f"SELECT * FROM {table_name} ORDER BY 1")
                    rows = cursor.fetchall()
                    
                    # Create INSERT statements in batches
                    batch_size = 100
                    for i in range(0, len(rows), batch_size):
                        batch = rows[i:i+batch_size]
                        
                        values_list = []
                        for row in batch:
                            formatted_values = []
                            for val in row:
                                if val is None:
                                    formatted_values.append("NULL")
                                elif isinstance(val, str):
                                    formatted_values.append(f"'{val.replace(chr(39), chr(39)+chr(39))}'")  # Escape quotes
                                elif isinstance(val, bool):
                                    formatted_values.append("TRUE" if val else "FALSE")
                                elif hasattr(val, 'isoformat'):
                                    formatted_values.append(f"'{val.isoformat()}'")
                                else:
                                    formatted_values.append(str(val))
                            values_list.append(f"({','.join(formatted_values)})")
                        
                        column_list = ','.join(columns)
                        values_str = ',\n'.join(values_list)
                        sql_statements.append(f"INSERT INTO {table_name} ({column_list}) VALUES\n{values_str};")
                        sql_statements.append("")
            
            except Exception as e:
                sql_statements.append(f"-- Error getting data for {table_name}: {str(e)}")
        
        # Add foreign keys
        sql_statements.append("-- FOREIGN KEYS")
        cursor.execute("""
            SELECT 
                'ALTER TABLE ' || tc.table_name || ' ADD CONSTRAINT ' || tc.constraint_name || 
                ' FOREIGN KEY (' || kcu.column_name || ') REFERENCES ' || 
                ccu.table_name || '(' || ccu.column_name || ');'
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu 
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage ccu 
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_schema = 'public';
        """)
        
        for (fk_statement,) in cursor.fetchall():
            sql_statements.append(fk_statement)
        
        sql_statements.append("")
        
        # Update sequences
        sql_statements.append("-- UPDATE SEQUENCES")
        for table_name in ordered_tables:
            if table_name not in all_tables:
                continue
                
            cursor.execute(f"""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = '{table_name}' 
                AND column_default LIKE 'nextval%'
            """)
            
            for (col,) in cursor.fetchall():
                seq_name = f"{table_name}_{col}_seq"
                sql_statements.append(f"SELECT setval('{seq_name}', COALESCE((SELECT MAX({col}) FROM {table_name}), 1));")
        
        sql_statements.append("")
        sql_statements.append("-- Database recreation complete!")
        
        cursor.close()
        conn.close()
        
        # Save to file
        with open("dvd_rental_complete_manual.sql", "w", encoding='utf-8') as f:
            f.write("\n".join(sql_statements))
        
        print("✅ Manual database dump saved to 'dvd_rental_complete_manual.sql'")
        print("\n📋 To recreate the database:")
        print("1. Run: psql -U postgres -f dvd_rental_complete_manual.sql")
        return True
        
    except Exception as e:
        print(f"❌ Error creating manual dump: {str(e)}")
        return False

if __name__ == "__main__":
    success = create_database_dump()
    if not success:
        print("\n🔄 Trying alternative method...")
        create_manual_dump()
