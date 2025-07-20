# DVD Rental SQL Execution API

A standalone FastAPI application for direct SQL execution against the DVD Rental PostgreSQL database. This API provides raw SQL execution capabilities without AI processing - just direct database interaction with comprehensive error handling and information endpoints.

## Features

### ✅ **Core Functionality**
- **Direct SQL Execution**: Execute any valid SQL statement against the database
- **Database Connection Management**: Automatic connection handling with health checks
- **Comprehensive Error Handling**: Detailed error messages and graceful failure handling
- **Performance Metrics**: Execution time measurement for all queries
- **Row Count Tracking**: Automatic detection of affected/returned rows

### ✅ **Database Information**
- **Schema Introspection**: Get detailed information about tables and columns
- **Relationship Mapping**: Primary keys, foreign keys, and constraints
- **Table Statistics**: Row counts and basic table information
- **Query Examples**: Built-in examples for common operations

### ✅ **Developer Tools**
- **Interactive Documentation**: Auto-generated Swagger UI at `/docs`
- **Query Builder Help**: Guidance for constructing effective queries
- **Error Diagnostics**: Clear error messages for debugging
- **Request/Response Validation**: Type-safe API with Pydantic models

## Installation and Setup

### Prerequisites
- Python 3.8+
- PostgreSQL DVD Rental database
- Required Python packages (see `requirements.txt`)

### Environment Setup
Create a `.env` file with your database connection:
```env
DATABASE_URL=postgresql://username:password@localhost/dvdrental
```

### Start the Server
```bash
# Using Python directly
python sql_execution_api.py

# Using the batch file (Windows)
start_sql_execution_api.bat

# Using uvicorn directly
python -m uvicorn sql_execution_api:app --host 127.0.0.1 --port 8001
```

## API Endpoints

### **Core Endpoints**

#### `GET /` - API Information
Returns basic information about the API and available endpoints.

#### `GET /health` - Health Check
Tests database connectivity and returns server status.
```bash
curl http://localhost:8001/health
```

#### `POST /execute` - Execute SQL Statement
Execute any SQL statement against the database.
```bash
curl -X POST "http://localhost:8001/execute" \
     -H "Content-Type: application/json" \
     -d '{"sql": "SELECT COUNT(*) FROM actor;", "description": "Count actors"}'
```

**Request Body:**
```json
{
  "sql": "SELECT * FROM actor LIMIT 5;",
  "description": "Get first 5 actors (optional)"
}
```

**Response:**
```json
{
  "result": [["Penelope", "Guiness"], ["Nick", "Wahlberg"], ...],
  "success": true,
  "error": null,
  "rows_affected": 5,
  "execution_time_ms": 2.75
}
```

### **Database Information Endpoints**

#### `GET /database-info` - Database Overview
Get general database information including name and table count.

#### `GET /tables` - List All Tables
Returns all tables with row counts.
```bash
curl http://localhost:8001/tables
```

#### `GET /table-schema/{table_name}` - Table Schema
Get detailed schema information for a specific table.
```bash
curl http://localhost:8001/table-schema/actor
```

### **Helper Endpoints**

#### `GET /examples` - Query Examples
Get example SQL queries organized by complexity level.

#### `GET /query-builder` - Query Building Help
Get guidance on database structure and common query patterns.

## Usage Examples

### Basic Queries
```bash
# Count records
curl -X POST "http://localhost:8001/execute" \
     -H "Content-Type: application/json" \
     -d '{"sql": "SELECT COUNT(*) FROM film;"}'

# Simple selection
curl -X POST "http://localhost:8001/execute" \
     -H "Content-Type: application/json" \
     -d '{"sql": "SELECT title, release_year FROM film LIMIT 10;"}'
```

