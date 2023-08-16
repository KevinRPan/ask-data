import streamlit as st
from functions.utils import *
import openai 
from datetime import datetime
import re 


st.markdown("# Explore")
st.sidebar.markdown("# Explore")

verbose = True

with st.sidebar:
    query_type = st.radio(
        'Select an output preference',
        options=['Explore','SQL', 'Python', 'Brainstorm'])


uploaded_file = st.file_uploader("Choose your own CSV file")

# if st.session_state.get("input_text_table") not in [None,""]:
#     st.warning("To use your own data, clear the table structure in the Table Structure tab.")

if uploaded_file is not None:   

    upload_df = find_file_type_import(uploaded_file)

    st.write(upload_df)
    table_structure = create_table_names_from_df(upload_df)
    prompt_prefix = f'Using a table named {uploaded_file.name}, with columns: '


input_text_question = st.text_input("What would you like to ask your data?", disabled=False, \
    placeholder="Example: What is the weekly average val of feature?")


input_text_table, input_text_question, input_df_table = None, None, None

table_structure = ''

data_viz_prefix = '''
I want you to act as a scientific data visualizer. You will apply your knowledge of data science principles and visualization techniques to create compelling visuals that help convey complex information, develop effective graphs and maps for conveying trends over time or across geographies, utilize tools such as seaborn and matplotlib to design meaningful interactive dashboards, collaborate with subject matter experts in order to understand key needs and deliver on their requirements. We have a dataset df with columns : '''


if (len(table_structure) > 5) and (len(input_text_question) > 5):

    st.session_state['output'] = st.session_state['output'] + 1

    prompt, output_type, output_file_ext = create_prompt(query_type = 'Explore', table_structure=table_structure)

    if verbose:
        st.write(prompt)

    if prompt:

        openai.api_key = st.secrets["openaiKey"]
        with st.spinner('Thinking...'):
            try:
                response = openai.Completion.create(engine="text-davinci-002", prompt=prompt, max_tokens=1000, temperature=0.3, top_p=1, frequency_penalty=0.0, presence_penalty=0.0)


                question_output = response['choices'][0]['text']
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
                df = upload_df if uploaded_file is not None else st.session_state['upload_df']

                explainer_prompt_prefix = "Please explain what the following code does: \n"
                explainer_prompt = explainer_prompt_prefix + question_output + "\n"


                if query_type == 'Python' or query_type == 'Explore':
                    try:
                        
                        lines = question_output.splitlines()
                        eval_list = []
                        for line in lines:
                        # question_output.replace('\n','\n\n')
                            eval_check = eval(line)
                            eval_list.append(eval_check)
                            st.write(eval_check)
                        [st.pyplot(plot) for plot in eval_list if isinstance(plot, plt.axes._subplots.AxesSubplot)]
                        explanation_response = openai.Completion.create(engine="text-davinci-002", prompt=explainer_prompt, max_tokens=1000, temperature=0.3, top_p=1, frequency_penalty=0.0, presence_penalty=0.0)
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