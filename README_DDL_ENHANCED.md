# DVD Rental Database AI SQL Agent - DDL Enhanced

This project contains an enhanced AI SQL agent that uses the DVD Rental database DDL (Data Definition Language) as a resource for more accurate SQL generation, plus a FastAPI-based REST API for executing SQL queries.

## New Files and Enhancements

### 1. DDL-Enhanced AI SQL Agent (`ai_sql_agent_ddl.py`)
- **Enhanced with DDL context**: Uses `extract_ddl.py` to load the complete database schema at startup
- **Improved query generation**: System prompts now include the full DDL, enabling more accurate SQL generation
- **Schema-aware**: Understands table relationships, column names, and data types from the DDL
- **All original functionality preserved**: Same API as the original agent with `process_query()` function

### 2. FastAPI SQL API (`fastapi_sql_api.py`)
A REST API that provides multiple endpoints for interacting with the DVD Rental database:

#### Endpoints:
- **GET `/`** - Root endpoint with API information
- **GET `/health`** - Health check and database connectivity test
- **POST `/query`** - Execute natural language queries (converted to SQL using AI)
- **POST `/execute`** - Execute direct SQL statements
- **GET `/schema`** - Get database schema information
- **GET `/examples`** - Get example queries for testing

#### Features:
- **Natural Language Processing**: Converts English queries to SQL using the DDL-enhanced agent
- **Direct SQL Execution**: Execute raw SQL statements directly
- **Error Handling**: Comprehensive error handling with meaningful error messages
- **Schema Information**: Provides database structure information
- **Interactive Documentation**: Auto-generated OpenAPI/Swagger documentation at `/docs`

### 3. Supporting Files
- **`start_sql_api.bat`** - Windows batch file to start the FastAPI server
- **`test_sql_api.py`** - Comprehensive test suite for all API endpoints
- **`extract_ddl.py`** - Original DDL extraction script (preserved)
- **`dvd_rental_ddl.sql`** - Generated DDL file (preserved)

## Installation and Setup

### Prerequisites
Ensure you have all dependencies installed:
```bash
pip install -r requirements.txt
```

### Database Setup
Make sure your `.env` file contains the correct database connection:
```env
DATABASE_URL=postgresql://postgres:admin@localhost/dvdrental
```

## Usage

### Option 1: Using the Enhanced AI SQL Agent Directly
```python
from ai_sql_agent_ddl import process_query

# Ask natural language questions
result = process_query("How many actors are in the database?")
print(f"SQL: {result['sql_query']}")
print(f"Result: {result['result']}")
print(f"Raw Data: {result['json_result']}")
```

### Option 2: Using the FastAPI REST API

#### Start the API Server
```bash
# Using Python directly
python -m uvicorn fastapi_sql_api:app --host 0.0.0.0 --port 8000

# Using the batch file (Windows)
start_sql_api.bat
```

#### Access the API
- **API Base URL**: http://localhost:8000
- **Interactive Documentation**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc

#### Example API Calls

**Natural Language Query:**
```bash
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "How many films are in each category?", "description": "Category breakdown"}'
```

**Direct SQL Execution:**
```bash
curl -X POST "http://localhost:8000/execute" \
     -H "Content-Type: application/json" \
     -d '{"sql": "SELECT COUNT(*) FROM customer;", "description": "Customer count"}'
```

**Get Schema Information:**
```bash
curl http://localhost:8000/schema
```

### Testing
Run the comprehensive test suite:
```bash
python test_sql_api.py
```

## Key Improvements Over Original Agent

### 1. DDL-Aware Query Generation
- **Before**: Agent had to query database schema for every request
- **After**: Agent loads complete schema at startup, enabling faster and more accurate queries

### 2. Enhanced Context Understanding
- **Before**: Limited understanding of table relationships
- **After**: Full knowledge of foreign keys, indexes, and column constraints

### 3. Better Error Handling
- **Before**: Basic error messages
- **After**: Schema-aware validation and detailed error reporting

### 4. REST API Access
- **Before**: Python function calls only
- **After**: HTTP REST API accessible from any programming language or tool

## API Response Formats

### Natural Language Query Response
```json
{
  "sql_query": "SELECT COUNT(*) FROM actor;",
  "result": "There are 200 actors in the database.",
  "json_result": [(200,)],
  "success": true,
  "error": null
}
```

### Direct SQL Execution Response
```json
{
  "result": [(1000,)],
  "success": true,
  "error": null
}
```

## Example Queries

### Natural Language Examples:
- "How many actors are in the database?"
- "What are the top 5 most popular film categories?"
- "Show me all customers from California"
- "Which actor has appeared in the most films?"
- "What is the average rental duration for films?"

### Direct SQL Examples:
- `SELECT COUNT(*) FROM film;`
- `SELECT c.name, COUNT(*) FROM category c JOIN film_category fc ON c.category_id = fc.category_id GROUP BY c.name ORDER BY COUNT(*) DESC LIMIT 5;`
- `SELECT first_name, last_name FROM actor ORDER BY last_name LIMIT 10;`

## Architecture

```
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│   FastAPI Server    │    │  ai_sql_agent_ddl.py │    │  DVD Rental Database │
│  (fastapi_sql_api)  │────│   (Enhanced Agent)   │────│    (PostgreSQL)     │
└─────────────────────┘    └──────────────────────┘    └─────────────────────┘
         │                            │                            │
         │                            │                            │
    HTTP REST API              LangGraph/LangChain           DDL Schema
    - /query                   + DDL Context                 - Tables
    - /execute                 + Enhanced Prompts            - Relationships
    - /schema                  + Error Handling              - Constraints
    - /examples                                              - Indexes
```

## Error Handling

The API provides comprehensive error handling:
- **Database Connection Errors**: Returned with 500 status code
- **SQL Syntax Errors**: Captured and returned in error field
- **Invalid Input**: Validated with detailed error messages
- **Agent Processing Errors**: Gracefully handled with fallback responses

## Performance Notes

- **DDL Loading**: Schema is loaded once at startup, not per request
- **Connection Pooling**: Database connections are efficiently managed
- **Background Processing**: Long-running queries are handled asynchronously
- **Memory Efficiency**: Raw results are captured for JSON serialization without duplication

This enhanced system provides a production-ready API for natural language database queries while maintaining all the functionality of the original AI SQL agent.
