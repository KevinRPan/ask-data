import streamlit as st
# import streamlit_authenticator as stauth
import openai
from streamlit.components.v1 import html
import pandas as pd
from pandasql import sqldf 
import re
import matplotlib.pyplot as plt
import seaborn as sns

from functions.utils import *

inject_ga()

st.set_page_config(page_title="Query Engine")


verbose = True 

html_temp = """
                <div style="background-color:{};padding:1px">
                
                </div>
                """

with st.sidebar:

    st.markdown("""
    # About 
    A Query Engine is a tool to help you answer questions about your data. 

    Ask Data aims to empower everyone to understand their data. 
    """)
    st.markdown(html_temp.format("rgba(55, 53, 47, 0.16)"),unsafe_allow_html=True)
    st.markdown("""
    # Tips:
    Enter your table structure, upload a file, or try the demo dataset. 

    Then ask any questions you have about it, like you'd ask a team member. 
    """)
    st.markdown(html_temp.format("rgba(55, 53, 47, 0.16)"),unsafe_allow_html=True)
    st.markdown("""
    """,
    unsafe_allow_html=True,
    )

    st.markdown("""
    For any questions, feedback, or inquiries, please reach out to [build@askdata.app](mailto:build@askdata.app)!""")


st.markdown("""
# Query Engine
""")

st.markdown("""
Try out the demo dataset, or upload your own CSV file by exploring the sidebar.
""")

if 'upload_df' not in st.session_state:
    st.session_state['upload_df'] = pd.DataFrame()


## Prompter 
