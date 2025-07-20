# Demo_v2.py - AI SQL Assistant Workflow

## 🏗️ **Architecture Overview**

```
User Input → demo_v2.py → ai_sql_agent_v2.py → sql_execution_api.py → PostgreSQL
     ↓
Streamlit UI ← Formatted Tables ← Response Processing ← SQL Execution ← Database Query
```

> 📊 **For detailed visual diagrams, see [DEMO_V2_VISUAL_WORKFLOW.md](DEMO_V2_VISUAL_WORKFLOW.md)**

## 📋 **Step-by-Step Workflow**

### **1. Application Startup**
```python
# Dependencies loaded
import streamlit as st, pandas as pd, PIL, etc.

# AI agent imported
from ai_sql_agent_v2 import process_query

# UI initialized
st.title("Search for Data AI Assistant")
```

### **2. User Interface Setup**
- **Title**: "Search for Data AI Assistant"
- **Input Field**: Text input for natural language queries
- **4 Tabs Created**:
  - `Result` → Formatted table display
  - `JSON` → Raw JSON response
  - `SQL Statement` → Generated SQL with syntax highlighting
  - `ERD Diagram` → Database schema visualization

### **3. User Query Processing**
When user enters a query (e.g., "Show me the first 5 actors"):

```python
if user_input:
    # Call AI SQL agent
    response = process_query(user_input)
    
    # Extract response components
    sql_statement = response['sql_query']    # Generated SQL
    result = response['result']              # Query results
    json_result = response['json_result']    # JSON format
```

### **4. Behind the Scenes (AI Agent Chain)**

#### **4.1 ai_sql_agent_v2.py Processing:**
```
Natural Language → DDL-Enhanced Prompt → Gemini AI → SQL Generation
"Show me actors" → [DDL Schema Context] → LLM → "SELECT * FROM actor LIMIT 5;"
```

#### **4.2 SQL Execution API Call:**
```
Generated SQL → sql_execution_api.py → PostgreSQL → Raw Results
"SELECT * FROM actor..." → API Request → Database → [{"actor_id":1,"first_name":"Penelope"...}]
```

#### **4.3 Response Assembly:**
```python
{
    "sql_query": "SELECT actor_id, first_name, last_name FROM actor LIMIT 5;",
    "result": [
        {"actor_id": 1, "first_name": "Penelope", "last_name": "Guiness"},
        {"actor_id": 2, "first_name": "Nick", "last_name": "Wahlberg"},
        ...
    ],
    "json_result": [same as result]
}
```

### **5. Result Formatting (Enhanced Feature)**

#### **5.1 Format Processing:**
```python
formatted_result = format_result_as_table(result)
```

#### **5.2 Data Type Handling:**
- **Error Messages**: Display directly as text
- **List of Dictionaries**: Convert to formatted DataFrame
- **Empty Results**: Show "No results found"
- **Other Types**: Convert to string

#### **5.3 DataFrame Enhancement:**
```python
df = pd.DataFrame(result)
# Clean column names: "first_name" → "First Name"
df.columns = [col.replace('_', ' ').title() for col in df.columns]
# Set 1-based indexing: [1, 2, 3, 4, 5] instead of [0, 1, 2, 3, 4]
df.index = range(1, len(df) + 1)
```

