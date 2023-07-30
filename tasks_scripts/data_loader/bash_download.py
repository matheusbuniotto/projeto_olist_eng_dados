
if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test
import os


bash_script = """
#!/bin/bash
folder_path="/home/src/data"
file_path="$folder_path/olist_data.zip"

mkdir -p "$folder_path"

# Confere se a pasta exite antes de criar
if [ ! -d "$folder_path" ]; then
  echo "Error: Folder does not exist"
  exit 1
fi

# Confere se existem os csvs na pasta 
csv_files=$(find "$folder_path" -name "*.csv" -print -quit)
if [ -n "$csv_files" ]; then
  echo "CSV files found in the folder: Skipping the download"
else
  # Faz o download dos arquivos
  wget_output=$(wget -nc -c -q 'https://www.dropbox.com/sh/c857ajr68nbwkvt/AABkXVrKB2yDF9GzhKcihpVHa?dl=1'  -q --show-progress -O "$file_path")

  # Valida o download
  if [ $? -ne 0 ]; then
    echo "Error: Failed to download the file"
    exit 1
  else
    echo "Olist data is in the folder"
  fi
fi

# Confere se existem csvs na pasta antes de fazer a extração
csv_files=$(find "$folder_path" -name "*.csv" -print -quit)
if [ -n "$csv_files" ]; then
  echo "CSV estão na pasta: pulando unzip"
else
  echo "Extraindo arquivos"
  unzip -q "$file_path" -d "$folder_path"

  # Confere se a extração foi realizada
  csv_files=$(find "$folder_path" -name "*.csv" -print -quit)
  if [ -n "$csv_files" ]; then
    echo "CSVs estão ok. Removendo o .zip..."
    rm "$file_path"
    echo "Zip file removed: $file_path"
  else
    echo "Error: falha na extração do arquivo"
  fi
fi
"""

@data_loader
def load_data(*args, **kwargs):
    bashCommand = bash_script
    os.system(bashCommand)