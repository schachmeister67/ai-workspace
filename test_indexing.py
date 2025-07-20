#!/usr/bin/env python3
"""
Test script to verify 1-based indexing in demo_v2.py
"""

import sys
import os
import pandas as pd

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from demo_v2 import format_result_as_table
from ai_sql_agent_v2 import process_query

def test_indexing():
    """Test the 1-based indexing feature"""
    print("Testing 1-based indexing in demo_v2.py")
    print("=" * 50)
    
    # Test with actual query
    print("\n1. Testing with real query:")
    print("-" * 30)
    
    try:
        response = process_query("Show me the first 5 actors")
        result = response['result']
        
        formatted_result = format_result_as_table(result)
        
        if isinstance(formatted_result, pd.DataFrame):
            print("✅ DataFrame created successfully")
            print(f"DataFrame index: {list(formatted_result.index)}")
            print(f"Expected: [1, 2, 3, 4, 5]")
            print(f"Index is 1-based: {formatted_result.index[0] == 1}")
            print("\nDataFrame preview:")
            print(formatted_result.head())
        else:
            print("❌ DataFrame not created, got:", type(formatted_result))
            print("Formatted result:")
            print(formatted_result[:200] + "..." if len(str(formatted_result)) > 200 else formatted_result)
            
    except Exception as e:
        print(f"❌ Error with real query: {e}")
    
    # Test with mock data
    print("\n\n2. Testing with mock data:")
    print("-" * 30)
    
    mock_result = [
        {"id": 101, "name": "Alice", "score": 85},
        {"id": 102, "name": "Bob", "score": 92},
        {"id": 103, "name": "Charlie", "score": 78}
    ]
    
    formatted_mock = format_result_as_table(mock_result)
    
    if isinstance(formatted_mock, pd.DataFrame):
        print("✅ Mock DataFrame created successfully")
        print(f"DataFrame index: {list(formatted_mock.index)}")
        print(f"Expected: [1, 2, 3]")
        print(f"Index is 1-based: {formatted_mock.index[0] == 1}")
        print("\nMock DataFrame:")
        print(formatted_mock)
    else:
        print("❌ Mock DataFrame not created, got:", type(formatted_mock))
        print("Formatted result:")
        print(formatted_mock)

if __name__ == "__main__":
    test_indexing()
