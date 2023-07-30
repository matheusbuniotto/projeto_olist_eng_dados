# Projeto ELTL Olist sem orquestração (v1)

### ETLT
Etapas:
1. Criação da Imagem Docker com um banco de dados MySQL e Python
2. Download (Extract) dos arquivos CSV da base de dados olist usando script bash
3. Envio (Load) dos arquivos CSV para o banco de dados utilizando script python em conexão com o MySQL (criação do datalake)
4. Transformação (Transform) das tabela no datalake para solução de problemas de négocio, gerando novas tabelas mais informativas e agregadas (Wide Fact Table)
5. Criação (Load) das novas tabela no data warehouse para consulta

