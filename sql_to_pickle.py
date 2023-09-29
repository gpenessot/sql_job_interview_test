import configparser
import psycopg2
import pandas as pd
import time

config = configparser.ConfigParser()
config.read('./config.cfg')

HOST_EXT = config['POSTGRES']['host_name_ext']
DATABASE_NAME = config['POSTGRES']['database']
HOST_PORT = config['POSTGRES']['port']
USERNAME = config['POSTGRES']['username']
PASSWORD = config['POSTGRES']['password']

conn = psycopg2.connect(f"postgres://{USERNAME}:{PASSWORD}@{HOST_EXT}/{DATABASE_NAME}")
df = pd.read_excel("input.xls")

for i, sql_code in enumerate(df['Réponse'].tolist()):
    print(f'Requête {i} :')
    result = pd.read_sql_query(sql_code, conn)
    result.to_pickle(f"./queries/resultat_{i}.pkl")
    time.sleep(2)  