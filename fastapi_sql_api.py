from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv
from ai_sql_agent_ddl import process_query
from langchain_community.utilities import SQLDatabase

load_dotenv()

app = FastAPI(
    title="DVD Rental SQL API",
    description="API for executing SQL queries against the DVD Rental database",
    version="1.0.0"
)

# Initialize database connection
db = SQLDatabase.from_uri(os.getenv("DATABASE_URL"))

class QueryRequest(BaseModel):
    query: str
    description: Optional[str] = None

class QueryResponse(BaseModel):
    sql_query: str
    result: str
    json_result: Any
    success: bool
    error: Optional[str] = None

class DirectSQLRequest(BaseModel):
    sql: str
    description: Optional[str] = None

class DirectSQLResponse(BaseModel):
    result: Any
    success: bool
    error: Optional[str] = None

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "DVD Rental SQL API",
        "version": "1.0.0",
        "endpoints": {
            "/query": "Execute natural language queries (converted to SQL)",
            "/execute": "Execute direct SQL statements",
            "/health": "Health check endpoint"
        }
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    try:
        # Test database connection
        result = db.run_no_throw("SELECT 1 as test")
        return {
            "status": "healthy",
            "database": "connected",
            "test_query": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

@app.post("/query", response_model=QueryResponse)
async def execute_natural_language_query(request: QueryRequest):
    """
    Execute a natural language query against the DVD Rental database.
    The query will be converted to SQL using AI and then executed.
    """
    try:
        # Process the natural language query using the DDL-enhanced agent
        result = process_query(request.query)
        
        return QueryResponse(
            sql_query=result["sql_query"],
            result=result["result"],
            json_result=result["json_result"],
            success=True
        )
    
    except Exception as e:
        return QueryResponse(
            sql_query="",
            result="",
            json_result=None,
            success=False,
            error=str(e)
        )

@app.post("/execute", response_model=DirectSQLResponse)
async def execute_direct_sql(request: DirectSQLRequest):
    """
    Execute a direct SQL statement against the DVD Rental database.
    Use this endpoint when you already have a SQL query and want to execute it directly.
    """
    try:
        # Clean the SQL query
        sql_query = request.sql.replace("```sql", "").replace("```", "").strip()
        
        if not sql_query:
            raise ValueError("SQL query cannot be empty")
        
        # Execute the SQL query
        result = db.run_no_throw(sql_query)
        
        return DirectSQLResponse(
            result=result,
            success=True
        )
    
    except Exception as e:
        return DirectSQLResponse(
            result=None,
            success=False,
            error=str(e)
        )

@app.get("/schema")
async def get_database_schema():
    """
    Get information about the database schema including tables and their structures.
    """
    try:
        # Get list of tables
        tables_result = db.run_no_throw("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        
        # Get basic statistics
        stats_result = db.run_no_throw("""
            SELECT 
                'Tables' as metric, 
                COUNT(*) as count
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            
            UNION ALL
            
            SELECT 
                'Columns' as metric, 
                COUNT(*) as count
            FROM information_schema.columns 
            WHERE table_schema = 'public'
        """)
        
        return {
            "database": "dvdrental",
            "tables": tables_result,
            "statistics": stats_result,
            "schema_info": "Use /query endpoint to ask natural language questions about the data"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving schema: {str(e)}")

@app.get("/examples")
async def get_example_queries():
    """
    Get example queries that can be used with the /query endpoint.
    """
    return {
        "natural_language_examples": [
            "How many actors are in the database?",
            "What are the top 5 most popular film categories?",
            "Show me all customers from California",
            "What is the average rental duration for films?",
            "Which actor has appeared in the most films?",
            "What are the most expensive films to rent?",
            "How many rentals were made last month?",
            "Show me the store locations and their addresses"
        ],
        "direct_sql_examples": [
            "SELECT COUNT(*) FROM actor;",
            "SELECT name, COUNT(*) as film_count FROM category c JOIN film_category fc ON c.category_id = fc.category_id GROUP BY name ORDER BY film_count DESC LIMIT 5;",
            "SELECT first_name, last_name, email FROM customer WHERE address_id IN (SELECT address_id FROM address a JOIN city ci ON a.city_id = ci.city_id JOIN country co ON ci.country_id = co.country_id WHERE co.country = 'United States');"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
