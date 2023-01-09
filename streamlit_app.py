import streamlit as st
import openai
from datetime import datetime
from streamlit.components.v1 import html

st.set_page_config(page_title="Query Engine")


html_temp = """
                <div style="background-color:{};padding:1px">
                
                </div>
                """


with st.sidebar:
    st.markdown("""
    # About 
    Query Engine is a helper tool built using generative AI to help you answer questions about your data. 
    """)
    st.markdown(html_temp.format("rgba(55, 53, 47, 0.16)"),unsafe_allow_html=True)
    st.markdown("""
    # How does it work
    Enter your table structure (table names, column names) and any questions you have about it.  
    """)
    st.markdown(html_temp.format("rgba(55, 53, 47, 0.16)"),unsafe_allow_html=True)
    st.markdown("""
    """,
    unsafe_allow_html=True,
    )


input_text_table, input_text_question = None, None
if 'output' not in st.session_state:
    st.session_state['output'] = 0

# if st.session_state['output'] <=2:
st.markdown("""
# Query Engine
""")
input_text_table = st.text_input("Table Structure", disabled=False)

input_text_question = st.text_input("Your question", disabled=False)
st.session_state['output'] = st.session_state['output'] + 1
# else:
#     st.info("Try out your query!")
#     st.markdown('''
#     <style>
#     .btn{
#         display: inline-flex;
#         -moz-box-align: center;
#         align-items: center;
#         -moz-box-pack: center;
#         justify-content: center;
#         font-weight: 400;
#         padding: 0.25rem 0.75rem;
#         border-radius: 0.25rem;
#         margin: 0px;
#         line-height: 1.6;
#         color: #fff;
#         background-color: #00acee;
#         width: auto;
#         user-select: none;
#         border: 1px solid #00acee;
#         }
#     .btn:hover{
#         color: #00acee;
#         background-color: #fff;
#     }
#     </style>
#     ''',
#     unsafe_allow_html=True
#     )

# hide="""
# <style>
# footer{
# 	visibility: hidden;
#     position: relative;
# }
# .viewerBadge_container__1QSob{
#     visibility: hidden;
# }
# <style>
# """
# st.markdown(hide, unsafe_allow_html=True)

st.markdown(
    """
    <style>
        iframe[width="220"] {
            position: fixed;
            bottom: 60px;
            right: 40px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)
if input_text_table and input_text_question:
    prompt_prefix = "Using the table structure: "
    prompt_suffix = "Write me a SQL query to to find: "
    prompt = prompt_prefix + str(input_text_table) + prompt_suffix + str(input_text_question)
    if prompt:
        openai.api_key = st.secrets["openaiKey"]
        response = openai.Completion.create(engine="text-davinci-002", prompt=prompt, max_tokens=1000)
        question_output = response['choices'][0]['text']
        today = datetime.today().strftime('%Y-%m-%d')
        topic = "Query help for: "+input_text+"\n@Date: "+str(today)+"\n"+question_output
        
        st.info(question_output)
        filename = "query_"+ str(input_text_question)+"_"+str(today)+".sql"
        btn = st.download_button(
            label="Download SQL",
            data=topic,
            file_name=filename
        )