#### **5.4 Fallback Formatting:**
If DataFrame fails, manual table creation with:
- Left-aligned columns
- Row numbers (#)
- Clean headers
- Proper spacing

### **6. Multi-Tab Display**

#### **Tab 0 - Result:**
```python
if isinstance(formatted_result, pd.DataFrame):
    st.dataframe(formatted_result, use_container_width=True)
else:
    st.text(formatted_result)
```
**Shows**: Clean, 1-based indexed table with formatted columns

#### **Tab 1 - JSON:**
```python
if json_result is not None:
    st.json(json_result)
else:
    st.write("No JSON result available")
```
**Shows**: Raw structured data for debugging/development

#### **Tab 2 - SQL Statement:**
```python
st.code(sql_statement, language='sql')
```
**Shows**: Generated SQL with syntax highlighting

#### **Tab 3 - ERD Diagram:**
```python
st.image(erd_diagram, caption='ERD Diagram', use_container_width=True)
```
**Shows**: Database schema for reference

## 🔄 **Complete User Journey**

### **Example: "How many actors are in the database?"**

1. **User Input**: Types query in text field
2. **AI Processing**: 
   - DDL context added
   - Gemini generates: `SELECT COUNT(*) FROM actor;`
3. **SQL Execution**: 
   - API executes query
   - Returns: `[{"count": 200}]`
4. **Response Formatting**:
   - Creates DataFrame with "Count" column
   - Sets 1-based index
   - Result: Clean table showing "1 | 200"
5. **Display**: 
   - **Result tab**: Formatted table
   - **JSON tab**: `[{"count": 200}]`
   - **SQL tab**: `SELECT COUNT(*) FROM actor;`
   - **ERD tab**: Database diagram

## ⚡ **Key Enhancements Over Original**

| Feature | Original demo.py | Enhanced demo_v2.py |
|---------|------------------|---------------------|
| **Indexing** | 0-based (0,1,2...) | 1-based (1,2,3...) |
| **Columns** | Raw names | Cleaned & Titled |
| **Display** | Basic st.write() | Formatted DataFrames |
| **Alignment** | Default | Left-aligned |
| **Error Handling** | Basic | Robust with fallbacks |
| **JSON Handling** | Direct display | Null-safe processing |

## 🛠️ **Prerequisites for Running**

### **1. Start SQL Execution API**
```bash
python sql_execution_api.py
```
- Runs on port 8001
- Handles all database operations
- Must be running before starting Streamlit

### **2. Environment Variables**
- `GOOGLE_API_KEY`: Required for Gemini AI integration
- Database connection variables handled by sql_execution_api.py

### **3. Start Streamlit Application**
```bash
streamlit run demo_v2.py --server.port 8502
```

## 📁 **File Dependencies**

```
demo_v2.py                 # Main Streamlit application
├── ai_sql_agent_v2.py     # SQL generation service
├── sql_execution_api.py   # SQL execution service
├── extract_ddl.py         # DDL extraction utility
├── dvd_rental_ddl.sql     # Database schema
└── images/
    └── ERD_DVD_RENTAL.png # Database diagram
```

## 🧪 **Testing the Workflow**

### **Sample Queries to Test**
```
"How many actors are in the database?"
"Show me the first 5 actors"
"What are the top 5 most rented movies?"
"Which customers have rented the most movies?"
"Show me all film categories"
"What is the average rental duration by category?"
```

### **Expected Workflow Verification**
1. **Input**: Natural language query
2. **Processing**: Watch for AI agent activity
3. **SQL Generation**: Check SQL Statement tab
4. **Execution**: Results appear in Result tab
5. **Formatting**: Tables show 1-based indexing with clean columns

## 🔧 **Troubleshooting**

### **Common Issues**

| Issue | Cause | Solution |
|-------|-------|----------|
| "SQL execution API is not available" | sql_execution_api.py not running | Start with `python sql_execution_api.py` |
| Import errors | Missing dependencies | Install requirements: `pip install -r requirements.txt` |
| ERD image not found | Missing image file | Verify `images/ERD_DVD_RENTAL.png` exists |
| Port conflicts | Port 8502 in use | Use different port: `--server.port 8503` |
| No results displayed | Database connection issue | Check PostgreSQL and API logs |

### **Debug Mode**
Add debug information to track the workflow:
```python
# Add after process_query() call
st.write("Debug - Response:", response)
st.write("Debug - Result Type:", type(response['result']))
```

## 🏆 **Key Features**

### **User Experience**
- **Simple Interface**: Same familiar layout as original demo.py
- **Professional Tables**: Clean, left-aligned, 1-based indexed results
- **Multi-Format View**: Result, JSON, SQL, and ERD tabs
- **Error Handling**: Clear error messages and graceful degradation

### **Technical Features**
- **Modular Architecture**: Separated SQL generation and execution
- **Robust Formatting**: Handles various data types and edge cases
- **Fallback Systems**: Manual formatting when DataFrame conversion fails
- **Performance**: Efficient pandas operations for table display

### **Data Processing**
- **Smart Column Names**: Automatic cleanup and formatting
- **1-Based Indexing**: User-friendly row numbering
- **Left Alignment**: Professional table appearance
- **Type Safety**: Handles null values and missing data

This workflow provides a seamless, professional experience for querying the DVD Rental database using natural language, while maintaining clean, maintainable code architecture.

## 🚀 **Getting Started**

1. **Clone/Navigate** to the ai-workspace directory
2. **Start the SQL API**: `python sql_execution_api.py`
3. **Launch the UI**: `streamlit run demo_v2.py --server.port 8502`
4. **Open browser** to `http://localhost:8502`
5. **Try a query**: "Show me the first 5 actors"
6. **Explore tabs**: Check Result, JSON, SQL Statement, and ERD views

The enhanced demo_v2.py provides the same simple interface you're familiar with, but with professional table formatting and robust error handling under the hood!
