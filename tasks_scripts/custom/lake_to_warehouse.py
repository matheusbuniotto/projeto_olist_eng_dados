if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


import os
import pandas as pd
from sqlalchemy import create_engine, text, inspect



# Configura as conexões do sql com diferentes databases
mysql_username = 'root'
mysql_password = 'root'
mysql_host = 'host.docker.internal'
mysql_port = 3306
mysql_database = 'lake'
mysql_database_2 = 'warehouse'

@custom
def lake_to_warehouse(*args, **kwargs):
    engine_lake = create_engine(f"mysql+mysqlconnector://{mysql_username}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}") #conexão lake
    engine_wh = create_engine(f"mysql+mysqlconnector://{mysql_username}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database_2}") #conexão warehouse

    # Escolhe algumas tabelas para envio
    insp = inspect(engine_lake) #insp para coletar os nomes da tabela no lake
    table_to_warehouse = ["order_items_detailed", "sellers_performance", "customers", "customer_experience",
                            "order_reviews"]

    
    

    with engine_lake.connect() as conn, engine_wh.connect() as conn_wh:
            for table in table_to_warehouse:
                query = f"SELECT * FROM {table}" #seleciona a tabela no lake
                # faz o envio para o warehouse
                try: 
                    pd.DataFrame(conn.execute(text(query)).fetchall()).to_sql(table, index=False, con=engine_wh, if_exists='replace')
                    print(f'{table} está pronta warehouse.')
                except: 
                    print(f'{table} falhou.')