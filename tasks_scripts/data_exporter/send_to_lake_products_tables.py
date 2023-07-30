from mage_ai.settings.repo import get_repo_path
from mage_ai.io.config import ConfigFileLoader
from mage_ai.io.mysql import MySQL
from pandas import DataFrame
from os import path
import os
import pandas as pd

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


@data_exporter
def export_data_to_mysql(df: DataFrame, **kwargs) -> None:
    """
    Template for exporting data to a MySQL database.
    Specify your configuration settings in 'io_config.yaml'.

    Docs: https://docs.mage.ai/design/data-loading#mysql
    """
    table_name = 'products'  
    config_path = path.join(get_repo_path(), 'io_config.yaml')
    config_profile = 'default'
    data = pd.read_csv("/home/src/data/olist_products_dataset.csv", keep_default_na=False) #leitura do csv de produto
    print(data.info())

    # Lista de colunas para conversão
    numeric_columns = [
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm"
    ]

    # Converte algumas colunas que estavam com erro
    data[numeric_columns] = data[numeric_columns].apply(pd.to_numeric, errors='coerce')
    data.fillna(0, inplace=True)
    
    # ENvia para o MySQL lake
    with MySQL.with_config(ConfigFileLoader(config_path, config_profile)) as loader:
        loader.export(
            data,
            None,
            table_name,
            index=False,  
            if_exists='replace',  
        )