from db.load_in_db import get_current_tables_data, insert_current_tables
from db.run_queries import run_queries
from app_files.streamlit_dashboard import streamlit_main
import os


INSERT = os.environ['INSERTION']

# change insert in .env if we need to add data. default is true
if INSERT:
    print("insertion happened")
    mappings = get_current_tables_data()
    insert_current_tables(mappings)
    results = run_queries()

# print(results.keys())
streamlit_main(results['query1'], results['query2'], results['query3'], results['query4'])