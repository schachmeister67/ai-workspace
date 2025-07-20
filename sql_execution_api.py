"""
SQL Execution API - Self-contained FastAPI server for executing SQL statements
against the DVD Rental database.

This API provides direct SQL execution capabilities without any AI or agent dependencies.
It uses pure psycopg2 for database connections.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import os
import json
import time
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import logging

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SQL Execution API",
    description="Direct SQL execution API for the DVD Rental database (no AI dependencies)",
    version="1.0.0"
)

class SQLRequest(BaseModel):
    sql: str
    description: Optional[str] = None

class SQLResponse(BaseModel):
    result: Any
    rows_affected: Optional[int] = None
    success: bool
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None

def get_database_connection():
    """Get a database connection using psycopg2"""
    try:
        return psycopg2.connect(os.getenv("DATABASE_URL"))
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

def execute_sql_query(sql_query: str):
    """Execute a SQL query and return results"""
    start_time = time.time()
    
    conn = None
    cursor = None
    try:
        conn = get_database_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Clean the SQL query
        sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
        
        if not sql_query:
            raise ValueError("SQL query cannot be empty")
        
        # Execute the query
        cursor.execute(sql_query)
        
        # Get execution time
        execution_time = (time.time() - start_time) * 1000
        
        # Handle different types of queries
        if cursor.description:
            # SELECT query - fetch results
            rows = cursor.fetchall()
            # Convert RealDict objects to regular dictionaries for JSON serialization
            result = []
            for row in rows:
                result.append(dict(row))
            rows_affected = len(result)
        else:
            # INSERT, UPDATE, DELETE, etc.
            rows_affected = cursor.rowcount
            result = {"message": f"Query executed successfully. {rows_affected} rows affected."}
        
        conn.commit()
        
        return {
            "result": result,
            "rows_affected": rows_affected,
            "success": True,
            "error": None,
            "execution_time_ms": execution_time
        }
        
    except Exception as e:
        if conn:
            conn.rollback()
        return {
            "result": None,
            "rows_affected": 0,
            "success": False,
            "error": str(e),
            "execution_time_ms": (time.time() - start_time) * 1000
        }
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "SQL Execution API for DVD Rental Database",
        "version": "1.0.0",
        "description": "Direct SQL execution without AI dependencies",
        "endpoints": {
            "/execute": "Execute SQL statements directly",
            "/tables": "Get list of tables and their info",
            "/schema/{table_name}": "Get schema information for a specific table",
            "/health": "Health check endpoint"
        }
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    try:
        result = execute_sql_query("SELECT 1 as test")
        if result["success"]:
            return {
                "status": "healthy",
                "database": "connected",
                "test_result": result["result"]
            }
        else:
            raise HTTPException(status_code=500, detail=f"Database test failed: {result['error']}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.post("/execute", response_model=SQLResponse)
async def execute_sql(request: SQLRequest):
    """
    Execute a SQL statement against the DVD Rental database.
    Supports SELECT, INSERT, UPDATE, DELETE, and other SQL operations.
    """
    result = execute_sql_query(request.sql)
    
    return SQLResponse(
        result=result["result"],
        rows_affected=result["rows_affected"],
        success=result["success"],
        error=result["error"],
        execution_time_ms=result["execution_time_ms"]
    )

@app.get("/tables")
async def get_tables():
    """Get list of all tables with row counts and basic information"""
    try:
        # Get table information
        tables_query = """
            SELECT 
                table_name
            FROM information_schema.tables
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """
        
        result = execute_sql_query(tables_query)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["error"])
        
        tables = []
        for table_data in result["result"]:
            table_name = table_data["table_name"]
            
            # Get actual row count for each table
            count_result = execute_sql_query(f"SELECT COUNT(*) as count FROM \"{table_name}\"")
            row_count = count_result["result"][0]["count"] if count_result["success"] else 0
            
            # Get column count
            columns_query = f"""
                SELECT COUNT(*) as column_count
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = '{table_name}';
            """
            
            columns_result = execute_sql_query(columns_query)
            column_count = columns_result["result"][0]["column_count"] if columns_result["success"] else 0
            
            tables.append({
                "table_name": table_name,
                "row_count": row_count,
                "column_count": column_count
            })
        
        return {
            "database": "dvdrental",
            "table_count": len(tables),
            "tables": tables
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving tables: {str(e)}")

@app.get("/schema/{table_name}")
async def get_table_schema(table_name: str):
    """Get detailed schema information for a specific table"""
    try:
        # Get column information
        columns_query = f"""
            SELECT 
                column_name,
                data_type,
                character_maximum_length,
                is_nullable,
                column_default,
                ordinal_position
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = '{table_name}'
            ORDER BY ordinal_position;
        """
        
        columns_result = execute_sql_query(columns_query)
        
        if not columns_result["success"]:
            raise HTTPException(status_code=500, detail=columns_result["error"])
        
        if not columns_result["result"]:
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")
        
        # Get row count
        count_result = execute_sql_query(f"SELECT COUNT(*) as count FROM \"{table_name}\"")
        row_count = count_result["result"][0]["count"] if count_result["success"] else 0
        
        # Get primary key information
        pk_query = f"""
            SELECT column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu 
                ON tc.constraint_name = kcu.constraint_name
            WHERE tc.table_schema = 'public'
            AND tc.table_name = '{table_name}'
            AND tc.constraint_type = 'PRIMARY KEY';
        """
        
        pk_result = execute_sql_query(pk_query)
        primary_keys = [row["column_name"] for row in pk_result["result"]] if pk_result["success"] else []
        
        # Get foreign key information
        fk_query = f"""
            SELECT 
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu 
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage ccu 
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.table_schema = 'public'
            AND tc.table_name = '{table_name}'
            AND tc.constraint_type = 'FOREIGN KEY';
        """
        
        fk_result = execute_sql_query(fk_query)
        foreign_keys = fk_result["result"] if fk_result["success"] else []
        
        return {
            "table_name": table_name,
            "row_count": row_count,
            "columns": columns_result["result"],
            "primary_keys": primary_keys,
            "foreign_keys": foreign_keys
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving schema for table '{table_name}': {str(e)}")

@app.get("/examples")
async def get_example_queries():
    """Get example SQL queries for the DVD Rental database"""
    return {
        "basic_queries": [
            "SELECT COUNT(*) FROM actor;",
            "SELECT * FROM actor LIMIT 5;",
            "SELECT first_name, last_name FROM customer WHERE active = 1 LIMIT 10;"
        ],
        "join_queries": [
            """SELECT f.title, c.name as category 
               FROM film f 
               JOIN film_category fc ON f.film_id = fc.film_id 
               JOIN category c ON fc.category_id = c.category_id 
               LIMIT 10;""",
            """SELECT c.first_name, c.last_name, COUNT(r.rental_id) as rental_count
               FROM customer c
               LEFT JOIN rental r ON c.customer_id = r.customer_id
               GROUP BY c.customer_id, c.first_name, c.last_name
               ORDER BY rental_count DESC
               LIMIT 10;"""
        ],
        "aggregate_queries": [
            "SELECT c.name, COUNT(*) as film_count FROM category c JOIN film_category fc ON c.category_id = fc.category_id GROUP BY c.name ORDER BY film_count DESC;",
            "SELECT rating, AVG(rental_rate) as avg_rate, COUNT(*) as film_count FROM film GROUP BY rating ORDER BY avg_rate DESC;"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)  # Using port 8001 to avoid conflict with main API
