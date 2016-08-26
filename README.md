[![Build Status](https://travis-ci.org/analytics-ufcg/sab-api.svg?branch=master)](https://travis-ci.org/analytics-ufcg/sab-api)

# Monitoramento dos reservatórios da região Semi-árida brasileira

Contém o acesso aos dados do monitoramento em uma API.

## Desenvolvimento

Para instalar as dependencias necessárias só é necessário executar o comando abaixo na pasta do projeto:

```
pip install -r requirements.txt
```

Também é necessário o arquivo de configuração do banco de dados que deve ser criado em `~/.my.cnf`. O conteúdo do arquivo é o seguinte:

```
[INSA]
user=usuarioDoBD
password=SenhaDoUsuario
host=db-insa
database=INSA
```
