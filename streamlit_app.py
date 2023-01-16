import streamlit as st
import openai
from datetime import datetime
from streamlit.components.v1 import html
import pandas as pd
from pandasql import sqldf 

st.set_page_config(page_title="Query Engine")

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

input_text_table, input_text_question, input_df_table = None, None, ''

upload_tab, schema_tab, demo_tab = st.tabs(['Table Structure', 'Upload', 'Demo'])

with upload_tab:
    uploaded_file = st.file_uploader("Or choose a file")

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write(df)
        input_df_table = ', '.join([str(col) for col in df.columns])

with schema_tab: 
    input_text_table = st.text_input("Enter your Table Structure", disabled=False, placeholder="Example format: fact_table: (date, id, val), dim_table: (id, feat, qual)")

with demo_tab:
    demo_df = pd.read_csv('data/Forbes2k.csv')
    st.write(demo_df)
    demo_df_table = ', '.join([str(col) for col in demo_df.columns])


if 'output' not in st.session_state:
    st.session_state['output'] = 0
  

input_text_question = st.text_input("Your question", disabled=False, placeholder="Example: What is the weekly average val of feature?")

st.session_state['output'] = st.session_state['output'] + 1

# st.write(st.session_state['output'])

table_structure = input_text_table + '\n' + input_df_table

if (len(table_structure) > 5) and (len(input_text_question) > 5):

    prompt_prefix = "Using the table structure: "

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
        prompt_query = "Brainstorm a solution to find: "
        prompt_suffix = ''
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

        st.info(question_output)

        filename = "query_"+str(st.session_state['output'])+"_"+str(today)+ output_file_ext
        btn = st.download_button(
            label="Download " + output_type,
            data=topic,
            file_name=filename
        )
    
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
                sql_string = question_output.replace('table','df')
                st.write(pysqldf(sql_string))
            except Exception as e:
                pass
                # st.write(e)
