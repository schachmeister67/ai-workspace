#!/usr/bin/env python3
"""
Side-by-side comparison test of demo.py vs demo_v2.py functionality
"""

import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_sql_agent_v2 import process_query
import pandas as pd

def format_result_as_table_v2(result):
    """
    Enhanced formatting function from demo_v2.py
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
            
            # Header line
            header_parts = []
            for header in headers:
                clean_header = header.replace('_', ' ').title()
                header_parts.append(f"{clean_header:<{col_widths[header]}}")
            lines.append(" | ".join(header_parts))
            
            # Separator line
            lines.append("-|-".join(["-" * col_widths[header] for header in headers]))
            
            # Data lines
            for row in result:
                row_parts = []
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

def compare_formatting():
    """Compare formatting between original and enhanced versions"""
    print("Demo.py vs Demo_v2.py - Formatting Comparison")
    print("=" * 60)
    
    # Test query
    query = "Show me the first 5 actors"
    print(f"Test Query: {query}")
    print("-" * 60)
    
    try:
        response = process_query(query)
        result = response['result']
        
        print("\n1. ORIGINAL DEMO.PY FORMATTING:")
        print("   Using: st.write(result)")
        print("   Output:", result)
        
        print("\n2. ENHANCED DEMO_V2.PY FORMATTING:")
        print("   Using: format_result_as_table() + st.dataframe()")
        formatted = format_result_as_table_v2(result)
        if isinstance(formatted, pd.DataFrame):
            print("   DataFrame columns:", list(formatted.columns))
            print("   DataFrame shape:", formatted.shape)
            print("   Sample output:")
            print(formatted.head().to_string(index=False))
        else:
            print("   Formatted output:")
            print(formatted)
        
        print("\n3. RESPONSE STRUCTURE:")
        print(f"   SQL Query: {response['sql_query'][:50]}...")
        print(f"   Result Type: {type(response['result'])}")
        print(f"   JSON Result Available: {response['json_result'] is not None}")
        
        if isinstance(result, list) and len(result) > 0:
            print(f"   First row keys: {list(result[0].keys())}")
            print(f"   Total rows: {len(result)}")
            
    except Exception as e:
        print(f"Error: {e}")

def test_edge_cases():
    """Test edge cases for formatting"""
    print("\n" + "=" * 60)
    print("EDGE CASES TESTING")
    print("=" * 60)
    
    test_cases = [
        ("Empty result", []),
        ("Error message", "Error: Table not found"),
        ("Single value", [{"count": 42}]),
        ("Multiple columns", [
            {"actor_id": 1, "first_name": "John", "last_name": "Doe"},
            {"actor_id": 2, "first_name": "Jane", "last_name": "Smith"}
        ])
    ]
    
    for case_name, test_data in test_cases:
        print(f"\nTesting: {case_name}")
        print("-" * 30)
        formatted = format_result_as_table_v2(test_data)
        if isinstance(formatted, pd.DataFrame):
            print("DataFrame output:")
            print(formatted.to_string(index=False))
        else:
            print("String output:")
            print(formatted)

if __name__ == "__main__":
    compare_formatting()
    test_edge_cases()
