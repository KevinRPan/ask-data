import streamlit as st
import openai
from datetime import datetime
from functions.utils import *
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import re 
from pandasql import sqldf 

st.markdown("# Demo")
st.sidebar.markdown("# Demo")

openai.api_base = "https://oai.hconeai.com/v1"

verbose = True 


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

input_text_question = 'Find trends in the dataset using the columns available.'

data_viz_prefix = '''
I want you to act as a scientific data visualizer. You will apply your knowledge of data science principles and visualization techniques to create compelling visuals that help convey complex information, develop effective graphs and maps for conveying trends over time or across geographies, utilize tools such as plotly to design meaningful interactive dashboards, collaborate with subject matter experts in order to understand key needs and deliver on their requirements. We have a dataset df with columns : '''


if 'output' not in st.session_state:
    st.session_state['output'] = 0


st.session_state['output'] = st.session_state['output'] + 1

prompt, output_type, output_file_ext = create_prompt(query_type = 'Explore', table_structure=table_structure)

if verbose:
    st.write(prompt)

query_type = "Explore"

if prompt:

    openai.api_key = st.secrets["openaiKey"]
    with st.spinner('Thinking...'):
        try:
            question_output = run_prompt(prompt)
            chart_type = run_prompt(identify_structure_prompt(table_structure))
            x_axis = run_prompt(identify_x_axis(table_structure))
            y_axis = run_prompt(identify_y_axis(table_structure))
            st.write(chart_type)
            st.write(x_axis,y_axis)
            today = datetime.today().strftime('%Y-%m-%d')
            topic = "Query help for: "+input_text_question+"\n@Date: "+str(today)+"\n"+question_output

            if query_type == "Brainstorm":
                question_output.replace('-','\n-')
            st.info(question_output)

            filename = "query_"+str(st.session_state['output'])+"_"+str(today)+ output_file_ext

            btn = st.download_button(
                label="Download " + output_type,
                data=topic,
                file_name=filename
            )

            # Evaluate the output 
            df = demo_df

            explainer_prompt_prefix = "Please explain what the following code does: \n"
            explainer_prompt = explainer_prompt_prefix + question_output + "\n"
            # st.
            # if verbose:
            #     st.write(question_output)

            if query_type == 'Python' or query_type == 'Explore':
                try:
                    
                    lines = question_output.splitlines()
                    fig = go.Figure()
                    eval_list = []
                    for line in lines:
                    # question_output.replace('\n','\n\n')
                        st.write(line)
                        if line == '' or line[0] == '#':
                            st.info(line)
                            continue

                        if line == 'fig.show()':
                            # st.plotly_chart(fig)
                            continue

                        try:

                            eval_check = eval(line)
                            eval_list.append(eval_check)
                            st.write(eval_check)
                        except SyntaxError as e:
                            if verbose:
                                st.write(e)
                            pass
                        


                    # st.pyplot(sns.lineplot(x="date", y="close", hue="Name", data=df))
                    # [st.pyplot(plot) for plot in eval_list if isinstance(plot, matplotlib.axes.Axes)]


                    explanation_response = openai.Completion.create(engine="text-davinci-002", 
                                                                    prompt=explainer_prompt, 
                                                                    max_tokens=1000, 
                                                                    temperature=0.3,
                                                                    top_p=1, 
                                                                    frequency_penalty=0.0, 
                                                                    presence_penalty=0.0,
                                                                    headers={
        "Helicone-Auth": "Bearer sk-44vv5wq-3l2uw2q-qhpqy7i-ugvm3gq",
      })
                    explanation_output = explanation_response['choices'][0]['text']
                    st.markdown("### Explanation")
                    st.write(explanation_output)
                except Exception as e:
                    if verbose:
                        st.write(e)
                    pass 

            elif query_type == 'SQL':
                try:
                    pysqldf = lambda q: sqldf(q, globals())
                    re_table_name = re.compile('FROM (\w*)', re.IGNORECASE)

                    sql_string = re_table_name.sub('FROM df', question_output)

                    explanation_response = openai.Completion.create(engine="text-davinci-002", prompt=explainer_prompt, max_tokens=1000, temperature=0.3, top_p=1, frequency_penalty=0.0, presence_penalty=0.0)
                    explanation_output = explanation_response['choices'][0]['text']
                    
                    st.markdown("### Explanation")
                    st.write(explanation_output)

                    if verbose:
                        st.write(sql_string)
                    pass
                
                    st.write(pysqldf(sql_string))
                except Exception as e:
                    if verbose:
                        st.write(e)
                    pass

        except openai.error.RateLimitError:
            st.error("Sorry, there are many requests at the moment! Please try again in a few minutes.")
        finally:
            pass 
        ## with tokens to spare, could shorten input text 

elif query_type == 'Explore':

    prompt, output_type, output_file_ext = create_prompt(query_type ='Explore')

if verbose:
    st.write(prompt)
    
    
# with st.spinner('Thinking...'):
    # response = openai.Completion.create(engine="text-davinci-002", prompt=prompt, max_tokens=1000, temperature=0.3, top_p=1, frequency_penalty=0.0, presence_penalty=0.0)

    # question_output = response['choices'][0]['text']
    # today = datetime.today().strftime('%Y-%m-%d')
    # topic = "Query help for: "+input_text_question+"\n@Date: "+str(today)+"\n"+question_output

    # st.info(question_output)