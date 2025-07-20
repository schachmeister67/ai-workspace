import streamlit as st
import sys
import os
from PIL import Image
from pathlib import Path
import pandas as pd

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the process_query function from ai_sql_agent
from ai_sql_agent_v2 import process_query

def format_result_as_table(result):
    """
    Format the result as a table with left-aligned values.
    
    Args:
        result: The raw result from ai_sql_agent_v2
        
    Returns:
        Formatted string or DataFrame for display
    """
    # Handle error messages
    if isinstance(result, str):
        if result.startswith("Error:"):
            return result
        return result
    
    # Handle list of dictionaries (query results)
    if isinstance(result, list) and len(result) > 0:
        # Convert to DataFrame for better table formatting
        try:
            df = pd.DataFrame(result)
            # Clean up column names (replace underscores with spaces, capitalize)
            df.columns = [col.replace('_', ' ').title() for col in df.columns]
            # Set 1-based index (1, 2, 3, 4, etc.)
            df.index = range(1, len(df) + 1)
            return df
        except Exception:
            # Fallback to manual formatting if DataFrame conversion fails
            headers = list(result[0].keys())
            
            # Calculate column widths for left alignment
            col_widths = {}
            for header in headers:
                col_widths[header] = max(len(str(header)), 
                                       max(len(str(row.get(header, ''))) for row in result))
            
            # Build formatted table
            lines = []
            
            # Header line with row number
            header_parts = ["#"]  # Add row number column
            for header in headers:
                clean_header = header.replace('_', ' ').title()
                header_parts.append(f"{clean_header:<{col_widths[header]}}")
            lines.append(" | ".join(header_parts))
            
            # Separator line
            separator_parts = ["-"]  # Add separator for row number column
            separator_parts.extend(["-" * col_widths[header] for header in headers])
            lines.append("-|-".join(separator_parts))
            
            # Data lines with 1-based row numbers
            for i, row in enumerate(result, 1):
                row_parts = [str(i)]  # Add 1-based row number
                for header in headers:
                    value = str(row.get(header, ''))
                    row_parts.append(f"{value:<{col_widths[header]}}")
                lines.append(" | ".join(row_parts))
            
            return "\n".join(lines)
    
    # Handle empty results
    elif isinstance(result, list) and len(result) == 0:
        return "No results found"
    
    # Handle other data types
    return str(result)

# Get the root path of the current directory
root_path = Path(__file__).parent

st.title("Search for Data AI Assistant")
user_input = st.text_input("Enter your search query:")
tab_titles = ["Result", "JSON", "SQL Statement", "ERD Diagram"]
tabs = st.tabs(tab_titles)
erd_diagram = Image.open(f'{root_path}/images/ERD_DVD_RENTAL.png')
with tabs[3]:
    st.image(erd_diagram, caption='ERD Diagram', use_container_width=True)

if user_input:
    response = process_query(user_input)
    sql_statement = response['sql_query']
    result = response['result']
    json_result = response['json_result']
    
    with tabs[0]:
        # Format and display result as a table
        formatted_result = format_result_as_table(result)
        if isinstance(formatted_result, pd.DataFrame):
            st.dataframe(formatted_result, use_container_width=True)
        else:
            st.text(formatted_result)
    
    with tabs[1]:
        if json_result is not None:
            st.json(json_result)
        else:
            st.write("No JSON result available")
    
    with tabs[2]:
        st.code(sql_statement, language='sql')
