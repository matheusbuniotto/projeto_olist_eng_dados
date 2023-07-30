import os
import pandas as pd
from sqlalchemy import create_engine, text, inspect
from etl_functions import lake_to_warehouse 


# Configs do mysql
mysql_username = 'root'
mysql_password = 'root'
mysql_host = 'mysql'
mysql_port = 3306
mysql_database = 'lake'
mysql_database_2 = 'warehouse'

# Pasta com csvs
folder_path = '/opt/src/data/'

# Coleta a lista de arquivos csv na pasts
csv_files = [file for file in os.listdir(folder_path) if file.endswith('.csv')]

# Conexão com mysql
mysql_url = f"mysql+mysqlconnector://{mysql_username}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}"
engine = create_engine(mysql_url)

# Itera a lista de arquivos csv e realiza as transformações
for csv_file in csv_files:
    # Coleta o nome do arquivo sem olist e dataset
    table_name = os.path.splitext(csv_file)[0]
    table_name = table_name.replace('olist_', '')
    table_name = table_name.replace('_dataset', '')

    # Le o csv
    file_path = os.path.join(folder_path, csv_file)
    data = pd.read_csv(file_path)

    # Carga no sql
    data.to_sql(name=table_name,
                con=engine,
                if_exists='replace',
                index=False,
                chunksize=10000)
    
    print(f"{table_name} criado em {mysql_database}")


#Le os comandos de criação das tabelas 
fd = open('/opt/src/scripts/create_tables.sql', 'r')
sqlFile = fd.read()
fd.close()

# le os comandos em SQL dividindo por ;
sqlCommands = sqlFile.split(';') 
sqlCommands

# Executa os comandos SQL
with engine.connect() as conn:
    for command in sqlCommands:
        conn.execute(text(command))
        
# Função que faz a carga das tabelas do lake para o warehouse 
lake_to_warehouse()

