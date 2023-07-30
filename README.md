# Projeto de Engenharia de dados com os dados do ecommerce Olist.
Esse projeto foi realizado por mim como forma de estudo de engenharia de dados, com foco nos processos de **ETL e orquestração utilizando Python, SQL, Docker, Bash e Mage**. A proposta do projeto é criar um pipeline que consome os dados, realiza a carga em um data lake, realiza as transformações e validações, e em sequência disponibiliza os dados em uma data warehouse para consumo analítico. Ele se baseia em um projeto anterior que realizei no meu TCC curso de Análise de dadosna PUC-MG, porém agora com mais experiência e conhecimento, acredito que consigo melhorar o que havia desenvolvido anteriormente.

Overview do projeto
![overview do projeto](presets/overview.png)

## Etapas do projeto
1 - Configuração da imagem e network docker\
2 - Orquestração utilizando mage\
    2.1 - Criação dos scripts de coleta, carga, extração e carga\
    2.1 - Criação das tasks no mage\
    2.2 - Criação das validações e sensores\
3 - Consumo dos dados, exemplo com jupyter e powerbi

## 1- Imagem com MySQL e script init com criação do lake e warehouse vazios.
Dockerfile contendo imagem MySQL (mysql:8.0.33-debian) e configurações, com script SQL para criação das bases na inizaliação do servidor. 

```
script/initdb.sql

CREATE DATABASE IF NOT EXISTS lake;
CREATE DATABASE IF NOT EXISTS warehouse;
USE lake;
```

#### Cria a network que será utilizada pelo Mage e pelo MySQL
`docker network create mage-app`

#### Build e execução da imagem do servidor MySQL
`docker build -t my_mysql_server .`
`docker run -d -p 3306:3306 --name my_mysql_container --network mage-app my_mysql_server`
Pronto, o servidor MySQL está rodando e exposto para conexão.

#### Inicializa o orquestrador Mage com conexão com MySQL
```
docker run --network mage-app -it -p 6789:6789 -v ${PWD}:/home/src `
   -e MAGE_DATABASE_CONNECTION_URL="mysql+mysqlconnector://root:root@host.docker.internal:3306/lake" `
   mageai/mageai `
   /app/run_app.sh mage start olist 
```
Pronto, agora temos nosso servidor em MySQL de pé e nosso orquestrador Mage funcionando em *http://localhost:6789/* 

## 2 - Regendo a orquestra
Na orquestração desse projeto utilizei o mage, um orquestrador open-source com proposta semelhante ao airflow, porém com algumas diferenças e uma maior facilidade para projetos pequenos, na minha opnião. O pipeline final do projeto ficou da seguinte forma (tree view).

![pipeline](presets/tree_view.png)


Nas etapas descritas abaixo irei ignorar os steps no mage que são sensores, ou seja, fazem uma validação se algo ocorreu antes da execução dos steps dependentes. No projeto incluí 2 sensores (em rosa na árvore de fluxo) e presentes em `tasks_scripts/sensors`, um deles valida se já existem os arquivos csv antes de fazer o download e o outro valida se a tabelas já existem no lake antes de realizar a carga.

### Etapa 1 - Extração - Task bashDownload @data_loader 
Uma task de extração é descrita como um @data_loader no mage. Um dataloader é descrito como:
*Code for fetching data from a remote source or loading it from disk.*

Nosso primeiro data loader irá acessar os dados que estão em um armazenamento na nuvem e realizar o download em formato zip, então extrairá os arquivos e irá fazer a remoção do .zip após a extração. Para isso configuramos BashCommand com script que realiza essas ações. O código da task e do script está disponível no arquivo olist/dataloaders/bashdownload.py

O task executa a função:
```
@data_loader
def load_data(*args, **kwargs):
    bashCommand = bash_script
    os.system(bashCommand)
