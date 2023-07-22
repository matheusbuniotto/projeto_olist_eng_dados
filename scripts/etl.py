

import os
import pandas as pd
from sqlalchemy import create_engine, text, inspect

# Configure MySQL connection
mysql_username = 'root'
mysql_password = 'root'
mysql_host = 'mysql'
mysql_port = 3306
mysql_database = 'lake'
mysql_database_2 = 'warehouse'



def lake_to_warehouse():
    engine_lake = create_engine(f"mysql+mysqlconnector://{mysql_username}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}")
    engine_wh = create_engine(f"mysql+mysqlconnector://{mysql_username}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database_2}")


    insp = inspect(engine_lake)
    table_to_warehouse = insp.get_table_names()
    for i in ['product_category_name_translation', 'geolocation', 'order_payments']:
        table_to_warehouse.remove(i)

    
    

    with engine_lake.connect() as conn, engine_wh.connect() as conn_wh:
        for table in table_to_warehouse:
            query = f"SELECT * FROM {table}"

            try:
                pd.DataFrame(conn.execute(text(query)).fetchall()).to_sql(table, con=engine_wh, if_exists='fail')
                print(f'{table} is ready in the warehouse.')
            except: 
                print(f'{table} failed')