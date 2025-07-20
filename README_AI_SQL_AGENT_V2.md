# AI SQL Agent v2 - Documentation

## Overview

AI SQL Agent v2 is a streamlined, modular SQL generation system that separates concerns between AI-powered query generation and database execution. This version focuses on clean architecture and maintainable code.

## Architecture

```
Natural Language Input
         ↓
AI SQL Agent v2 (SQL Generation)
         ↓
Generated SQL Query
         ↓
SQL Execution API (Database Operations)
         ↓
Formatted Results
```

## Key Features

### ✅ **Modular Design**
- **SQL Generation**: LLM-powered natural language to SQL conversion
- **SQL Execution**: Dedicated API service for database operations
- **Clean Separation**: No database connections in the AI agent

### ✅ **Enhanced Query Generation**
- DDL schema-aware query generation using `extract_ddl.py`
- PostgreSQL-specific optimizations
- Context-aware table relationships
- System query support (database metadata, version info)

### ✅ **Comprehensive Validation**
- Syntax validation before execution
- Security checks for destructive operations
- API availability verification
- Error handling and recovery

### ✅ **Flexible Usage**
- Generate SQL only (no execution)
- Complete pipeline (generation + execution)
- Legacy compatibility mode
- Batch processing support

## Components

### Core Functions

#### `generate_sql_query(natural_query, include_explanation=False)`
Converts natural language to SQL using DDL-enhanced prompting.

**Parameters:**
- `natural_query` (str): Natural language query
- `include_explanation` (bool): Include SQL explanation

**Returns:** `SQLGenerationResponse` with generated SQL and validation status

#### `process_natural_language_query(natural_query, include_explanation=False)`
Complete pipeline: generates SQL and executes via API.

**Parameters:**
- `natural_query` (str): Natural language query
- `include_explanation` (bool): Include explanation

**Returns:** `QueryExecutionResponse` with complete results

#### `execute_sql_via_api(sql_query)`
Executes SQL using the separate sql_execution_api.py service.

**Parameters:**
- `sql_query` (str): SQL query to execute

**Returns:** Dictionary with execution results

### Utility Functions

#### `validate_sql_syntax(sql_query)`
Performs basic SQL syntax validation and security checks.

#### `check_api_availability()`
Verifies if the SQL execution API is running.

#### `get_database_info()`
Retrieves database metadata via the execution API.

#### `get_table_schema(table_name)`
Gets detailed schema information for a specific table.

## Usage Examples

### 1. SQL Generation Only

```python
from ai_sql_agent_v2 import generate_sql_query

# Generate SQL without execution
result = generate_sql_query(
    "Show me the top 5 actors by number of films",
    include_explanation=True
)

print(f"SQL: {result.sql_query}")
print(f"Explanation: {result.explanation}")
print(f"Valid: {result.validation_status}")
```

### 2. Complete Pipeline

```python
from ai_sql_agent_v2 import process_natural_language_query

# Generate and execute SQL
result = process_natural_language_query(
    "How many customers are from California?"
)

if result.execution_success:
    print(f"SQL: {result.sql_query}")
    print(f"Results: {result.execution_result}")
    print(f"Rows: {result.rows_affected}")
else:
    print(f"Error: {result.execution_error}")
```

### 3. Legacy Compatibility

```python
from ai_sql_agent_v2 import process_query

# Compatible with existing code
result = process_query("Count all actors")
print(f"SQL: {result['sql_query']}")
print(f"Result: {result['result']}")
```

### 4. Database Information

```python
from ai_sql_agent_v2 import get_database_info, get_table_schema

# Get database overview
db_info = get_database_info()
print(f"Tables: {db_info['table_count']}")

# Get specific table schema
schema = get_table_schema("actor")
print(f"Columns: {len(schema['columns'])}")
```

## Setup Requirements

### 1. Dependencies
```bash
pip install requests python-dotenv pydantic langchain-google-genai
```

### 2. Environment Configuration
Create `.env` file with:
```
DATABASE_URL=postgresql://username:password@localhost:5432/dvdrental
GOOGLE_API_KEY=your_gemini_api_key
```

### 3. Start SQL Execution API
```bash
python sql_execution_api.py
```

The API will run on `http://localhost:8001`

