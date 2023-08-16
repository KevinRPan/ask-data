import streamlit as st
import pandas as pd
from functions.utils import * 

st.markdown("# Explore")
st.sidebar.markdown("# Explore")

uploaded_file = st.file_uploader("Choose your own CSV file")

# if st.session_state.get("input_text_table") not in [None,""]:
#     st.warning("To use your own data, clear the table structure in the Table Structure tab.")

if uploaded_file is not None:
    upload_df = find_file_type_import(uploaded_file)
    st.write(upload_df)
