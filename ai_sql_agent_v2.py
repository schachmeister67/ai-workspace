"""
AI SQL Agent v2 - Streamlined SQL Generation Agent

This module provides AI-powered SQL query generation for the DVD Rental database.
The LLM generates SQL queries based on natural language input and DDL schema,
while SQL execution is handled by the separate sql_execution_api.py module.

Key Features:
- Natural language to SQL conversion using Gemini AI
- DDL schema-aware query generation
- SQL validation and syntax checking
- Modular design with separated concerns
"""

import os
import requests
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from extract_ddl import extract_ddl_from_database
from typing import Dict, Any, Optional
import logging

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

# SQL Execution API configuration
SQL_API_BASE_URL = "http://localhost:8001"

# Extract DDL once at startup for enhanced query generation
try:
    DATABASE_DDL = extract_ddl_from_database()
    logger.info("DDL extracted successfully for enhanced query generation")
except Exception as e:
    logger.warning(f"Could not extract DDL: {e}")
    DATABASE_DDL = "DDL not available"


class SQLGenerationRequest(BaseModel):
    """Request model for SQL generation"""
    query: str = Field(description="Natural language query to convert to SQL")
    include_explanation: bool = Field(default=False, description="Include explanation of the generated SQL")


class SQLGenerationResponse(BaseModel):
    """Response model for SQL generation"""
    sql_query: str = Field(description="Generated SQL query")
    explanation: Optional[str] = Field(default=None, description="Explanation of the SQL query")
    validation_status: str = Field(description="Validation status: 'valid', 'warning', or 'error'")
    validation_message: Optional[str] = Field(default=None, description="Validation details")


class QueryExecutionResponse(BaseModel):
    """Response model for complete query processing"""
    natural_query: str = Field(description="Original natural language query")
    sql_query: str = Field(description="Generated SQL query")
    execution_result: Any = Field(description="Results from SQL execution")
    execution_success: bool = Field(description="Whether SQL execution was successful")
    execution_error: Optional[str] = Field(default=None, description="Execution error message if any")
    rows_affected: Optional[int] = Field(default=None, description="Number of rows affected/returned")
    execution_time_ms: Optional[float] = Field(default=None, description="Execution time in milliseconds")


def generate_sql_query(natural_query: str, include_explanation: bool = False) -> SQLGenerationResponse:
    """
    Generate SQL query from natural language input using DDL-enhanced prompting.
    
    Args:
        natural_query: Natural language query to convert
        include_explanation: Whether to include explanation of the generated SQL
        
    Returns:
        SQLGenerationResponse with generated SQL and validation status
    """
    
    # Enhanced system prompt with DDL knowledge
    system_prompt = f"""You are an expert SQL query generator specialized in PostgreSQL for the DVD Rental database.
You have complete knowledge of the database schema through the DDL provided below.

DATABASE SCHEMA (DDL):
{DATABASE_DDL}

Your task is to convert natural language queries into precise PostgreSQL SQL statements.

Guidelines:
- Generate syntactically correct PostgreSQL queries
- Use proper table and column names from the schema above
- Handle joins correctly based on foreign key relationships
- Use appropriate PostgreSQL functions and syntax
- For system queries (database name, version), use PostgreSQL system functions
- Return only the SQL query without additional commentary
- Ensure queries are efficient and follow best practices

Common DVD Rental database patterns:
- Actor and film relationships via film_actor table
- Customer rental history via rental and customer tables  
- Film categories via film_category and category tables
- Store inventory via inventory and store tables
- Payment transactions via payment table
- Geographic data via country, city, address tables

IMPORTANT: Return ONLY the SQL query, no explanation or additional text unless specifically requested.
"""

    if include_explanation:
        system_prompt += "\n\nIf explanation is requested, provide a brief explanation after the SQL query, separated by a newline and starting with 'EXPLANATION:'."

    try:
        # Create the full prompt
        full_prompt = f"{system_prompt}\n\nNatural language query: {natural_query}"
        
        # Generate SQL using LLM
        response = llm.invoke([HumanMessage(content=full_prompt)])
        generated_content = response.content.strip()
        
        # Parse response (extract SQL and optional explanation)
        if include_explanation and "EXPLANATION:" in generated_content:
            parts = generated_content.split("EXPLANATION:", 1)
            sql_query = parts[0].strip()
            explanation = parts[1].strip()
        else:
            sql_query = generated_content
            explanation = None if not include_explanation else None
            
        # Clean SQL query
        sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
        
        # Basic validation
        validation_result = validate_sql_syntax(sql_query)
        
        return SQLGenerationResponse(
            sql_query=sql_query,
            explanation=explanation,
            validation_status=validation_result["status"],
            validation_message=validation_result["message"]
        )
        
    except Exception as e:
        logger.error(f"Error generating SQL query: {e}")
        return SQLGenerationResponse(
            sql_query="",
            explanation=None,
            validation_status="error",
            validation_message=f"SQL generation failed: {str(e)}"
        )


