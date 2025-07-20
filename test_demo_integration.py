#!/usr/bin/env python3
"""
Test script to verify demo_v2.py integration with ai_sql_agent_v2.py
"""

import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_sql_agent_v2 import process_query

def test_query_processing():
    """Test the query processing pipeline"""
    print("Testing demo_v2.py integration with ai_sql_agent_v2.py")
    print("=" * 60)
    
    test_queries = [
        "How many actors are in the database?",
        "What are the top 5 most rented movies?",
        "Show me all categories"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\nTest {i}: {query}")
        print("-" * 40)
        
        try:
            response = process_query(query)
            
            print(f"SQL Query: {response['sql_query']}")
            print(f"Result Type: {type(response['result'])}")
            print(f"Result: {response['result']}")
            print(f"JSON Result Available: {response['json_result'] is not None}")
            
            if isinstance(response['result'], list) and len(response['result']) > 0:
                print(f"First row keys: {list(response['result'][0].keys())}")
                
        except Exception as e:
            print(f"Error: {e}")
        
        print()

if __name__ == "__main__":
    test_query_processing()
