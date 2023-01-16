import streamlit as st
import openai
from datetime import datetime
from streamlit.components.v1 import html
import pandas as pd
from pandasql import sqldf 
import re

st.set_page_config(page_title="Query Engine")

# Functions
def create_table_names_from_df(df):
    return('"' + '", "'.join([str(col) for col in df.columns])+'"')

html_temp = """
                <div style="background-color:{};padding:1px">
                
                </div>
                """

with st.sidebar:
    st.markdown("""
    # About 
    Ask Data is a tool built using Large Language Models (LLMs) to help you answer questions about your data. 

    Query Engine will be a platform to enable everyone to unlock the powers of data science. 
    """)
    st.markdown(html_temp.format("rgba(55, 53, 47, 0.16)"),unsafe_allow_html=True)
    st.markdown("""
    # Tips:
    Enter your table structure, upload a file, or try the demo dataset. 

    Then ask any questions you have about it. 
    """)
    st.markdown(html_temp.format("rgba(55, 53, 47, 0.16)"),unsafe_allow_html=True)
    st.markdown("""
    """,
    unsafe_allow_html=True,
    )

    query_type = st.radio(
        'Select an output preference',
        options=['SQL', 'Python', 'Brainstorm!'])


st.markdown("""
# Query Engine
""")

input_text_table, input_text_question, input_df_table = None, None, None

table_structure = ''

upload_tab, schema_tab, demo_tab = st.tabs(['Upload','Table Structure', 'Demo'])

with upload_tab:
    uploaded_file = st.file_uploader("Choose your own CSV file")

    if st.session_state.get("input_text_table") not in [None,""]:
        st.warning("To use your own data, clear the table structure in the Table Structure tab.")

    if uploaded_file is not None:
        upload_df = pd.read_csv(uploaded_file)
        st.write(upload_df)
        table_structure = create_table_names_from_df(upload_df)
        prompt_prefix = f'Using a table named {uploaded_file.name}, with columns: '

with schema_tab: 

    if st.session_state.get("schema_tab") not in [None,""]:
        st.warning("To use your own data, clear the table structure in the Table Structure tab.")


    input_text_table = st.text_input("Enter your Table Structure", disabled=False, \
        placeholder="Example format: fact_table: (date, id, val), dim_table: (id, feat, qual)")
    
    if input_text_table:
        table_structure = input_text_table
        prompt_prefix = "Using a table structure: "

with demo_tab:
    st.markdown("""
    ### Example dataset: Forbes 2000
    """)
    demofile_name = 'Forbes2k'
    demofile_ext = '.csv'
    demo_df = pd.read_csv('data/'+demofile_name+demofile_ext)
    st.write(demo_df)
    if uploaded_file is None:
        if st.session_state.get("input_text_table") not in [None,""]:
            st.warning("To use the demo, clear the table structure in the Table Structure tab.")
        table_structure = create_table_names_from_df(demo_df)
        prompt_prefix = 'Using a table named "table", with columns: '


input_text_question = st.text_input("What would you like to ask your data?", disabled=False, \
    placeholder="Example: What is the weekly average val of feature?")

if 'output' not in st.session_state:
    st.session_state['output'] = 0
  
if (len(table_structure) > 5) and (len(input_text_question) > 5):

    st.session_state['output'] = st.session_state['output'] + 1

    if query_type == 'SQL':
        prompt_query = "Write me a SQL query to to find: "
        prompt_suffix = '' 
        output_type = 'SQL'
        output_file_ext = '.sql'

    elif query_type == 'Python': 
        prompt_query = "You have a dataframe named df. Do not write an import or read file. Write me python code on the dataframe df using the pandas library to find: "
        prompt_suffix = 'import pandas as pd \n'
        output_type = 'Python'
        output_file_ext = '.py'


    elif query_type == 'Brainstorm!':
        prompt_query = "What are some other things to explore in this data after finding "
        prompt_suffix = '\n Only return your top five ideas in a numbered list.'
        output_type = 'Text'
        output_file_ext = '.md'


    prompt = prompt_prefix \
             + str(table_structure) \
             + ' \n' \
             + prompt_query \
             + str(input_text_question) \
             + ' \n' \
             + prompt_suffix 

    # st.write(prompt)

    if prompt:
        openai.api_key = st.secrets["openaiKey"]
        response = openai.Completion.create(engine="text-davinci-002", prompt=prompt, max_tokens=1000, temperature=0.3, top_p=1, frequency_penalty=0.0, presence_penalty=0.0)

        ## with tokens to spare, could shorten input text 

        question_output = response['choices'][0]['text']
        today = datetime.today().strftime('%Y-%m-%d')
        topic = "Query help for: "+input_text_question+"\n@Date: "+str(today)+"\n"+question_output

        if query_type == "Brainstorm!":
            question_output.replace('-','\n-')
        st.info(question_output)

        filename = "query_"+str(st.session_state['output'])+"_"+str(today)+ output_file_ext
        btn = st.download_button(
            label="Download " + output_type,
            data=topic,
            file_name=filename
        )

        # Evaluate the output 
        df = upload_df if uploaded_file is not None else demo_df

        if query_type == 'Python':
            try:
                eval_check = eval(question_output)
                st.write(eval_check)
            except Exception as e:
                pass
                # st.write(e)

        elif query_type == 'SQL':
            try:
                pysqldf = lambda q: sqldf(q, globals())
                re_table_name = re.compile('FROM (\w*)', re.IGNORECASE)

                sql_string = re_table_name.sub('FROM df', question_output)
                # st.write(sql_string)
                st.write(pysqldf(sql_string))
            except Exception as e:
                pass
                # st.write(e)
