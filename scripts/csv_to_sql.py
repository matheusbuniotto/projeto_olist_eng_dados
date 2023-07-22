import os
import pandas as pd
from sqlalchemy import create_engine, text, inspect
from etl_functions import lake_to_warehouse 


# Configure MySQL connection
mysql_username = 'root'
mysql_password = 'root'
mysql_host = 'mysql'
mysql_port = 3306
mysql_database = 'lake'
mysql_database_2 = 'warehouse'

# Folder path containing CSV files
folder_path = '/opt/src/data/'

# Get a list of all CSV files in the folder
csv_files = [file for file in os.listdir(folder_path) if file.endswith('.csv')]

# Create a MySQL connection
mysql_url = f"mysql+mysqlconnector://{mysql_username}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}"
engine = create_engine(mysql_url)

# Iterate over each CSV file and load it into MySQL
for csv_file in csv_files:
    # Remove the prefixes and suffixes from the file name
    table_name = os.path.splitext(csv_file)[0]
    table_name = table_name.replace('olist_', '')
    table_name = table_name.replace('_dataset', '')

    # Read the CSV file into a DataFrame
    file_path = os.path.join(folder_path, csv_file)
    data = pd.read_csv(file_path)

    # Load the DataFrame into MySQL
    data.to_sql(name=table_name,
                con=engine,
                if_exists='replace',
                index=False,
                chunksize=10000)
    
    print(f"{table_name} created in {mysql_database}")


fd = open('/opt/src/scripts/create_tables.sql', 'r')
sqlFile = fd.read()
fd.close()


sqlCommands = sqlFile.split(';') 
sqlCommands

with engine.connect() as conn:
    for command in sqlCommands:
        # This will skip and report errors
        # For example, if the tables do not yet exist, this will skip over
        # the DROP TABLE command
        conn.execute(text(command))



                
lake_to_warehouse()