### 4. Test the Agent
```bash
python ai_sql_agent_v2.py
```

## Testing

### Comprehensive Test Suite
```bash
python test_ai_sql_agent_v2.py
```

This runs tests for:
- SQL generation only
- Complete pipeline with execution
- Database information retrieval
- Error handling and validation

### Manual Testing
```python
# Test individual components
from ai_sql_agent_v2 import *

# Check if API is running
print(f"API Available: {check_api_availability()}")

# Test SQL generation
sql_result = generate_sql_query("Count all films")
print(f"Generated: {sql_result.sql_query}")

# Test complete pipeline
full_result = process_natural_language_query("Show me 5 actors")
print(f"Success: {full_result.execution_success}")
```

## Configuration

### API Endpoint Configuration
```python
# Default configuration
SQL_API_BASE_URL = "http://localhost:8001"

# Custom configuration (modify in ai_sql_agent_v2.py)
SQL_API_BASE_URL = "http://your-api-server:8001"
```

### LLM Configuration
```python
# Default: Gemini 2.5 Flash
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

# Alternative models
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro")
```

## Error Handling

### Common Scenarios

1. **API Not Available**
   - Check: `check_api_availability()`
   - Solution: Start `sql_execution_api.py`

2. **DDL Extraction Failure**
   - Warning logged, continues with limited functionality
   - Check database connectivity

3. **SQL Generation Error**
   - Returns error status in response
   - Check input query and API key

4. **Execution Timeout**
   - 30-second timeout for SQL execution
   - 10-second timeout for metadata queries

## Performance Considerations

### SQL Generation
- Fast LLM inference (typically < 2 seconds)
- DDL loaded once at startup
- No database connections in agent

### Execution
- Handled by dedicated API service
- Connection pooling in execution layer
- Timing information provided

### Memory Usage
- Minimal memory footprint
- DDL cached in memory
- No database connection state

## Differences from v1

| Feature | v1 | v2 |
|---------|----|----|
| **Architecture** | Monolithic | Modular |
| **Database Access** | Direct LangChain | Dedicated API |
| **LLM Responsibility** | Generate + Execute | Generate Only |
| **Testing** | Complex | Simple Components |
| **Dependencies** | Heavy | Light |
| **Maintainability** | Coupled | Decoupled |

## Migration from v1

### Code Changes Needed
```python
# v1 Usage
from ai_sql_agent_ddl import process_query
result = process_query("query")

# v2 Usage (backward compatible)
from ai_sql_agent_v2 import process_query
result = process_query("query")  # Same interface!

# v2 New Features
from ai_sql_agent_v2 import process_natural_language_query
result = process_natural_language_query("query")  # Enhanced response
```

### Setup Changes
1. Start SQL execution API: `python sql_execution_api.py`
2. Update imports to use `ai_sql_agent_v2`
3. Optionally use new enhanced response format

## Best Practices

### 1. Development
- Test SQL generation separately from execution
- Use validation functions before execution
- Handle API availability gracefully

### 2. Production
- Run SQL execution API as a service
- Monitor API health and connectivity
- Use appropriate timeouts

### 3. Query Writing
- Be specific in natural language queries
- Reference table/column names when possible
- Use business terminology familiar to the domain

## Troubleshooting

### SQL Generation Issues
```python
# Debug SQL generation
result = generate_sql_query("your query", include_explanation=True)
print(f"Status: {result.validation_status}")
print(f"Message: {result.validation_message}")
```

### Execution Issues
```python
# Check API status
if not check_api_availability():
    print("Start SQL execution API first")

# Test direct API call
import requests
response = requests.get("http://localhost:8001/health")
print(response.json())
```

### DDL Issues
```python
# Check DDL extraction
from extract_ddl import extract_ddl_from_database
ddl = extract_ddl_from_database()
print(f"DDL Length: {len(ddl)}")
```

## Future Enhancements

- [ ] Query result caching
- [ ] Query optimization suggestions
- [ ] Support for multiple databases
- [ ] Advanced security validation
- [ ] Query performance analysis
- [ ] Visual query explanation

## Support

For issues or questions:
1. Check API availability: `check_api_availability()`
2. Review logs for error details
3. Test individual components separately
4. Verify environment configuration
