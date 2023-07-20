docker run -it \
  -e POSTGRES_USER="root" \
  -e POSTGRES_PASSWORD="root" \
  -e POSTGRES_DB="olist" \
  -v e:/github/olist_dataset/olist_data:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:13


  conectando on pgcli
  pgcli -h localhost -p 5432 -u root -d olist


python -m  notebook --ip 0.0.0.0 --port 8888 --no-browser --allow-root --NotebookApp.token=''


## criar mage

docker run -it -p 6789:6789 -v ${PWD}:/home/src mageai/mageai /app/run_app.sh mage start olist
https://docs.mage.ai/getting-started/setup


docker run --network olist -it -p 6789:6789 -v .:/home/src \
   -e MAGE_DATABASE_CONNECTION_URL=postgresql+psycopg2://root:root@olist:5432/olist \
   mageai/mageai \
   /app/run_app.sh mage start olist


   docker run --network olist --network-alias olist \
   -it -p 5432:5432 -v pgdata:/var/lib/postgresql/data:rw \
   -e POSTGRES_USER=root -e POSTGRES_PASSWORD=root \
   -e POSTGRES_DB=olist -e PG_DATA=/var/lib/postgresql/data/pgdata \
   postgres:13-alpine3.17 postgres