def validate_sql_syntax(sql_query: str) -> Dict[str, str]:
    """
    Perform basic SQL syntax validation.
    
    Args:
        sql_query: SQL query to validate
        
    Returns:
        Dictionary with validation status and message
    """
    if not sql_query or not sql_query.strip():
        return {"status": "error", "message": "Empty SQL query"}
    
    sql_upper = sql_query.upper().strip()
    
    # Basic syntax checks
    if not any(keyword in sql_upper for keyword in ["SELECT", "INSERT", "UPDATE", "DELETE", "WITH"]):
        return {"status": "warning", "message": "Query doesn't appear to contain standard SQL keywords"}
    
    # Check for balanced parentheses
    if sql_query.count("(") != sql_query.count(")"):
        return {"status": "warning", "message": "Unbalanced parentheses detected"}
    
    # Check for basic SQL injection patterns (simple check)
    suspicious_patterns = ["DROP TABLE", "DELETE FROM", "TRUNCATE", "DROP DATABASE"]
    if any(pattern in sql_upper for pattern in suspicious_patterns):
        return {"status": "warning", "message": "Query contains potentially destructive operations"}
    
    return {"status": "valid", "message": "Basic syntax validation passed"}


def execute_sql_via_api(sql_query: str) -> Dict[str, Any]:
    """
    Execute SQL query using the sql_execution_api.py service.
    
    Args:
        sql_query: SQL query to execute
        
    Returns:
        Execution results from the API
    """
    try:
        response = requests.post(
            f"{SQL_API_BASE_URL}/execute",
            json={"sql": sql_query},
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "result": None,
                "rows_affected": 0,
                "success": False,
                "error": f"API error: HTTP {response.status_code}",
                "execution_time_ms": 0
            }
            
    except requests.exceptions.RequestException as e:
        return {
            "result": None,
            "rows_affected": 0,
            "success": False,
            "error": f"Connection error: {str(e)}",
            "execution_time_ms": 0
        }


def check_api_availability() -> bool:
    """
    Check if the SQL execution API is available.
    
    Returns:
        True if API is available, False otherwise
    """
    try:
        response = requests.get(f"{SQL_API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def process_natural_language_query(natural_query: str, include_explanation: bool = False) -> QueryExecutionResponse:
    """
    Complete pipeline: Generate SQL from natural language and execute it.
    
    Args:
        natural_query: Natural language query to process
        include_explanation: Whether to include SQL explanation
        
    Returns:
        QueryExecutionResponse with complete results
    """
    
    # Check API availability
    if not check_api_availability():
        return QueryExecutionResponse(
            natural_query=natural_query,
            sql_query="",
            execution_result=None,
            execution_success=False,
            execution_error="SQL execution API is not available. Please start sql_execution_api.py",
            rows_affected=None,
            execution_time_ms=None
        )
    
    # Generate SQL query
    generation_result = generate_sql_query(natural_query, include_explanation)
    
    if generation_result.validation_status == "error":
        return QueryExecutionResponse(
            natural_query=natural_query,
            sql_query=generation_result.sql_query,
            execution_result=None,
            execution_success=False,
            execution_error=generation_result.validation_message,
            rows_affected=None,
            execution_time_ms=None
        )
    
    # Execute SQL query
    execution_result = execute_sql_via_api(generation_result.sql_query)
    
    return QueryExecutionResponse(
        natural_query=natural_query,
        sql_query=generation_result.sql_query,
        execution_result=execution_result["result"],
        execution_success=execution_result["success"],
        execution_error=execution_result["error"],
        rows_affected=execution_result.get("rows_affected"),
        execution_time_ms=execution_result.get("execution_time_ms")
    )


def get_database_info() -> Dict[str, Any]:
    """
    Get basic database information via the execution API.
    
    Returns:
        Database information including tables and connection status
    """
    if not check_api_availability():
        return {"error": "SQL execution API is not available"}
    
    try:
        response = requests.get(f"{SQL_API_BASE_URL}/tables", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API error: HTTP {response.status_code}"}
    except Exception as e:
        return {"error": f"Failed to get database info: {str(e)}"}


def get_table_schema(table_name: str) -> Dict[str, Any]:
    """
    Get schema information for a specific table via the execution API.
    
    Args:
        table_name: Name of the table to inspect
        
    Returns:
        Table schema information
    """
    if not check_api_availability():
        return {"error": "SQL execution API is not available"}
    
    try:
        response = requests.get(f"{SQL_API_BASE_URL}/schema/{table_name}", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API error: HTTP {response.status_code}"}
    except Exception as e:
        return {"error": f"Failed to get table schema: {str(e)}"}


# Legacy compatibility function
def process_query(message: str) -> dict:
    """
    Legacy compatibility function for existing code.
    
    Args:
        message: Natural language query
        
    Returns:
        Dictionary with sql_query, result, and json_result keys for compatibility
    """
    result = process_natural_language_query(message)
    
    # Format for legacy compatibility
    return {
        "sql_query": result.sql_query,
        "result": result.execution_result if result.execution_success else f"Error: {result.execution_error}",
        "json_result": result.execution_result if result.execution_success else None
    }


if __name__ == "__main__":
    # Simple test when run directly
    print("AI SQL Agent v2 - Testing")
    print("=" * 50)
    
    # Check API availability
    if not check_api_availability():
        print("❌ SQL Execution API is not available!")
        print("Please start the API with: python sql_execution_api.py")
        exit(1)
    
    print("✅ SQL Execution API is available")
    
    # Test query
    test_query = "How many actors are in the database?"
    print(f"\nTesting with query: '{test_query}'")
    print("-" * 50)
    
    result = process_natural_language_query(test_query, include_explanation=True)
    
    print(f"Generated SQL: {result.sql_query}")
    print(f"Execution Success: {result.execution_success}")
    print(f"Execution Time: {result.execution_time_ms}ms")
    print(f"Rows Affected: {result.rows_affected}")
    print(f"Result: {result.execution_result}")
    
    if result.execution_error:
        print(f"Error: {result.execution_error}")
