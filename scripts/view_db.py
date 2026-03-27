import streamlit as st
import sqlite3
import pandas as pd
import os

st.set_page_config(layout="wide", page_title="Database Viewer")

st.title("📂 Database Inspector")

# Data directory
DATA_DIR = "data"

# List database files
db_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".db")]

if not db_files:
    st.error("No database files found in data directory.")
    st.stop()

selected_db = st.sidebar.selectbox("Select Database", db_files, index=db_files.index("woocommerce.db") if "woocommerce.db" in db_files else 0)

db_path = os.path.join(DATA_DIR, selected_db)

conn = sqlite3.connect(db_path)

# Get tables
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [r[0] for r in cursor.fetchall()]

if not tables:
    st.warning("No tables found in this database.")
else:
    selected_table = st.sidebar.radio("Select Table", tables)
    
    st.subheader(f"Table: `{selected_table}`")
    
    # Get total count
    count = pd.read_sql_query(f"SELECT COUNT(*) FROM '{selected_table}'", conn).iloc[0,0]
    st.info(f"Total Rows: {count}")
    
    # Filter/Limit
    limit = st.sidebar.slider("Rows to display", 50, 1000, 100)
    
    # Custom Query
    if st.sidebar.checkbox("Run Custom SQL"):
        custom_sql = st.text_area("SQL Query", f"SELECT * FROM '{selected_table}' LIMIT 10")
        if custom_sql:
            try:
                df = pd.read_sql_query(custom_sql, conn)
                st.dataframe(df)
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        # Show table data
        query = f"SELECT * FROM '{selected_table}' LIMIT {limit}"
        df = pd.read_sql_query(query, conn)
        st.dataframe(df, use_container_width=True)
        
        st.write("### Data Types")
        st.write(df.dtypes.astype(str))

conn.close()
