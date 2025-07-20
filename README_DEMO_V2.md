# Demo v2 - AI SQL Assistant with Enhanced Table Formatting

This Streamlit application provides a user-friendly interface for querying the DVD Rental database using natural language. It integrates with the modular `ai_sql_agent_v2.py` backend for SQL generation and execution.

## Features

- **Natural Language Queries**: Enter queries in plain English
- **Formatted Table Results**: Results are displayed as clean, left-aligned tables
- **Multiple View Tabs**: 
  - **Result**: Formatted table view of query results
  - **JSON**: Raw JSON response data
  - **SQL Statement**: Generated SQL query with syntax highlighting
  - **ERD Diagram**: Database entity relationship diagram
- **Error Handling**: Clear error messages for failed queries
- **Modular Architecture**: Uses separated SQL generation and execution services

## Architecture

```
User Input → demo_v2.py → ai_sql_agent_v2.py → sql_execution_api.py → PostgreSQL
                ↓
           Formatted Table Display
```

## Key Improvements Over Original Demo

### Table Formatting
- **Pandas DataFrames**: Automatic conversion for structured display
- **Left-aligned Values**: Clean column alignment
- **Column Name Cleanup**: Underscores replaced with spaces, title case
- **Fallback Formatting**: Manual table formatting if DataFrame conversion fails
- **Error Message Display**: Clear presentation of error messages

### Response Processing
- **Robust Data Handling**: Supports various response formats
- **Empty Result Handling**: Clear "No results found" messages
- **JSON Display**: Proper JSON formatting for structured data
- **SQL Syntax Highlighting**: Code highlighting for generated SQL

## Usage

### Prerequisites
1. **SQL Execution API**: Must be running on port 8001
   ```bash
   python sql_execution_api.py
   ```

2. **Environment Setup**: Required environment variables
   - `GOOGLE_API_KEY`: For Gemini AI integration
   - Database connection variables (handled by sql_execution_api.py)

### Starting the Application
```bash
streamlit run demo_v2.py --server.port 8502
```

### Example Queries
- "How many actors are in the database?"
- "What are the top 5 most rented movies?"
- "Show me all categories"
- "Which customers have rented the most movies?"
- "What is the average rental duration by category?"

## File Structure

```
demo_v2.py                 # Main Streamlit application
ai_sql_agent_v2.py         # SQL generation service
sql_execution_api.py       # SQL execution service  
images/
  ERD_DVD_RENTAL.png      # Database schema diagram
```

## Response Format

The application processes responses from `ai_sql_agent_v2.py`:

```python
{
    "sql_query": "SELECT COUNT(*) FROM actor;",
    "result": [{"count": 200}],
    "json_result": [{"count": 200}]
}
```

### Result Types
- **List of Dictionaries**: Query results → Formatted table
- **Error Strings**: Error messages → Displayed as text
- **Empty Lists**: No results → "No results found" message

## Table Formatting Logic

1. **Check for Error Messages**: Display directly if error
2. **Convert to DataFrame**: Use pandas for structured display
3. **Clean Column Names**: Replace underscores, apply title case
4. **Fallback Formatting**: Manual table creation if needed
5. **Handle Empty Results**: Show appropriate message

## UI Components

### Main Interface
- **Title**: "Search for Data AI Assistant"
- **Text Input**: Natural language query input
- **Tab Navigation**: Four distinct result views

### Tab Content
- **Result Tab**: Primary formatted table display
- **JSON Tab**: Raw structured data with null handling
- **SQL Tab**: Generated query with syntax highlighting  
- **ERD Tab**: Interactive database schema diagram

## Error Handling

### API Connection Issues
- Detects if sql_execution_api.py is not running
- Displays clear error messages to users
- Graceful degradation for missing services

### Query Processing Errors
- SQL syntax errors from generated queries
- Database connection issues
- Invalid query responses
- Timeout handling for long-running queries

## Testing

Use `test_demo_integration.py` to verify the integration:

```bash
python test_demo_integration.py
```

This will test various query types and response formats.

## Development Notes

### Key Functions

#### `format_result_as_table(result)`
- Main formatting function for query results
- Handles multiple data types and formats
- Returns pandas DataFrame or formatted string

#### Response Processing
- Extracts `sql_query`, `result`, and `json_result`
- Routes each component to appropriate display tab
- Handles null/missing data gracefully

### Dependencies
- `streamlit`: Web application framework
- `pandas`: Data manipulation and display
- `PIL`: Image processing for ERD diagram
- `ai_sql_agent_v2`: SQL generation service

## Comparison with Original Demo

| Feature | demo.py | demo_v2.py |
|---------|---------|------------|
| UI Layout | ✅ Same | ✅ Same |
| Tab Structure | ✅ Same | ✅ Same |
| Table Formatting | Basic | Enhanced |
| Error Handling | Basic | Robust |
| Data Display | st.write() | Formatted tables |
| JSON Handling | Basic | Null-safe |
| SQL Display | Basic | Syntax highlighted |

## Troubleshooting

### Common Issues
1. **"SQL execution API is not available"**: Start sql_execution_api.py first
2. **Import errors**: Ensure all dependencies are installed
3. **ERD image not found**: Verify images/ERD_DVD_RENTAL.png exists
4. **Port conflicts**: Use different port with --server.port flag

### Debug Mode
Add debug information by modifying the query display:
```python
st.write("Debug - Response:", response)  # Add after process_query()
```

This enhanced demo maintains the same simple, user-friendly interface while providing robust table formatting and error handling for the modular AI SQL agent architecture.