```

### Etapa 2 - Carga - Tasks de @data_exporter
Uma task de carga é descrita como um @data_exporter no mage. Um data exporter é descrito como:
*... use these types of blocks to store that data or to train models and store those models elsewhere.*

Nesse projeto utilizei 3 tasks de carga separadamente para fazer o envio dos arquivos .csv para tabelas no data lake criado. Em um cenário ideal, cada arquivo csv passaria por um pipeline específico de carga, transformação e carga no warehouse, porém optei por unir em um pipeline único por motivos de simplicidade.

A `task send_to_lake_orders_table` utiliza operador Python que possuí um loop faz a leitura dos csvs que possuem relação com o fato de order, extraí o nome do arquivo que dará origem ao nome da tabela e realiza a carga em uma tabela no lake. Por exemplo:

O arquivo olist_order_payments_dataset.csv é lido e enviado para o lake como uma tabela chamada order_payments. 

** OBS!! Antes da execução das tasks, é executado um sensor que valida se os dados já não estão presentes no lake. (lakesensor, em rosa)**

Respectivamente, as task `send_to_lake_products` faz envio das tabelas de produto e a `send_to_lake_others` faz envio das tabelas restantes, com exceção do arquivo de geolocalização que não será carregado para utilização. 

Os scripts dos @data_exporter se encontram em tasks_scripts/data_exporter

```
@data_exporter
def export_data_to_mysql_others(df: pd.DataFrame, **kwargs) -> None:
    """
    Exporting data to a MySQL database.
    Specify your configuration settings in 'io_config.yaml'.

    Docs: https://docs.mage.ai/design/data-loading#mysql
    """
    config_path = path.join(get_repo_path(), 'io_config.yaml')
    config_profile = 'default'

    folder_path = '/home/src/data/'
    #Coleta o nome dos arquivos csv na pasta folder_path e ignora os que contem order, product ou geolocation no nome
    csv_files = [file for file in os.listdir(folder_path) if file.endswith('.csv') \
                and 'order' not in file.lower()\
                and 'product' not in file.lower()\
                and 'geolocation' not in file.lower()]

    for csv_file in csv_files:
    # Extrai o nome do arquivo que dara origem a tabela
        table_name = os.path.splitext(csv_file)[0]
        table_name = table_name.replace('olist_', '')
        table_name = table_name.replace('_dataset', '')

        # Le o csv
        file_path = os.path.join(folder_path, csv_file)
        data = pd.read_csv(file_path, low_memory=False, keep_default_na=False)
        

        #Carrega os dados (data) no lake com as configuração de replace e sem index
        with MySQL.with_config(ConfigFileLoader(config_path, config_profile)) as loader:
                loader.export(
                    data,
                    None,
                    table_name,
                    index=False,
                    if_exists='replace',  # Raise an error if the table name already exists
            )
