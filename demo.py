import streamlit as st
import sys
import os
from PIL import Image
from pathlib import Path

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the process_query function from ai_sql_agent
#from ai_sql_agent import process_query
from ai_sql_agent_v2 import process_query

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
        st.write(result)
    with tabs[1]:
        st.write(json_result)
    with tabs[2]:
        st.write(sql_statement)
