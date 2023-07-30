from mage_ai.orchestration.run_status_checker import check_status
import os

if 'sensor' not in globals():
    from mage_ai.data_preparation.decorators import sensor


@sensor
def check_condition(*args, **kwargs) -> bool:
    """
    Template code for checking if block or pipeline run completed.
    """
    folder_path = '/home/src/data/'
    csv_file = 'olist_order_items_dataset.csv'   
    for file in os.listdir(folder_path): # Faz um check se existe um dos arquivos csv na pasta
        if file.lower().endswith('.csv'):
            return True
        return False        