### Advanced Queries
```bash
# Join with aggregation
curl -X POST "http://localhost:8001/execute" \
     -H "Content-Type: application/json" \
     -d '{
       "sql": "SELECT c.name, COUNT(*) as film_count FROM category c JOIN film_category fc ON c.category_id = fc.category_id GROUP BY c.name ORDER BY film_count DESC;",
       "description": "Films per category"
     }'

# Complex multi-table join
curl -X POST "http://localhost:8001/execute" \
     -H "Content-Type: application/json" \
     -d '{
       "sql": "SELECT c.first_name, c.last_name, f.title FROM customer c JOIN rental r ON c.customer_id = r.customer_id JOIN inventory i ON r.inventory_id = i.inventory_id JOIN film f ON i.film_id = f.film_id LIMIT 5;",
       "description": "Customer rental history"
     }'
```

## Database Schema Overview

The DVD Rental database contains the following key tables:

### **Core Entities**
- `actor` - Movie actors (200 records)
- `film` - Movie details (1000 records)
- `customer` - Customer information (599 records)
- `rental` - Rental transactions (16,044 records)
- `payment` - Payment records (14,596 records)

### **Relationship Tables**
- `film_actor` - Links films to actors
- `film_category` - Links films to categories  
- `inventory` - Store inventory of films

### **Reference Tables**
- `category` - Film categories (Action, Comedy, Drama, etc.)
- `language` - Film languages
- `store` - Store locations (2 stores)
- `staff` - Store staff
- `address`, `city`, `country` - Geographic data

## Error Handling

The API provides comprehensive error handling:

### **SQL Errors**
```json
{
  "result": null,
  "success": false,
  "error": "relation \"nonexistent_table\" does not exist",
  "rows_affected": null,
  "execution_time_ms": null
}
```

### **Connection Errors**
```json
{
  "result": null,
  "success": false,
  "error": "Database connection not available"
}
```

### **Validation Errors**
```json
{
  "result": null,
  "success": false,
  "error": "SQL query cannot be empty"
}
```

## Performance Features

- **Execution Timing**: All queries include execution time in milliseconds
- **Row Counting**: Automatic detection of affected/returned rows
- **Connection Pooling**: Efficient database connection management
- **Query Optimization**: Direct SQL execution without processing overhead

## Security Considerations

- **SQL Injection Protection**: Uses parameterized queries where applicable
- **Error Information**: Detailed errors for development, without exposing sensitive data
- **Connection Management**: Secure database connection handling
- **Input Validation**: Comprehensive request validation

## Testing

Run the comprehensive test suite:
```bash
python test_sql_execution_api.py
```

The test suite covers:
- Health check functionality
- Database information retrieval
- SQL execution with various query types
- Error handling and edge cases
- Performance metrics
- Schema introspection

## API Response Models

### SQLExecutionResponse
```python
{
  "result": Any,                    # Query results
  "success": bool,                  # Execution success status
  "error": Optional[str],           # Error message if any
  "rows_affected": Optional[int],   # Number of rows affected/returned
  "execution_time_ms": Optional[float]  # Execution time in milliseconds
}
```

### DatabaseInfo
```python
{
  "database_name": str,     # Name of the database
  "tables": List[str],      # List of table names
  "connection_status": str  # Connection status
}
```

## Architecture

```
HTTP Request
     ↓
FastAPI Application (sql_execution_api.py)
     ↓
LangChain SQLDatabase
     ↓
PostgreSQL Database (DVD Rental)
```

This API is completely self-contained and does not depend on any AI processing modules. It provides direct, raw access to the DVD Rental database through a clean REST interface.

## Comparison with AI SQL Agent

| Feature | SQL Execution API | AI SQL Agent API |
|---------|-------------------|------------------|
| **Purpose** | Raw SQL execution | Natural language to SQL |
| **Dependencies** | Database only | AI models + Database |
| **Query Input** | Valid SQL statements | Natural language |
| **Processing** | Direct execution | AI processing pipeline |
| **Performance** | ~2-5ms per query | ~500-2000ms per query |
| **Use Case** | Developers, direct DB access | End users, conversational interface |

Both APIs can run simultaneously on different ports (8000 for AI agent, 8001 for SQL execution) and serve different use cases within the same application ecosystem.
