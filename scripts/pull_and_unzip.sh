folder_path="./data/raw"
file_path="$folder_path/olist_data.zip"

mkdir -p "$folder_path"

# Check if folder exists
if [ ! -d "$folder_path" ]; then
  echo "Error: Folder does not exist"
  exit 1
fi

# Check if there are CSV files in the folder
if compgen -G "$folder_path/*.csv" >/dev/null; then
  echo "CSV files found in the folder: Skipping the download"
else
  # Download the file using wget
  wget_output=$(wget 'https://www.dropbox.com/sh/c857ajr68nbwkvt/AABkXVrKB2yDF9GzhKcihpVHa?dl=1' -q --show-progress -O "$file_path")

  # Check if the download was successful
  if [ $? -ne 0 ]; then
    echo "Error: Failed to download the file"
    exit 1
  else  
    echo "Olist data is in the folder"
  fi
fi

# Check if there are CSV files in the folder (again)
if compgen -G "$folder_path/*.csv" >/dev/null; then
  echo "CSV files found in the folder: Skipping unzip"
else
  echo "No CSV files found in the folder, unzipping"
  unzip -q "$file_path" -d "$folder_path"

  # Check if the unzip was successful
  if compgen -G "$folder_path/*.csv" >/dev/null; then
    echo "CSV files are ready. Removing the .zip file..."
    rm "$file_path"
    echo "Zip file removed: $file_path"
  else
    echo "Error: Failed to unzip the file or no CSV files found"
  fi
fi
