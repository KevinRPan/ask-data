import pandas as pd
import streamlit as st
import pathlib
from bs4 import BeautifulSoup
import logging
import shutil
import openai 



# Functions
def create_table_names_from_df(df):
    return('"' + '", "'.join([str(col) for col in df.columns])+'"')

@st.cache(suppress_st_warning=True)
def find_file_type_import(file=None):
    """
    Find file type and import data
    """

    if file is None:
        return 

    def read_excel_header(file_name):
        return pd.read_excel(file_name, header=0)

    # All file extensions possible for importing data
    read_functions = {'csv': pd.read_csv,
                        'xlsx': read_excel_header,
                        'txt': pd.read_csv,
                        'parquet': pd.read_parquet,
                        'json': pd.read_json}

    try:
        for file_ext, read in read_functions.items():

            # st.write('Checking: ', file_ext)
            if file.name.endswith(file_ext):
                df = read(file)
                st.write('Imported file type: ', file_ext)
                return df
    except:
        st.warning('Perhaps try a different file type?')
    finally:
        print('File attempt finish')

@st.experimental_memo
def load_df():
    return find_file_type_import()


def identify_structure_prompt(table_structure):
    prompt_prefix = 'Act as a data analyst. Please identify what type of graph you would use to visualize the table with columns:'

    prompt = prompt_prefix \
            + str(table_structure) \
            + 'Only say the graph type.'
    
    return prompt

def run_prompt(prompt):
    response = openai.Completion.create(engine="text-davinci-002", prompt=prompt, max_tokens=1000, temperature=0.3, top_p=1, frequency_penalty=0.0, presence_penalty=0.0)

    question_output = response['choices'][0]['text']
    return question_output

def identify_x_axis(table_structure):
    prompt_prefix = 'Act as a data analyst. Please identify what column you would use as the x-axis when graphing the table with columns:'

    prompt = prompt_prefix \
            + str(table_structure) \
            + 'Only say the column name.'
    
    return prompt

def identify_y_axis(table_structure):
    prompt_prefix = 'Act as a data analyst. Please identify what column you would use as the y-axis when graphing the table with columns:'

    prompt = prompt_prefix \
            + str(table_structure) \
            + 'Only say the column name.'
    
    return prompt

def create_prompt(prompt_query='',
                  query_type='', 
                  data_viz_prefix='', 
                  prompt_prefix='', 
                  table_structure='', 
                  input_text_question=''):

    ## guess the category of data
    ## Guess how to handle it 
    ## try handling it 


    data_viz_prefix = '''
    I want you to act as a scientific data visualizer. 
    You will apply your knowledge of data science principles and visualization techniques to create compelling visuals that help convey complex information, develop effective graphs and maps for conveying trends over time or across geographies, utilize tools such as seaborn and matplotlib to design meaningful interactive dashboards, collaborate with subject matter experts in order to understand key needs and deliver on their requirements. We have a dataset df with columns : '''



    if query_type == 'Explore':
        prompt_prefix = data_viz_prefix
        prompt_query = "Please create a visualization to find trends in this data using python plotly code."
        prompt_suffix = '''
                        import pandas as pd
                        import plotly.express as px
                        import plotly.graph_objects as go
                        df = pd.read_csv("data.csv")
                        ''' 
        output_type = 'Explore'
        output_file_ext = '.md'

    elif query_type == 'SQL':
        prompt_query = "\n Write me a SQL query to to find: "
        prompt_suffix = '' 
        output_type = 'SQL'
        output_file_ext = '.sql'

    elif query_type == 'Python': 
        prompt_query = "\n You have a dataframe named df. Do not write an import or read file. Write me python code on the dataframe df using the pandas library to find: "
        prompt_suffix = 'import pandas as pd \n'
        output_type = 'Python'
        output_file_ext = '.py'

    elif query_type == 'Brainstorm':
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

    return prompt, output_type, output_file_ext


def inject_ga():
    GA_ID = "google_analytics"


    GA_JS = """
    <!-- Global site tag (gtag.js) - Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-01RV4J89GV"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());

        gtag('config', 'G-01RV4J89GV');
    </script>
    """

    # Insert the script in the head tag of the static template inside your virtual
    index_path = pathlib.Path(st.__file__).parent / "static" / "index.html"
    logging.info(f'editing {index_path}')
    soup = BeautifulSoup(index_path.read_text(), features="html.parser")
    if not soup.find(id=GA_ID): 
        bck_index = index_path.with_suffix('.bck')
        if bck_index.exists():
            shutil.copy(bck_index, index_path)  
        else:
            shutil.copy(index_path, bck_index)  
        html = str(soup)
        new_html = html.replace('<head>', '<head>\n' + GA_JS)
        index_path.write_text(new_html)