```

Saída no log do mage.
![log](presets/loader_lake_done.png) \
### Etapa 3 - Transformação - Tasks de @transformer
Nessa task irei consumir os dados do lake criados na etapa anterior e através deles criar novas tabelas com modelagens analíticas (ainda no lake). Além disso, nas novas tabelas deixamos de lado a modelagem relacional e passamos a consolidar os dados em uma Wide Table analítica que facilita o consumo dos usuários. Hoje, com a evolução do armazenamento em nuvem, temos à nossa disposição uma performance significativamente melhor, bem como métodos de otimização que tornam viável o uso dessa modelagem wide.

Ao contrário das tasks anteriores, essa task é puramente em SQL, aqui vamos criar 4 novas tabelas. São elas:

- sellers_performance: tabela agregada e enriquecida do vendedor (seller_id) contendo as dimensões do vendedor e as métricas de pedidos, pedidos entregues, pedidos cancelados, número de itens distintos vendidos, ticket médio, quantidade de avaliações, média de avaliações, total vendidos em $, categoria mais vendida por ele.

- paid_orders: tabela enriquecida de pedidos considerando apenas os pedidos com pagamento confirmado e não cancelados, além disso contém informações do vendedor, comprador, frete e pagamento.

- order_items_detailed: tabela dos itens comprados (ordem_items) enriquecida com informações do produto, comprador, vendedor e frete. 
d
- customer_experience: tabela contendo o id do usuário, nota média das avaliações, quantidade de avaliações, data da última compra, número de compras e LTV (total comprado ao longo da vida).

Essas novas tabelas contém muitas das informações necessárias para analistas e pessoas de negócio realizarem as análises necessárias sem a necessidade de fazer inúmeros JOINs e correr o risco de trazer informações inválidas ou erradas. Os dados estão prontos para consumos de forma simples e clara.

Exemplo, tabela de sellers_performance:
```
CREATE TABLE IF NOT EXISTS sellers_performance AS (
    WITH seller_category_rank AS (
        SELECT
            seller_id,
            product_category_name,
            ROW_NUMBER() OVER (
                PARTITION BY seller_id
                ORDER BY COUNT(oi.order_id) DESC
            ) AS category_rank
        FROM order_items oi
        LEFT JOIN products p ON p.product_id = oi.product_id
        GROUP BY 1, 2
    )
    SELECT
        s.seller_id,
        s.seller_state,
        s.seller_city,
        COUNT(DISTINCT o.order_id) AS qty_orders,
        COUNT(DISTINCT CASE WHEN order_status = 'delivered' THEN o.order_id ELSE NULL END) AS delivered_orders,
        COUNT(DISTINCT CASE WHEN order_status LIKE '%cancel%' THEN o.order_id ELSE NULL END) AS canceled_orders,
        COUNT(DISTINCT product_id) AS qty_distinct_items_sold,
        AVG(price) AS avg_item_sold_price,
        COUNT(DISTINCT review_id) AS qty_reviews,
        AVG(review_score) AS avg_review_score,
        CASE WHEN category_rank = 1 AND product_category_name IS NOT NULL THEN product_category_name END AS most_sold_category,
        SUM(CASE WHEN o.order_status NOT LIKE '%cancel%' THEN oi.price END) AS seller_sold_amount
    FROM sellers s
    LEFT JOIN order_items oi ON oi.seller_id = s.seller_id
    LEFT JOIN orders o ON o.order_id = oi.order_id
    LEFT JOIN order_reviews r ON r.order_id = o.order_id
    LEFT JOIN seller_category_rank AS scr ON s.seller_id = scr.seller_id
    GROUP BY 1, 2, 3, most_sold_category
);
```

O script completo de transformação @transformer se encontram em `tasks_scripts/transfomers`

### Etapa 4 - Validação - Task validation @data_loader
Nessa etapa utilizo a biblioteca great_expectations para validar os dados antes de levamos para o data warehouse. Essa biblioteca permite validar os dados de acordo com algumas premissas que desejamos, por exemplo, a coluna seller_id na tabela seller_performance no nosso data lake não pode conter nenhum valor nulo.

Nesse exemplo, não faço uma validação tão detalhada como poderiamos ter a necessídade em um projeto de larga escala real.

No mage, temos o great_expectations de forma nativa, sem necessídade de importar ou instalar a biblioteca. Para utilização é necessário criar uma task e vincular a um powerup com great_expectations e neste powerup realizar a configuração da função que irá validar os dados. Dessa forma, nesse exemplo abaixo faço a validação da task que faz um `SELECT * FROM sellers_performance`. O great expectations espera 2 coisas: a coluna seller_id não deve conter valores nuloes e a coluna de avaliações deve conter um número mínimo de 0 e máximo de 5.
Se essas expectativas não forem atendidas, seremos alertados.

Task que carrega os dados para o great_expectations valiadar
```
@data_loader
def check_sellers(*args, **kwargs):
    """
    Retorna o resultado da query
    """
    query = 'SELECT * FROM sellers_performance'  

    config_path = path.join(get_repo_path(), 'io_config.yaml')
    config_profile = 'default'

    with MySQL.with_config(ConfigFileLoader(config_path, config_profile)) as loader:
        return loader.load(query)

