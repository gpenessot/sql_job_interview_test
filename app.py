import os
import pandas as pd
import gradio as gr
import configparser
from sqlalchemy import create_engine, text

os.chdir(os.path.dirname(os.path.abspath(__file__)))
config = configparser.ConfigParser()
config.read('./config.cfg')

HOST_EXT = config['POSTGRES']['host_name_ext']
DATABASE_NAME = config['POSTGRES']['database']
HOST_PORT = config['POSTGRES']['port']
USERNAME = config['POSTGRES']['username']
PASSWORD = config['POSTGRES']['password']

# Read the input dataframe with exercise statements and answers
df = pd.read_excel("input.xls")

# Connect to the PostgreSQL database
engine = create_engine(f"postgresql://{USERNAME}:{PASSWORD}@{HOST_EXT}/{DATABASE_NAME}")

def charger_enonce(row_idx):
    """
    This function takes a row index as input and returns the value of the 'Enoncé' column for that row.
    
    Parameters:
    row_idx (int): The index of the row to retrieve the value from.
    
    Returns:
    str: The value of the 'Enoncé' column for the specified row.
    """
    val = df.at[int(row_idx), 'Enoncé']
    return val

def clean_string(a_string):
    """
    Cleans a string by replacing special characters with spaces.

    Args:
        a_string (str): The input string to be cleaned.

    Returns:
        str: The cleaned string.
    """
    if a_string is None:
        return ''
    if not isinstance(a_string, str):
        raise TypeError("Input must be a string")
    clean_txt = a_string.replace('\r', ' ').replace('\t', ' ').replace('\n', ' ')
    return clean_txt

def execute_sql(row_idx, sql_code):
    """
    Executes the given SQL code and compares the result to the expected answer.

    Args:
        row_idx (int): The index of the row.
        sql_code (str): The SQL code to execute.

    Returns:
        tuple: A tuple containing the message indicating correctness and the result dataframe.
    """
    result = execute_query(sql_code)
    expected_answer = load_expected_answer(row_idx)
    message = compare_results(result, expected_answer)
    return message, result


def execute_query(sql_code):
    """
    Executes the given SQL code and returns the result dataframe.

    Args:
        sql_code (str): The SQL code to execute.

    Returns:
        pandas.DataFrame: The result dataframe.
    """
    with engine.connect() as conn:
        with conn.begin():
            result = pd.read_sql_query(text(clean_string(sql_code)), conn)
    return result


def load_expected_answer(row_idx):
    """
    Loads the expected answer dataframe for the given row index.

    Args:
        row_idx (int): The index of the row.

    Returns:
        pandas.DataFrame: The expected answer dataframe.
    """
    expected_answer = pd.read_pickle(f'./queries/resultat_{row_idx}.pkl')
    return expected_answer


def compare_results(result, expected_answer):
    """
    Compares the result dataframe to the expected answer dataframe and returns the message indicating correctness.

    Args:
        result (pandas.DataFrame): The result dataframe.
        expected_answer (pandas.DataFrame): The expected answer dataframe.

    Returns:
        str: The message indicating correctness.
    """
    if result.equals(expected_answer):
        message = "Correct!"
    else:
        message = "Incorrect. Try again!"
    return message


with gr.Blocks() as app:
    
    gr.Markdown("# SQL Questions for Job Interview")
    
    gr.Markdown("### Teste tes connaissances en SQL!")
    with gr.Row():
        idx = gr.components.Dropdown(
                                    label="Selectionne une question",
                                    choices=df.index.tolist()
                                    )
        txt = gr.Textbox(label="Enoncé", lines=3)
    btn = gr.Button(value="Charger l'énoncé")
    btn.click(charger_enonce, inputs=[idx], outputs=[txt]) # On charge la question 

    with gr.Row():
        requete = gr.Textbox(label='Entre ta requête SQL ici :')
        print(f"### REQUETE : {requete}")
        verdict = gr.Textbox(label='verdict')
    
    resultat = gr.Dataframe(label="Résultats de ta requête", type='pandas')
    
    btn2 = gr.Button(value="Vérifiez la requête")
    btn2.click(execute_sql, inputs=[idx, requete], outputs=[verdict, resultat]) # On charge la question     

    gr.HTML("""<img alt='ERD Schema' src='./dbschema.png'>""")
    
if __name__ == "__main__":
    app.launch()