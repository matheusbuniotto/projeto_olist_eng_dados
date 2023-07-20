import pandas as pd
from sqlalchemy import create_engine
import sqlalchemy


df = pd.read_csv('data/raw/olist_sellers_dataset.csv')

print(pd.io.sql.get_schema(df, 'sellers'))


engine = create_engine('postgresql://root:root@localhost:5432/olist', connect_args={'options': '-csearch_path={}'.format('datalake')})





df.to_sql(name='sellers_olist',
          con=engine,
          if_exists='append',
          index=False,
          chunksize=10000)