```
Função de validação no great_expectations
```

@extension('great_expectations')
def validate(validator, *args, **kwargs):

    """
    validator: Great Expectations validator object
    
    Espera que a coluna seller_id não possua nenhum nulo - expect_column_values_to_not_be_null
    Espera que a coluna avg_review_score tenha o valor entre 0 e 5 - expect_column_max_to_be_between

    """
    validator.expect_column_values_to_not_be_null(
        column = 'seller_id'
    )
    validator.expect_column_max_to_be_between(
        min=0,
        max=5,
        column='avg_review_score'
    )
```
**Resultado da nossa validação neste exemplo**
```
MySQL initialized
├─ Opening connection to MySQL database...DONE
└─ Loading data with query
SELECT * FROM sellers_performance
...DONE
seller_id and review
Expectations from extension great_expecations for block validation succeeded.
Expectations from extension great_expecations for block validation succeeded.
```

### Etapa 5 - Agora vai! Carga das tabelas no Warehouse - lake_to_warehouse @custom
Nessa etapa, as tabelas novas tabelas e algumas outras que considerei relevante para o exemplo do proejto e estão no data lake serão enviadas ao warehouse. Para isso, criei uma função em Python que coleta os dados da coxeão no datalake e faz a carga no data warehouse. A função e a task são chamadas de lake_to_warehouse e no mage possuem um decorator @custom.
```
@custom
def lake_to_warehouse(*args, **kwargs):
    engine_lake = create_engine(f"mysql+mysqlconnector://{mysql_username}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}")
    engine_wh = create_engine(f"mysql+mysqlconnector://{mysql_username}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database_2}")


    insp = inspect(engine_lake)
    table_to_warehouse = ["order_items_detailed", "sellers_performance", "customers", "customer_experience", "order_reviews"]

    with engine_lake.connect() as conn, engine_wh.connect() as conn_wh:
        for table in table_to_warehouse:
            query = f"SELECT * FROM {table}"

            try:
                pd.DataFrame(conn.execute(text(query)).fetchall()).to_sql(table, con=engine_wh, if_exists='replace')
                print(f'{table} está pronta warehouse.')
            except: 
                print(f'{table} falhou.')
```


### Fim do ETL! Os dados estão no warehouse
Agora com os dados no warehouse vamos checar se as tabelas estão populadas. Outro ponto legal do mage é que podemos fazer pequenas análises dentro da própria UI com as funções de chart. Abaixo, fiz um `SELECT * FROM warehouse.sellers_performance` e uma vizualição em formato de tabela e um histograma do campo `canceled_order` dos vendedores. 

![resultado da query](presets/check_warehouse.png)

### Consumo no Jupyter 
Iniciando jupyter 
`docker run --network mage-app -p 8888:8888 -v ${PWD}:/home/jovyan/work jupyter/minimal-notebook`
Vendo alguns dados que foram enviados ao lake
![jupyter](presets/jupyter.png)

### Consumo no PowerBI
Fiz uma visualização extremamente simples para validar se os dados estavam chegando no conector do power bi, tudo certo!
![jupyter](presets/power-bi.png)



## Próximas etapas
Como próximas etapas desse projeto tenho duas coisas em mente:
- 1. Analisar os dados e produtizar um modelo simples de clusterização de clientes (ideia inicial) utilizando Python e fazendo o deploy no Mage.
- 2. Estruturar os dashboards no PowerBI (já fiz na primeira versão desse projeto, porém a modelagem está diferente e mais performáticas nessa nova versão)
- 3. Incluir alguma step de transformação com dbt 
- 4. O datalake e o warehouse ficarão na nuvem e disponíveis para consumo. Nesse caso, provavelmente vou optar pelo Azure ou GCP (estou estudando como fazer isso sem estourar o cartão 💸💸💸)

Tem alguma sugestão? Manda pra mim! 










