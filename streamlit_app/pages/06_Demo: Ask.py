import streamlit as st
from functions.utils import *

st.markdown("# Demo")
st.sidebar.markdown("# Demo")


st.markdown("""
### Example dataset: S&P 500 stock prices
""")
demofile_name = 'all_stocks_5yr'
demofile_ext = '.csv'
demo_df = find_file_type_import('data/'+demofile_name+demofile_ext)
st.write(demo_df.head(100))

if st.session_state.get("input_text_table") not in [None,""]:
    st.warning("To use the demo, clear the table structure in the Table Structure tab.")
table_structure = create_table_names_from_df(demo_df)
prompt_prefix = 'Using a table named "table", with columns: '

