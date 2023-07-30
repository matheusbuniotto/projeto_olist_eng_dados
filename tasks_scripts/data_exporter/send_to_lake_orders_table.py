from mage_ai.settings.repo import get_repo_path
from mage_ai.io.config import ConfigFileLoader
from mage_ai.io.mysql import MySQL
import numpy as np
import pandas as pd
from os import path
import os

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter




@data_exporter
def export_data_to_mysql(df: pd.DataFrame, **kwargs) -> None:
    """
    Template for exporting data to a MySQL database.
    Specify your configuration settings in 'io_config.yaml'.

    Docs: https://docs.mage.ai/design/data-loading#mysql
    """
    config_path = path.join(get_repo_path(), 'io_config.yaml')
    config_profile = 'default'

    folder_path = '/home/src/data/'
    #Coleta a lista de csvs contendo order
    csv_files = [file for file in os.listdir(folder_path) if file.endswith('.csv') \
                and 'order' in file.lower()\
                and 'orders' not in file.lower()]

    for csv_file in csv_files:
    # Coleta o nome do arquivo
        table_name = os.path.splitext(csv_file)[0]
        table_name = table_name.replace('olist_', '')
        table_name = table_name.replace('_dataset', '')

        # Leitura do csv
        file_path = os.path.join(folder_path, csv_file)
        data = pd.read_csv(file_path, low_memory=False, keep_default_na=False)

       
        # Envio para o MYSQl
        with MySQL.with_config(ConfigFileLoader(config_path, config_profile)) as loader:
                loader.export(
                    data,
                    None,
                    table_name,
                    index=False,
                    if_exists='replace',  
            )
