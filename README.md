[![Build Status](https://travis-ci.org/analytics-ufcg/sab-api.svg?branch=master)](https://travis-ci.org/analytics-ufcg/sab-api)

# Monitoramento dos reservatórios da região Semi-árida brasileira

Contém o acesso aos dados do monitoramento em uma API.

## Desenvolvimento
Previamente a instalação do projeto é necessária a instalação do libmysql:

```
sudo apt-get install libmysqlclient-dev
sudo apt-get install python-numpy

```

Para instalar as dependencias necessárias é necessário executar o comando abaixo na pasta do projeto:


```
pip install -r requirements.txt
```

Também é necessário o arquivo de configuração do banco de dados que deve ser criado em `~/.my.cnf`. O conteúdo do arquivo é o seguinte:

```
[INSA]
user=usuarioDoBD
password=SenhaDoUsuario
host=hostDoUsuario
```


Para criar o Banco de dados e populá-lo inicialmente com os dados previamente baixados é necessário:

- executar na pasta script:
```
python inicial_script_DB.py
```

Caso queira colocar uma rotina no Ubuntu para todo dia atualizar o banco de dados as 3 da manhã:
```
crontab -e
0 3 * * *   /usr/bin/python /home/ubuntu/sab-api/script/atualizacao_diaria.py

```

Para executar a api na pasta raiz executar:

```
python run.py [--debug]

```

### Importação de dados

Para atualização do desenho do semiárido e geolocalização dos reservatórios, veja o
guia de [importação de dados](https://github.com/analytics-ufcg/sab-api/tree/master/data).
