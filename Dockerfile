FROM mysql:8.0.33-debian as db

# Install dependencies
# Set the MySQL root password
ENV MYSQL_ROOT_PASSWORD=root

# Copy the SQL initialization script
COPY init2.sql /docker-entrypoint-initdb.d/

#CMD ["python3", "/opt/src/scripts/csv_to_sql.py"]

# Expose the MySQL port
EXPOSE 3306

# Define the volume mount
VOLUME ["/var/lib/mysql" ]


FROM python:3.11-slim-bullseye as etl

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y wget unzip python3-pip

# Copy the Bash script and Python script

COPY scripts/pull_and_unzip.sh /opt/src/scripts/pull_and_unzip.sh
COPY scripts/csv_to_sql.py /opt/src/scripts/csv_to_sql.py
COPY scripts/etl.py /opt/src/scripts/etl_functions.py

COPY scripts/queries/create_tables.sql /opt/src/scripts/create_tables.sql

# Install Python dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Make the Bash script executable
RUN chmod +x /opt/src/scripts/pull_and_unzip.sh

# Run the Bash script
RUN /opt/src/scripts/pull_and_unzip.sh

ENTRYPOINT [ "python", "/opt/src/scripts/csv_to_sql.py"]


FROM apache/superset as superset
# Switching to root to install the required packages
USER root
# Example: installing the MySQL driver to connect to the metadata database
# if you prefer Postgres, you may want to use `psycopg2-binary` instead
RUN pip install mysqlclient
# Example: installing a driver to connect to Redshift
# Find which driver you need based on the analytics database
# you want to connect to here:
# https://superset.apache.org/installation.html#database-dependencies
RUN pip install sqlalchemy-redshift
# Switching back to using the `superset` user
USER superset