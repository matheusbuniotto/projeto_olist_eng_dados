FROM mysql:8.0.33-debian as db
# Seta a senha do mysql
ENV MYSQL_ROOT_PASSWORD=root

# Copia o script que cria o lake e o warehouse
COPY scripts/init.sql /docker-entrypoint-initdb.d/

# Expõe a porta 
EXPOSE 3306

# Define the volume mount
VOLUME ["/var/lib/mysql" ]


# Iagem python que realiza o ETL 
FROM python:3.11-slim-bullseye as etl
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y wget unzip python3-pip

# Copy the Bash script and Python script

COPY scripts/pull_and_unzip.sh /opt/src/scripts/pull_and_unzip.sh
COPY scripts/csv_to_sql.py /opt/src/scripts/csv_to_sql.py
COPY scripts/etl.py /opt/src/scripts/etl_functions.py

COPY scripts/queries/create_tables.sql /opt/src/scripts/create_tables.sql

# Instala os requirements
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Habilita a execução do script the download e extração
RUN chmod +x /opt/src/scripts/pull_and_unzip.sh

# Roda o script bash
RUN /opt/src/scripts/pull_and_unzip.sh

ENTRYPOINT [ "python", "/opt/src/scripts/csv_to_sql.py"]